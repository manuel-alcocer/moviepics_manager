from django.urls import path


from .views import FilesView

urlpatterns = [
    path('files/', FilesView.as_view(), name='files'),
]
