# Generated by Django 4.2 on 2024-07-31 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_tvsm_accessories_tvsm_vehicles_vehical_img_link_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tvsm_accessories',
            name='product_description',
            field=models.CharField(max_length=1000),
        ),
    ]