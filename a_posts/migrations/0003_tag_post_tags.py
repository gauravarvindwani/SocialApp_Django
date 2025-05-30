# Generated by Django 5.1.7 on 2025-04-03 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('a_posts', '0002_alter_post_options_post_artist_post_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('slug', models.SlugField(max_length=20, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='tags',
            field=models.ManyToManyField(to='a_posts.tag'),
        ),
    ]
