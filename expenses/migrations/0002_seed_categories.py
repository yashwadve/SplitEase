from django.db import migrations


DEFAULT_CATEGORIES = [
    ('Food & Dining', 'bi-cup-hot'),
    ('Transport', 'bi-car-front'),
    ('Accommodation', 'bi-house'),
    ('Entertainment', 'bi-film'),
    ('Shopping', 'bi-bag'),
    ('Groceries', 'bi-basket'),
    ('Utilities', 'bi-lightning-charge'),
    ('Travel', 'bi-airplane'),
    ('Other', 'bi-three-dots'),
]


def seed_categories(apps, schema_editor):
    Category = apps.get_model('expenses', 'Category')
    for name, icon in DEFAULT_CATEGORIES:
        Category.objects.get_or_create(name=name, defaults={'icon': icon})


def remove_categories(apps, schema_editor):
    Category = apps.get_model('expenses', 'Category')
    Category.objects.filter(name__in=[name for name, _ in DEFAULT_CATEGORIES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0001_initial'),  # <-- change to your actual latest expenses migration name
    ]

    operations = [
        migrations.RunPython(seed_categories, remove_categories),
    ]