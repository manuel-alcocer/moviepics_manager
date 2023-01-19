from django.utils import timezone
from datetime import timedelta

from project.celery import app

from filesystem.models import VideoFile, MoviesDirectory, Search
from tmdb.models import Movie, Image, Setting

from os import listdir
from os.path import isfile, join, exists
from os.path import realpath, basename
from pathlib import Path

import mimetypes

from tmdbv3api import TMDb, Movie as TmdbMovie
from urllib import request
from os.path import basename

from os.path import join
from shutil import copyfile

def has_to_store_file(file):
    mimetypes.add_type('video/divx', '.divx')
    mimetypes.add_type('video/iso', '.iso')
    mime_type, _ = mimetypes.guess_type(file)
    if mime_type and mime_type.startswith('video'):
        return True
    return False

def create_search(filename_pk):
    file = VideoFile.objects.get(pk=filename_pk)
    search = Search.objects.filter(file=file)
    if search.exists():
        print('Search already exists for file: ' + file.name)
        search = search.first()
    else:
        print('Creating search for: ' + file.name)
        search = Search(name=file.name, file=file)
        search.save()
    return search.pk

def create_association(filename_pk):
    video_file = VideoFile.objects.get(pk=filename_pk)
    search = Search.objects.get(file=video_file)
    title = 'No title found'
    if search.movie_selected:
        if search.movie_selected.title:
            title = search.movie_selected.title
        print('Movie already associated: ' + search.movie_selected.title + ' with file: ' + video_file.name)
    else:
        print('Cannot associate movie to file: ' + video_file.name)
        search.movie_selected = search.get_first_movie()
        search.save()

def search_on_tmdb(movie_name):
    tmdb = TMDb()
    tmdb.api_key = Setting.objects.get(option__name='api_key').value
    tmdb.language = Setting.objects.get(option__name='language').value
    tmdb.debug = True
    movie = TmdbMovie()
    return [ m.__dict__ for m in movie.search(movie_name) ]

def update_result(search):
    max_search_cache = Setting.objects.get(option__name='max_search_cache').value

    if search.result_count() > 0 and search.last_search > (timezone.now() - timedelta(days=int(max_search_cache))):
        print('Search cache hit: ' + search.name)
    else:
        search.result = { "data" : search_on_tmdb(search.name) }
    search.save()

def add_to_movies(movie):
    if not Movie.objects.filter(tmdb_id=movie['id']).exists():
        m = Movie.objects.create(tmdb_id=movie['id'], title=movie['title'], data=movie)
    else:
        m = Movie.objects.get(tmdb_id=movie['id'])
        if 'title' in movie:
            m.title = movie['title']
        else:
            m.title = 'No title found'
        m.data = movie
        m.save()
    return m

def update_movies(search):
    movie_list = []
    for movie in search.result['data']:
        new_movie = add_to_movies(movie)
        if not new_movie in search.movies.all():
            search.movies.add(new_movie)
        movie_list.append(new_movie)
        if not search.movie_selected:
            search.movie_selected = new_movie
    search.save()
    return movie_list

def update_posters(movie_list):
    for movie in movie_list:
        if not 'poster_path' in movie.data:
            continue
        if movie.data['poster_path']:
            poster_filename = basename(movie.data['poster_path'])
            if not Image.objects.filter(name=poster_filename).exists():
                movie.image = Image.objects.create(name=poster_filename)
                movie.image.title = movie.title
            else:
                movie.image = Image.objects.get(name=poster_filename)
            if not movie.image.image_file:
                try:
                    print('Downloading poster: ' + poster_filename)
                    movie.image.image_file.save(poster_filename, request.urlopen('https://image.tmdb.org/t/p/w500/' + poster_filename, timeout=10))
                except Exception as e:
                    print('Error downloading poster: ' + poster_filename)
                    movie.download_correct = False
                    movie.download_error_message = str(e)
            movie.save()


def run_search(search_pk):
    search = Search.objects.get(pk=search_pk)
    update_result(search)
    movie_list = update_movies(search)
    update_posters(movie_list)
    return search.pk

def create_picture_on_disk(file_pk):
    file = VideoFile.objects.get(pk=file_pk)
    search = Search.objects.filter(file=file)
    if not search.exists():
        return
    search = search.first()
    if not search.movie_selected:
        return
    if not search.movie_selected.get_poster_url():
        return
    src_file = search.movie_selected.image.image_file
    filename = f'{file.name}.jpg'
    filepath = join(file.directory.name, filename)
    print(filepath)
    copyfile(src_file.path, filepath)
    print(f'Picture created: {filepath}')

@app.task()
def create_picture_on_disk_task(filename_pk):
    file = VideoFile.objects.get(pk=filename_pk)
    create_picture_on_disk(file.pk)

@app.task()
def create_search_task(filename_pk):
    create_search(filename_pk)

@app.task()
def create_association_task(filename_pk):
    create_association(filename_pk)

@app.task
def scan_directory_task(directory_pk):
    directory = MoviesDirectory.objects.get(pk=directory_pk)

    if not exists(directory.name):
        return 'Directory not exists: ' + directory.name

    count = 0
    for filename in listdir(directory.name):
        file = join(directory.name, filename)
        file_full_path = realpath(file)
        if isfile(file):
            count += 1
            if not has_to_store_file(file):
                print('Not storing file: ' + file)
                continue
            if VideoFile.objects.filter(realpath=file_full_path).exists():
                print('File already exists in db: ' + filename)
            else:
                new_file = VideoFile.objects.create(directory=directory, name=file)
                new_file.directory = directory
                new_file.realpath = file_full_path
                new_file.extension = Path(file).suffix
                new_file.name = basename(file)[:-len(new_file.extension)]
                new_file.save()

    return f'Scanned {count} files in directory: {directory.name}'

@app.task()
def run_search_task(search_pk):
    return run_search(search_pk)

@app.task()
def filename_search_task(filename_pk):
    search_pk = create_search(filename_pk)
    run_search(search_pk)
    create_association_task(filename_pk)
