from django.db import models

from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils.safestring import mark_safe

class SettingOption(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Setting(models.Model):
    option = models.OneToOneField(SettingOption, blank=True, null=True, on_delete=models.SET_NULL, related_name='setting_option_selected')
    value = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.option.name}: {self.value}'

class Image(models.Model):
    name = models.CharField(max_length=255)
    image_file = models.ImageField(upload_to='images/', blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True, default=None)

    def __str__(self):
        if self.title:
            return f'{self.title}'
        else:
            return f'{self.name}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique image name')
        ]

    def has_image_file(self):
        if self.image_file:
            return True
        else:
            return False

@receiver(pre_delete, sender=Image)
def image_delete(sender, instance, **kwargs):
    instance.image_file.delete(save=False)

class Movie(models.Model):
    tmdb_id = models.IntegerField()
    title = models.CharField(max_length=100, blank=True, null=True)
    data = models.JSONField(blank=True, null=True)
    image = models.ForeignKey(Image, blank=True, null=True, on_delete=models.SET_NULL, related_name='movie_poster_selected')
    download_correct = models.BooleanField(default=True)
    download_error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        flags = []
        if self.image:
            flags.append('P')
        if self.year():
            flags.append(f'({self.year()})')
        flags = ' '.join(flags)
        if self.title is not None:
            return f'({self.tmdb_id}) {self.title} [{flags}]'
        else:
            return str(self.tmdb_id)

    def year(self):
        if self.data:
            if 'release_date' in self.data:
                return self.data["release_date"][:4]
        else:
            return None

    def get_poster_url(self):
        if self.image and self.image.has_image_file():
            return self.image.image_file.url
        else:
            return None
