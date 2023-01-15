from django.db import models

from tmdb.models import Movie

class MoviesDirectory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class VideoFile(models.Model):
    name = models.CharField(max_length=255)
    extension = models.CharField(max_length=100, blank=True, null=True)
    realpath = models.TextField(blank=True, null=True)
    directory = models.ForeignKey(MoviesDirectory, related_name='files', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Search(models.Model):
    name = models.CharField(max_length=255)
    movie_selected = models.ForeignKey(Movie, blank=True, null=True, on_delete=models.SET_NULL, related_name='search_movie_selected')
    result = models.JSONField(blank=True, null=True)
    last_search = models.DateTimeField(auto_now=True)
    file = models.ForeignKey(VideoFile, blank=True, null=True, on_delete=models.SET_NULL, related_name='search_file_selected')
    movies = models.ManyToManyField(Movie, related_name='search_movies')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['file'], name='unique search name')
        ]

    def __str__(self):
        return self.name

    def result_count(self):
        if self.result and 'data' in self.result:
            return len(self.result["data"])
        return 0

    def movie_id_list(self):
        if self.result_count() == 0:
            return []
        return [ movie['id'] for movie in self.result['data'] ]
    
    def get_first_movie(self):
        if self.result_count() == 0:
            return None
        return Movie.objects.get(tmdb_id=self.result['data'][0]['id'])
