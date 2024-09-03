# Generated by Django 5.0.6 on 2024-09-02 15:41

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents_parser', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='extracteddata',
            name='search_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.AlterField(
            model_name='extracteddata',
            name='date_of_search',
            field=models.DateField(auto_now_add=True),
        ),
    ]
