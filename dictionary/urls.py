from django.conf.urls import url, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
# register job endpoint in the router
router.register(r'jobs', views.JobViewSet)

app_name = 'dictionary'
urlpatterns = [
    url(r'^$', views.index),
    url(r'^upload_file/$', views.upload_file, name='upload_file'),
    url(r'^sources/$', views.source_types, name='sources'),
    url(r'^new_words/(?P<job_id>.*)/$', views.new_words, name='new_words'),
    url(r'^poll_state$', views.poll_state, name='poll_state'),
    url(r'^router/', include(router.get_urls())),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))

]