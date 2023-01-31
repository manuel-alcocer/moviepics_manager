from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse

from filesystem.models import MoviesDirectory, VideoFile
from filesystem.models import Search
from tmdb.models import Movie

from filesystem.tasks import scan_directory_task
from filesystem.tasks import filename_search_task
from filesystem.tasks import run_search_task
from filesystem.tasks import create_picture_on_disk_task

from django import forms
from django.db import models

@admin.action(description='Scan directory')
def scan_directory(modeladmin, request, queryset):
    for directory in queryset:
        scan_directory_task.delay(directory.pk)

@admin.action(description='Search on TMDB')
def search_on_tmdb(modeladmin, request, queryset):
    for filename in queryset:
        filename_search_task.delay(filename.pk)

@admin.action(description='Create picture on disk')
def create_picture(modeladmin, request, queryset):
    for video_file in queryset:
        create_picture_on_disk_task.delay(video_file.pk)

@admin.register(MoviesDirectory)
class DirectoryAdmin(admin.ModelAdmin):
    actions = [scan_directory]

@admin.register(VideoFile)
class FileAdmin(admin.ModelAdmin):
    list_display = ('name', 'search_link' ,'image_preview','directory', 'extension', 'realpath')
    actions = [search_on_tmdb, create_picture]
    ordering = ('name',)

    def search_link(self, obj):
        search = Search.objects.filter(file=obj)
        if search.exists():
            search = search.first()
            url = reverse('admin:filesystem_search_change', args=[search.pk])
            return mark_safe(f'<a href="{url}">{search.movie_selected}</a>')

    def asociated_movie(self, obj):
        search = Search.objects.filter(file=obj)
        if search.exists():
            return search.first().movie_selected
        return None

    def image_preview(self, obj):
        if not self.asociated_movie(obj):
            return ''
        poster_url = self.asociated_movie(obj).get_poster_url()
        if poster_url:
            return mark_safe(f'<img src="{poster_url}" height="100"/>')
    image_preview.short_description = 'Preview'

@admin.action(description='Run selected searches on TMDB')
def run_selected_searches(modeladmin, request, queryset):
    for search in queryset:
        run_search_task.delay(search.id)

@admin.register(Search)
class SearchAdmin(admin.ModelAdmin):
    list_display = ('name', 'movie_selected', 'file_link' ,'movie_count', 'last_search')
    search_fields = ('name',)
    exclude = ('result',)
    actions = [run_selected_searches]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        print(form)
        return form

    def file_link(self, obj):
        if obj.file:
            url = reverse('admin:filesystem_videofile_change', args=[obj.file.pk])
            return mark_safe(f'<a href="{url}">{obj.file}</a>')
    file_link.short_description = 'File'

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj:
            if obj.file:
                readonly_fields += ('file',)
            if obj.movies:
                readonly_fields += ('movies',)
        return readonly_fields

    def movie_count(self, obj):
        return len(obj.movie_id_list())

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'movie_selected':
            kwargs['queryset'] = Movie.objects.none()
            if 'object_id' in request.resolver_match.kwargs:
                current_search = self.get_object(request, request.resolver_match.kwargs['object_id'])
                if current_search.result_count() > 0:
                    movie_id_list = current_search.movie_id_list()
                    kwargs['queryset'] = Movie.objects.filter(tmdb_id__in=movie_id_list).order_by('title')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
