# Generated by Django 2.2.9 on 2022-07-19 09:39

from django.db import migrations
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_auto_20220719_1438'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='group',
            options={'verbose_name_plural': 'Группы'},
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': [django.db.models.expressions.OrderBy(django.db.models.expressions.F('pub_date'), descending=True, nulls_last=True)], 'verbose_name_plural': 'Публикации'},
        ),
    ]
