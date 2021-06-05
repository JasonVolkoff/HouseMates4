# Generated by Django 2.2 on 2021-06-05 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_and_profile', '0002_auto_20210605_0617'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='action',
            field=models.CharField(choices=[('PURCHASED', 'purchased'), ('INVITED', 'invited'), ('CREATED', 'created'), ('HELPED', 'helped purchase'), ('REGISTERED', 'Registered an account')], default='CREATED', max_length=32),
        ),
    ]
