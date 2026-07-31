from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('technical', '0002_concept_example'),
    ]

    operations = [
        migrations.AddField(
            model_name='concept',
            name='reference_url',
            field=models.URLField(blank=True, default='', max_length=400),
        ),
        migrations.AddField(
            model_name='concept',
            name='flowchart_mermaid',
            field=models.TextField(blank=True, default=''),
        ),
    ]
