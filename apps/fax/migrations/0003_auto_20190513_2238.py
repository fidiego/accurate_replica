# Generated by Django 2.2.1 on 2019-05-13 22:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fax', '0002_auto_20190513_2237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fax',
            name='sid',
            field=models.CharField(blank=True, max_length=34, null=True),
        ),
    ]
