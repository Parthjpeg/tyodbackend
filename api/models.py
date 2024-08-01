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
    function = models.CharField(max_length=255 , null=True)

class filecontent(models.Model):
    filename=models.ForeignKey(files, on_delete=models.CASCADE)
    chunk = models.CharField(max_length=3700)
    feature_vector = VectorField(dimensions=1536)

class excelfilecontent(models.Model):
    filename=models.ForeignKey(files, on_delete=models.CASCADE)
    content = models.JSONField()

class Tvsm_Vehicles(models.Model):
    vehicle_name = models.CharField(max_length=100)
    vehicle_type = models.CharField(max_length=100) #electirc gear non-gear
    vehicle_fuel_type = models.CharField(max_length=100) #electirc pertrol
    vehicle_prime_users = models.CharField(max_length=1000) 
    vehicle_mileage = models.IntegerField()
    vehicle_price = models.IntegerField()
    vehicle_daily_commute = models.CharField(max_length=1000)
    vehicle_description = models.CharField(max_length=2000)
    vehical_link = models.CharField(max_length=200 , null=True)
    vehical_img_link = models.CharField(max_length=200 , null=True)
    vehical_testdrive_link = models.CharField(max_length=200 , null=True)
    vehical_booking_link = models.CharField(max_length=200 , null=True)
    feature_vector = VectorField(dimensions=1536)

class Tvsm_Accessories(models.Model):
    product_name = models.CharField(max_length=100)
    vehicle_name = models.CharField(max_length=100)
    product_price = models.IntegerField()
    product_primary_color = models.CharField(max_length=100)
    product_accent_color = models.CharField(max_length=100)
    product_description = models.CharField(max_length=1500)
    product_user = models.CharField(max_length=100)
    product_link = models.CharField(max_length=200 , null=True)
    product_img_link = models.CharField(max_length=200 , null=True)
    feature_vector = VectorField(dimensions=1536)

# electric or petrol
# geared or non geared
# budget
# City use or long rides