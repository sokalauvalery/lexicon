from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

NEW, LEARN, KNOWN, IGNORE = 0, 1, 2, 3
WORD_STATUSES = ((NEW, 'new'),
                 (LEARN, 'learn'),
                 (KNOWN, 'known'),
                 (IGNORE, 'ignore'))


class TextFile(models.Model):
    #type = models.ForeignKey(Source)
    user = models.ForeignKey(User)
    title = models.CharField(max_length=200)
    file = models.FileField()
    upload_date = models.DateTimeField('upload date')
    new_words_count = models.IntegerField(default=0)
    total_words_count = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.id:
            self.upload_date = timezone.now()
        return super(TextFile, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class Word(models.Model):
    user = models.ForeignKey(User)
    word = models.CharField(max_length=200)
    explore_date = models.DateTimeField('explore date')
    status = models.IntegerField(choices=WORD_STATUSES, default=NEW)
    source = models.ManyToManyField(TextFile)

    def __str__(self):
        return self.word

    def save(self, *args, **kwargs):
        if not self.id:
            self.explore_date = timezone.now()
        return super(Word, self).save(*args, **kwargs)


class Dictionary(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()


class Meaning(models.Model):
    word = models.ForeignKey(Word, primary_key=True, on_delete=models.CASCADE)
    #dictionary = models.ForeignKey(Dictionary)
    meaning = models.TextField(max_length=10000)

    def __str__(self):
        return self.meaning


class Source(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Usage(models.Model):
    word = models.ForeignKey(Word)
    source = models.ForeignKey(Source)
    usage = models.TextField()



class Job(models.Model):
    """Class describing a computational job"""

    # currently, available types of job are:
    TYPES = (
        ('fibonacci', 'fibonacci'),
        ('power', 'power'),
    )

    # list of statuses that job can have
    STATUSES = (
        ('pending', 'pending'),
        ('started', 'started'),
        ('finished', 'finished'),
        ('failed', 'failed'),
    )

    type = models.CharField(choices=TYPES, max_length=20)
    status = models.CharField(choices=STATUSES, max_length=20)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    argument = models.PositiveIntegerField()
    result = models.IntegerField(null=True)

    def save(self, *args, **kwargs):
        """Save model and if job is in pending state, schedule it"""
        super(Job, self).save(*args, **kwargs)
        if self.status == 'pending':
            from .tasks import TASK_MAPPING
            task = TASK_MAPPING[self.type]
            task.delay(job_id=self.id, n=self.argument)