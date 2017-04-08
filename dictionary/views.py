from django.shortcuts import render
from .models import Word, Source, TextFile, Meaning, NEW, KNOWN
from .forms import UploadFileForm
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.db.models import Count
from .models import Job
from .serializers import JobSerializer
from .tasks import get_file_words
from django.views.decorators.csrf import csrf_exempt
from celery.result import AsyncResult
from lexicon.celeryconf import app
from django.http import HttpResponse
import json
from translator import parser
from django.utils import timezone

#bulk_create


def index(request):
    last_words = Word.objects.filter(status=1).order_by('-explore_date')[:30]
    total = Word.objects.count()
    new = Word.objects.filter(status=NEW).count()
    definition = {}
    for word in last_words:
        meaning = Meaning.objects.filter(word=word.id)
        definition[word] = json.loads(str(meaning[0])) if meaning else None
    return render(request, 'dictionary/index.html', context={'words': definition,
                                                             'total': total,
                                                             'new': new,
                                                             'last_learned': last_words})


def explore_new_words(request, source_id=None):
    new_words = Word.objects.filter(status=NEW) if not source_id else Word.objects.filter(status=NEW, source=source_id)
    #word = words[0]
    #meaning = parser.get_word_definithins(word)
    return render(request, 'dictionary/word_explorer.html', context={'new_words': [str(word) for word in new_words]})


@csrf_exempt
def get_definition(request):
    data = 'Fail'
    if request.is_ajax():
        if 'word' in request.POST.keys() and request.POST['word']:
            data = parser.get_word_definition(request.POST['word'])
        else:
            data = 'No word in the request'
    else:
        data = 'This is not an ajax request'
    json_data = json.dumps(data)
    print(json_data)
    return HttpResponse(json_data, content_type='application/json')


@csrf_exempt
def save_word(request):
    expected_fields = ['word', 'meaning', 'status']
    has_all_data = True
    print(request.POST.keys())
    print('Save word!')
    if request.is_ajax():
        for field in expected_fields:
            if field not in request.POST.keys() or request.POST[field] is None:
                print('Cannot save word. Missing requared data. Post body: ' + str(request.POST))
                has_all_data =False
        if has_all_data:
            word = Word.objects.get(word=request.POST['word'])
            word.status = request.POST['status']
            word.save()
            if request.POST['status'] == 'learn':
                meaning = Meaning(word=request.POST['word'], meaning=request.POST['meaning'])
                meaning.save()
    else:
        data = 'This is not an ajax request'
    return HttpResponse({'Status': 'Ok'}, content_type='application/json')


def source_types(request):
    last_uploaded_sources = Source.objects.annotate(Count('textfile'))
    return render(request, 'dictionary/source_list.html', context={'sources': last_uploaded_sources})


@csrf_exempt
def upload_file(request):
    #source_types_all = Source.objects.all()
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            #source_type = [source for source in source_types_all if str(source.id) == request.POST['source']]
            #if not source_type:
            #    raise Exception('Invalid source type ' + request.POST['source'])
            #instance = TextFile(type=source_type[0], title=request.POST['title'], file=request.FILES['file'])
            text_file = TextFile(title=request.POST['title'], file=request.FILES['file'])
            text_file.save()
            #job_id = get_file_words.delay(instance.id)
            known_words = [x.word for x in Word.objects.all()]
            words = set(parser.get_words([str(line) for line in text_file.file]))
            print(words)
            unknown_words = [Word(word=word, explore_date=timezone.now()) for word in words if word not in known_words]
            Word.objects.bulk_create(unknown_words)
            return render(request, 'dictionary/upload_statistics.html', context={'words': unknown_words})
#            return HttpResponseRedirect(reverse('dictionary:upload_statistics', args=(job_id,)))
#            return HttpResponseRedirect(reverse('dictionary:new_words', args=(job_id,)))
    else:
        form = UploadFileForm()
    return render(request, 'dictionary/upload.html', {'form': form}) #, 'sources': source_types_all})


def new_words(request, job_id):
    return render(request, 'dictionary/new_words.html', {'task_id': job_id})


@csrf_exempt
def poll_state(request):
    print("DEBUG")
    """ A view to report the progress to the user """
    data = 'Fail'
    if request.is_ajax():
        print("Is ajax")
        if 'task_id' in request.POST.keys() and request.POST['task_id']:
            task_id = request.POST['task_id']
            task = app.AsyncResult(task_id)

            print(task)
            data = task.result or task.state
        else:
            data = 'No task_id in the request'
    else:
        data = 'This is not an ajax request'

    json_data = json.dumps(data)
    print(json_data)
    return HttpResponse(json_data, content_type='application/json')

from rest_framework import mixins, viewsets


class JobViewSet(mixins.CreateModelMixin,
                 mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """
    API endpoint that allows jobs to be viewed or created.
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer