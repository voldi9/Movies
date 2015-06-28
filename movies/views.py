# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.db import connections
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
import omdb


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
    fetched_movies = dictfetchall(cursor)

    #deleting the original_titles that match titles
    #since we don't want to output same title twice
    #also we enumarete the movies by their ranking

    for i in range(0, len(fetched_movies)):
        if fetched_movies[i]['title'] == fetched_movies[i]['original_title']:
            fetched_movies[i]['original_title'] = ''
        fetched_movies[i]['ranking'] = i

    template = loader.get_template('movies/index.html')

    context = RequestContext(request, {
        'top_movies_list': fetched_movies,
    })
    return HttpResponse(template.render(context))

def top_genre(request):
    connection = connections['default']
    cursor = connection.cursor()
    cursor.execute('SELECT genre.name, COUNT(*) FROM movie_genre '
                   'INNER JOIN genre ON (genre.id = movie_genre.genre_id) '
                   'GROUP BY genre.name ORDER BY COUNT(*) DESC;')
    genres = dictfetchall(cursor)

    template = loader.get_template('movies/top_genre.html')
    context = RequestContext(request, {

        'top_genres_list': genres,
    })
    return HttpResponse(template.render(context))

def search(request):
    connection = connections['default']
    cursor = connection.cursor()
    cursor.execute('SELECT name, id FROM genre '
                   'ORDER BY name ASC;')
    genres = dictfetchall(cursor)

    template = loader.get_template('movies/search.html')

    searching_genres = ()
    movies = {}
    minrank = 0

    if(request.method == 'POST'):
        for element in request.POST:
            if element != 'minrank' and element != 'csrfmiddlewaretoken':
                searching_genres = searching_genres + (element,)
        if request.POST['minrank'] != '':
            minrank = request.POST['minrank']
        query_str = 'SELECT DISTINCT m.id, m.title, m.original_title, m.vote_average FROM ' \
                    '(SELECT id, title, original_title, vote_average FROM movie WHERE vote_average >= '
        query_str += str(minrank)
        query_str += ') m INNER JOIN (SELECT movie_id FROM movie_genre WHERE '
        for genre in searching_genres:
            query_str += 'genre_id = ' + genre + ' OR '

        query_str = query_str[:-4] + ') mg ON (mg.movie_id = m.id) ORDER BY m.vote_average DESC;'
        if searching_genres: #only if genre set is not empty are we searching for movies
            cursor.execute(query_str)
        movies = dictfetchall(cursor)
        for i in range(0, len(movies)):
            if movies[i]['title'] == movies[i]['original_title']:
                movies[i]['original_title'] = ''
            movies[i]['ranking'] = i

    for genre in genres:
        if str(genre['id']) in searching_genres:
            genre['on'] = True

    data_dict = {
        'genres_list': genres,
        'movies_list': movies,
        'NUM_RES': len(movies),
        'minrank': minrank,
    }

    context = RequestContext(request, data_dict)

    return HttpResponse(template.render(context))

def movies(request, movie_id):
    connection = connections['default']
    cursor = connection.cursor()
    cursor.execute('SELECT id, title, original_title, vote_average FROM '
                'movie WHERE id = (%s);', (movie_id,))

    movie_data = dictfetchall(cursor)[0]

    cursor.execute('SELECT DISTINCT g.name FROM '
                   '(((SELECT * FROM movie WHERE id = (%s)) m '
                   'INNER JOIN movie_genre mg ON (mg.movie_id = m.id)) '
                   'INNER JOIN genre g ON (g.id = mg.genre_id));', (movie_id,))

    template = loader.get_template('movies/movie.html')

    genres = ''

    for genre in dictfetchall(cursor):
        genres += genre['name'] + ', '

    genres = genres[:-2]

    context = RequestContext(request, {
        'genres': genres,
        'movie': movie_data,
        'plot': omdb.get(title = movie_data['title'], fullplot = True)['plot'],
    })
    return HttpResponse(template.render(context))