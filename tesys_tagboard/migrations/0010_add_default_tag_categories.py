from django.db import migrations
from django.db import migrations
from django.db.models import Model

def add_categories(apps, schema_editor):
    TagCategory = apps.get_model("tesys_tagboard.TagCategory")
    TagCategory(name="artist", bg="#bae1ff").save()
    TagCategory(name="copyright", bg="#ffd3b6").save()

class Migration(migrations.Migration):
    dependencies = [
        ('tesys_tagboard', '0009_tagcategory_remove_tag_tag_category_idx_and_more'),
    ]

    operations = [
        migrations.RunPython(add_categories),
    ]
