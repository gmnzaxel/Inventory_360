from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('control', '0008_alter_product_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='document_number',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterUniqueTogether(
            name='document',
            unique_together={('business', 'document_type', 'document_number')},
        ),
        migrations.AddIndex(
            model_name='movement',
            index=models.Index(fields=['date'], name='movement_date_idx'),
        ),
        migrations.AddIndex(
            model_name='movement',
            index=models.Index(fields=['movement_type'], name='movement_type_idx'),
        ),
    ]

