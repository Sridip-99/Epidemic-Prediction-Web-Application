# Generated by Django 5.1.3 on 2024-12-08 17:45
from django.db import migrations

def create_regularuser_group(apps, schema_editor):
    # Get the Group model from the app registry to avoid direct import issues
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='regularuser')  # Create the group if it doesn't exist

class Migration(migrations.Migration):

    dependencies = [
        ('signup_app', '0001_initial'),  # Adjust this based on your app's previous migration
    ]

    operations = [
        migrations.RunPython(create_regularuser_group),  # Add a custom operation
    ]