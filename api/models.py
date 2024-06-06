from django.db import models
from pgvector.django import VectorField
from django.contrib.postgres.fields import ArrayField
# Create your models here.

class files(models.Model):
    filename = models.CharField(max_length=255 , primary_key=True)

class Chat(models.Model):
    name = models.CharField(max_length=255 , primary_key=True)
    messages = models.JSONField()
    files = ArrayField(models.CharField(blank=True , null=True), blank=True)

class filecontent(models.Model):
    filename=models.ForeignKey(files, on_delete=models.CASCADE)
    chunk = models.CharField(max_length=3700)
    feature_vector = VectorField(dimensions=1536)

class excelfilecontent(models.Model):
    filename=models.ForeignKey(files, on_delete=models.CASCADE)
    content = models.JSONField()