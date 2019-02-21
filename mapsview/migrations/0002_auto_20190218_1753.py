# Generated by Django 2.1.5 on 2019-02-18 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapsview', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('content', models.TextField()),
                ('link', models.URLField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.DeleteModel(
            name='Data',
        ),
    ]
