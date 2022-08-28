# Generated by Django 2.2.19 on 2022-08-05 08:31

from django.db import migrations
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0009_auto_20220802_1705'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='group',
            options={'verbose_name': 'Группа', 'verbose_name_plural': 'Группы'},
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': [django.db.models.expressions.OrderBy(django.db.models.expressions.F('pub_date'), descending=True, nulls_last=True)], 'verbose_name': 'Публикация', 'verbose_name_plural': 'Публикации'},
        ),
    ]
