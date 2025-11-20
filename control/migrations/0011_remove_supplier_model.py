from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('control', '0010_case_insensitive_uniques'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='movement',
            name='supplier',
        ),
        migrations.DeleteModel(
            name='Supplier',
        ),
    ]
