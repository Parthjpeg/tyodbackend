# Generated by Django 4.2 on 2024-06-06 08:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_chat_files'),
    ]

    operations = [
        migrations.CreateModel(
            name='excelfilecontent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.JSONField()),
                ('filename', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.files')),
            ],
        ),
    ]
