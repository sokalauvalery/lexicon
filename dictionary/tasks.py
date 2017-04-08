from celery import shared_task, current_task
from numpy import random
from .models import TextFile, Word, Meaning
from translator import parser
import json


from functools import wraps

from lexicon.celeryconf import app
#from .models import Job

# decorator to avoid code duplication

# def update_job(fn):
#     """Decorator that will update Job with result of the function"""
#
#     # wraps will make the name and docstring of fn available for introspection
#     @wraps(fn)
#     def wrapper(job_id, *args, **kwargs):
#         job = Job.objects.get(id=job_id)
#         job.status = 'started'
#         job.save()
#         try:
#             # execute the function fn
#             result = fn(*args, **kwargs)
#             job.result = result
#             job.status = 'finished'
#             job.save()
#         except:
#             job.result = None
#             job.status = 'failed'
#             job.save()
#     return wrapper


# two simple numerical tasks that can be computationally intensive
#
# @app.task
# @update_job
# def power(n):
#     """Return 2 to the n'th power"""
#     return 2 ** n
#
#
# @app.task
# @update_job
# def fib(n):
#     """Return the n'th Fibonacci number.
#     """
#     if n < 0:
#         raise ValueError("Fibonacci numbers are only defined for n >= 0.")
#     return _fib(n)
#
#
# def _fib(n):
#     if n == 0 or n == 1:
#         return n
#     else:
#         return _fib(n - 1) + _fib(n - 2)

# mapping from names to tasks

TASK_MAPPING = {
    # 'power': power,
    # 'fibonacci': fib
}


class SourceStat:
    def __init__(self):
        self.total = None
        self.new = None

class Parser:
    def __init__(self, source):
        self.source = source
        self.total


@app.task
def get_file_words(file_id):
    file = TextFile.objects.filter(id=file_id)[0]
    known_words = [x.word for x in Word.objects.all()]
    # words = []
    # for line in file.file:
    #     words.extend(parser.get_words(str(line)))
    words = set(parser.get_words([str(line) for line in file.file]))
    print(words)
    new_words = [word for word in words if word not in known_words]
    print(new_words)

    defined_words = []
    for word in parser.get_words_definition(new_words, lang='rus'):
        print('GOT NEW WORD {}'.format(word))
        strword, meaning = word
        print(meaning)
        if meaning:
            newword = Word(word=strword)
            meaning = json.dumps(meaning)
            newword.save()
            word_meaning = Meaning(word=newword, meaning=meaning)
            word_meaning.save()
        defined_words.append(word)
        process_percent = int(100 * (1 - (len(new_words) - len(defined_words)) / float(len(new_words))))
        # print('DEBUG')
        # print(word)
        # print(process_percent)

        app.current_task.update_state(state='PROGRESS', meta={'process_percent': process_percent})
    return new_words

    # for i in range(0, 100, 5):
    #     #x = random.normal(0, 0.1, 2000)
    #     # if(i%30 == 0):
    #     #process_percent = int(100 * float(i) / float(5))
    #     print(i)
    #     import time; time.sleep(10)
    #     app.current_task.update_state(state='PROGRESS', meta={'process_percent': i})
