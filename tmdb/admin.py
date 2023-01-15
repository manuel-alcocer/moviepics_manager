from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Image, Movie
from .models import Setting, SettingOption

from filesystem.models import Search

@admin.register(SettingOption)
class SettingOptionAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ('option', 'value')

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'name','image_preview')
    search_fields = ('title','name')
    ordering = ('title',)

    def image_preview(self, obj):
        if obj.has_image_file():
            return mark_safe(f'<img src="{obj.image_file.url}" height="150"')
        return None
    image_preview.short_description = 'poster'

class MovieDownloadCorrectLookup(admin.SimpleListFilter):
    title = 'download correct'
    parameter_name = 'download_correct'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(download_correct=True)
        if self.value() == 'no':
            return queryset.filter(download_correct=False)

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('tmdb_id','title', 'year',
                    'has_poster','image_preview',
                    'download_correct', 'overview', 'download_error_message')
    search_fields = ('title',)
    ordering = ('title',)

    def image_preview(self, obj):
        if obj.image is not None:
            if obj.image.image_file:
                return mark_safe(f'<img src="{obj.image.image_file.url}" height="150"')
        return ''
    image_preview.short_description = 'poster preview'

    def overview(self, obj):
        if obj.data is not None and 'overview' in obj.data:
            return obj.data['overview']
        return 'No overview'
    overview.short_description = 'overview'

    def has_poster(self, obj):
        icon = 'icon-no'
        alt = 'False'
        if 'poster_path' in obj.data and obj.data['poster_path'] is not None:
            icon = 'icon-yes'
            alt = 'True'
        return mark_safe(f'<img src="/static/admin/img/{icon}.svg" alt="{alt}">')
    has_poster.short_description = 'poster available'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'image':
            if 'object_id' in request.resolver_match.kwargs:
                current_object = self.get_object(request, request.resolver_match.kwargs['object_id'])
                searches = Search.objects.filter(movies=current_object)
                movies = Movie.objects.filter(search_movies__in=searches)
                images = Image.objects.filter(movie_poster_selected__in=movies)
                kwargs['queryset'] = images
            else:
                kwargs['queryset'] = Image.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
