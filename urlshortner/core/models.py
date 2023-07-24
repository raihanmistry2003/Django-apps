from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import userManager
import qrcode
from io import BytesIO
from django.core.files import File

# Create your models here.

class urls(models.Model):
    email = models.EmailField(max_length=254)
    short_url = models.CharField(unique=True,max_length = 20)
    long_url = models.TextField()
    title = models.CharField(max_length=100)
    url_hit_count = models.PositiveIntegerField(default=0)
    url_created_at = models.DateTimeField(auto_now=True)
    url_updated_at = models.DateTimeField(auto_now=True)


class User(AbstractUser):
    username = None
    profile_pic = models.ImageField(upload_to='image', blank=True, null=True)
    email = models.EmailField(unique=True, max_length=254)
    email_token = models.CharField(max_length=100, null=True, blank=True)
    is_email_varified = models.BooleanField(default=False)

    objects = userManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class Qrcodes(models.Model):
    email = models.EmailField(max_length=254)
    long_url = models.TextField()
    title = models.CharField(max_length=100)
    qrcode = models.ImageField(upload_to='Qrcodes', null=True, blank='True')
    
    # save method
    def save(self, *args, **kwargs):
        my_qr = qrcode.make(self.long_url)
        file_name = f'{self.email}-{self.title}qr.png'
        stream = BytesIO()
        my_qr.save(stream, 'PNG')
        self.qrcode.save(file_name, File(stream), save=False)
        super().save(*args, **kwargs)
