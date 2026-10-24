from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("icdapp", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="icdmodel",
            options={
                "ordering": ["id"],
                "verbose_name": "ICD code",
                "verbose_name_plural": "ICD codes",
            },
        ),
        migrations.AlterField(
            model_name="icdmodel",
            name="category_code",
            field=models.CharField(blank=True, db_index=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="icdmodel",
            name="full_code",
            field=models.CharField(blank=True, db_index=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="icdmodel",
            name="category_title",
            field=models.CharField(blank=True, db_index=True, max_length=200, null=True),
        ),
    ]
