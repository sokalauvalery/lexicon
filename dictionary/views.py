from django.shortcuts import render
from .models import Word, Source, TextFile, Meaning, NEW, KNOWN, SubUsage, LEARN
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
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from rest_framework import mixins, viewsets


@login_required()
def index(request):
    last_words = Word.objects.filter(status=1).filter(user=request.user).order_by('-explore_date')[:30]
    total = Word.objects.filter(user=request.user).count()
    new = Word.objects.filter(status=NEW).filter(user=request.user).count()
    definition = {}
    for word in last_words:
        meaning = Meaning.objects.filter(word=word.id)
        definition[word] = json.loads(str(meaning[0])) if meaning else None
    return render(request, 'dictionary/index.html', context={'words': definition,
                                                             'total': total,
                                                             'new': new,
                                                             'last_learned': last_words,
                                                             'username': request.user})


@login_required()
def explore_new_words(request, source_title=None):
    new_words = Word.objects.filter(status=NEW).filter(user=request.user) if not source_title else Word.objects.filter(status=NEW).filter(user=request.user).filter(source__title=source_title)
    return render(request, 'dictionary/word_explorer.html', context={'new_words': [str(word) for word in new_words]})


@csrf_exempt
def get_definition(request):
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
def get_usage(request):
    if request.is_ajax():
        if 'word' in request.POST.keys() and request.POST['word']:
            word = Word.objects.get(word=request.POST['word'])
            usages = SubUsage.objects.filter(word=word)
            data = {}
            for usage in usages:
                if usage.source.title not in data:
                    data[usage.source.title] = [usage.usage]
                else:
                    data[usage.source.title].append(usage.usage)
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
    if request.is_ajax():
        # for field in expected_fields:
            # if field not in request.POST.keys() or request.POST[field] is None:
            #     print('Cannot save word. Missing requared data. Post body: ' + str(request.POST))
            #     has_all_data =False
        # if has_all_data:
        word = Word.objects.get(word=request.POST['word'])
        word.status = request.POST['status']
        word.save()
        # if request.POST['status'] == 'learn':
        #     meaning = Meaning(word=request.POST['word'], meaning=request.POST['meaning'])
        #     meaning.save()
    else:
        data = 'This is not an ajax request'
    return HttpResponse({'Status': 'Ok'}, content_type='application/json')


@login_required()
def source_types(request):
    data = []
    last_uploaded_sources = TextFile.objects.filter(user=request.user).order_by('-upload_date')[:30]
    for source in last_uploaded_sources:
        unprocessed = Word.objects.filter(status=NEW).filter(user=request.user).filter(source__title=source.title).count()
        to_learn = Word.objects.filter(status=LEARN).filter(user=request.user).filter(source__title=source.title).count()
        data.append((source, unprocessed, to_learn))
    return render(request, 'dictionary/source_list.html', context={'sources': data})


@login_required()
def source_words(request, title, status_filter=-1):
    source = TextFile.objects.get(title=title)
    words = Word.objects.filter(source=source).filter(user=request.user)
    return render(request, 'dictionary/source.html', context={'words': enumerate(words),
                                                              'source': source,
                                                              'word_status_filter': status_filter})


@login_required()
@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            #source_type = [source for source in source_types_all if str(source.id) == request.POST['source']]
            #if not source_type:
            #    raise Exception('Invalid source type ' + request.POST['source'])
            #instance = TextFile(type=source_type[0], title=request.POST['title'], file=request.FILES['file'])
            if request.POST['title']:
                pass
            text_file = TextFile(title=request.POST['title'], file=request.FILES['file'], user=request.user)
            text_file.save()
            #job_id = get_file_words.delay(instance.id)
            known_words = [x.word for x in Word.objects.filter(user=request.user)]
            with open(text_file.file.path) as f:
                sub_parser = parser.SrtSubParser(f)
                words = sub_parser.get_words()
            unknown_words = [Word(word=word, user=request.user, explore_date=timezone.now()) for word in words if word not in known_words]
            Word.objects.bulk_create(unknown_words)
            for new_word in unknown_words:
                new_word.source.add(text_file)
            text_file.new_words_count = len(unknown_words)
            text_file.total_words_count = len(words)
            text_file.save()
            # Save usages
            usages_to_save = []
            for word in unknown_words:
                for usage in words[word.word]:
                    usages_to_save.append(SubUsage(word=word,
                                                   source=text_file,
                                                   usage=usage.line,
                                                   begin_time=usage.begin_time,
                                                   end_time=usage.end_time,
                                                   block_id=usage.block_id
                    ))
            SubUsage.objects.bulk_create(usages_to_save)
            return render(request, 'dictionary/upload_statistics.html', context={'words': unknown_words})
    else:
        form = UploadFileForm()
    return render(request, 'dictionary/upload.html', {'form': form}) #, 'sources': source_types_all})


@login_required()
def new_words(request, job_id):
    return render(request, 'dictionary/new_words.html', {'task_id': job_id})


@csrf_exempt
def poll_state(request):
    """ A view to report the progress to the user """
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


class JobViewSet(mixins.CreateModelMixin,
                 mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """
    API endpoint that allows jobs to be viewed or created.
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer