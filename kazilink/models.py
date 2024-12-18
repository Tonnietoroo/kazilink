from django.db import models

# Create your models here.

class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    replied = models.BooleanField(default=False)  # New field

    def __str__(self):
        return f"{self.name} - {self.subject}"

    
    