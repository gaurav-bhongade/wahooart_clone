# Generated by Django 5.2.1 on 2025-06-06 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('artshop', '0003_artworkcategoryimage_description_frame_thickness'),
    ]

    operations = [
        migrations.AddField(
            model_name='artworkcategoryimage',
            name='supported_sizes',
            field=models.ManyToManyField(blank=True, null=True, related_name='category_images', to='artshop.size'),
        ),
    ]
