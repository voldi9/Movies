from django.conf.urls import url

from . import views

urlpatterns = [
    #url(r'^$', views.index, name='index'),
    url(r'^topGenre/$', views.top_genre, name='top_genre'),
]