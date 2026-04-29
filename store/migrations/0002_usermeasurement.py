# Generated migration for UserMeasurement model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserMeasurement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('height', models.IntegerField(default=170, help_text='Рост в см')),
                ('chest', models.IntegerField(default=92, help_text='Обхват груди в см')),
                ('waist', models.IntegerField(default=76, help_text='Обхват талии в см')),
                ('hips', models.IntegerField(default=98, help_text='Обхват бёдер в см')),
                ('shoulders', models.IntegerField(default=116, help_text='Ширина плеч в см')),
                ('arm_length', models.IntegerField(default=58, help_text='Длина руки в см')),
                ('leg_length', models.IntegerField(default=80, help_text='Длина ноги в см')),
                ('shoe_size', models.IntegerField(default=40, help_text='Размер обуви')),
                ('weight', models.IntegerField(default=70, help_text='Вес в кг')),
                ('gender', models.CharField(choices=[('male', 'Мужской'), ('female', 'Женский'), ('neutral', 'Универсальный')], default='neutral', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='measurements', to='store.user')),
            ],
        ),
    ]
