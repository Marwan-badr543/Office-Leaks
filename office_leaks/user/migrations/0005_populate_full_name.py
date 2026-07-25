from django.db import migrations
from django.db.models import F, Value
from django.db.models.functions import Concat

def populate_full_name(apps, schema_editor):
    User = apps.get_model('user', 'User')
    User.objects.all().update(full_name=Concat(F('first_name'), Value(' '), F('last_name')))

def reverse_populate(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_user_full_name'),
    ]

    operations = [
        migrations.RunPython(populate_full_name, reverse_code=reverse_populate),
    ]
