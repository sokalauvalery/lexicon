from django.conf.urls import url, include
from . import views
from rest_framework import routers
from django.conf.urls.static import static



router = routers.DefaultRouter()
# register job endpoint in the router
router.register(r'jobs', views.JobViewSet)

app_name = 'dictionary'
urlpatterns = [
    url(r'^$', views.index, name='home'),
    url(r'^upload_file/$', views.upload_file, name='upload_file'),
    url(r'^explore_words/(?P<source_title>.*)/$', views.explore_new_words, name='explore_words'),
    url(r'^explore_words/$', views.explore_new_words, name='explore_words'),
    url(r'^sources/$', views.source_types, name='sources'),
    url(r'^new_words/(?P<job_id>.*)/$', views.new_words, name='new_words'),
    url(r'^poll_state$', views.poll_state, name='poll_state'),
    url(r'^router/', include(router.get_urls())),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^get_definition/', views.get_definition, name='get_definition'),
    url(r'^get_usage/', views.get_usage, name='get_usage'),
    url(r'^save_word/', views.save_word, name='save_word'),
    # TODO: now here using source title instead of id. fix it
    url(r'^source_words/(?P<title>.*)/(?P<status_filter>.*)/$', views.source_words, name='source_words'),
    url(r'^source_words/(?P<title>.*)/$', views.source_words, name='source_words'),

]