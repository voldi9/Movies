# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.db import connections
from django.http import HttpResponse
from django.template import RequestContext, loader

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

def index(request):
    connection = connections['default']
    cursor = connection.cursor()
    cursor.execute('SELECT id, title, original_title, vote_average FROM movie '
                   'ORDER BY vote_average DESC, release_date ASC LIMIT 20;')
    template = loader.get_template('movies/index.html')
    fetched_movies = dictfetchall(cursor)

    #deleting the original_titles that match titles
    #since we don't want to output same title twice
    #also we enumarete the movies by their ranking
    i = 1
    for movie in fetched_movies:
        if movie['title'] == movie['original_title']:
            movie['original_title'] = ''
        movie['ranking'] = i
        i += 1

    context = RequestContext(request, {
        'top_movies_list': fetched_movies,
    })
    return HttpResponse(template.render(context))