from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_profile_avatar_profile_coins_badge'),
    ]

    operations = [
        migrations.CreateModel(
            name='Quote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('series', models.CharField(choices=[('OP', 'One Piece'), ('AOT', 'Attack on Titan')], max_length=3)),
                ('text', models.CharField(max_length=300)),
                ('speaker', models.CharField(blank=True, max_length=80)),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ['series', 'order', 'id'],
            },
        ),
    ]
