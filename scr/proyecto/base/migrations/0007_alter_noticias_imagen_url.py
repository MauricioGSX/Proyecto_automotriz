# Generated by Django 4.2.4 on 2023-10-30 00:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_noticias_imagen_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='noticias',
            name='imagen_url',
            field=models.TextField(),
        ),
    ]
