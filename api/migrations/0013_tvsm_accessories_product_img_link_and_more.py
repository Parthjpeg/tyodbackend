# Generated by Django 4.2 on 2024-08-01 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_tvsm_vehicles_vehical_booking_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='tvsm_accessories',
            name='product_img_link',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='tvsm_accessories',
            name='product_link',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
