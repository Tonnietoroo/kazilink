from django.db import models

# Create your models here.

class Contact(models.Model):
    """Contact table"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    replied = models.BooleanField(default=False)
   
   
    def __str__(self):
       return self.name
    
    