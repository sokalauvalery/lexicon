from django.shortcuts import render
from .models import Word, Source, TextFile, Meaning
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


def index(request):
    last_words = Word.objects.order_by('-explore_date')[:30]
    definition = {}
    for word in last_words:
        meaning = Meaning.objects.filter(word=word.id)
        definition[word] = meaning[0] if meaning else None
    return render(request, 'dictionary/index.html', context={'words': definition})


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
            instance = TextFile(title=request.POST['title'], file=request.FILES['file'])
            instance.save()
            job_id = get_file_words.delay(instance.id)
            return HttpResponseRedirect(reverse('dictionary:new_words', args=(job_id,)))
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