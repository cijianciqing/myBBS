# Generated by Django 2.2 on 2020-02-04 01:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myauth', '0002_auto_20200131_1832'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuserinfo',
            name='avatar',
            field=models.ImageField(default='avatars/default.png', upload_to='avatars/', verbose_name='头像'),
        ),
    ]
