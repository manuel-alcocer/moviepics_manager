from django.shortcuts import render

from django.views.generic import ListView

from filesystem.models import VideoFile
# Create your views here.

from os.path import basename

def movie_pools(request):
    return render(request, 'movie_pools.html')

class FilesView(ListView):
    model = VideoFile
    template_name = 'videofiles.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for file in context['object_list']:
            file.image_preview = file.get_movie()
            file.basename = basename(file.realpath)
            file.title = 
        return context
