from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('price', models.IntegerField()),
                ('old_price', models.IntegerField(blank=True, null=True)),
                ('image', models.CharField(max_length=200)),
                ('sku', models.CharField(max_length=50)),
                ('category', models.CharField(choices=[('hoodies', 'Худи'), ('tshirts', 'Футболки'), ('shirts', 'Рубашки')], max_length=20)),
                ('is_new', models.BooleanField(default=False)),
                ('is_popular', models.BooleanField(default=False)),
                ('description', models.TextField()),
            ],
        ),
    ]
