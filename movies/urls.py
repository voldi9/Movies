from django.conf.urls import url

from views import movies

urlpatterns = [
    url(r'^(?P<movie_id>[0-9]+)/$', movies, name='movies'),
]