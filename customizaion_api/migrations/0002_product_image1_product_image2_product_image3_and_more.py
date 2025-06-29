# Generated by Django 5.2.1 on 2025-05-22 09:59

import customizaion_api.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customizaion_api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image1',
            field=models.ImageField(blank=True, null=True, upload_to=customizaion_api.models.product_image_upload_to),
        ),
        migrations.AddField(
            model_name='product',
            name='image2',
            field=models.ImageField(blank=True, null=True, upload_to=customizaion_api.models.product_image_upload_to),
        ),
        migrations.AddField(
            model_name='product',
            name='image3',
            field=models.ImageField(blank=True, null=True, upload_to=customizaion_api.models.product_image_upload_to),
        ),
        migrations.AddField(
            model_name='product',
            name='image4',
            field=models.ImageField(blank=True, null=True, upload_to=customizaion_api.models.product_image_upload_to),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(upload_to=customizaion_api.models.product_image_upload_to),
        ),
    ]
