# Generated by Django 2.2 on 2020-02-04 01:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myarticle', '0001_initial'),
        ('myauth', '0003_auto_20200204_0932'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuserinfo',
            name='blog',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='myarticle.Blog'),
        ),
    ]