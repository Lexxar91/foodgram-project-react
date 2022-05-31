# Generated by Django 4.0.3 on 2022-04-20 14:11

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AmountIngredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1, 'Мы же не воздух собираемся готовить?'), django.core.validators.MaxValueValidator(1000, 'Где же взять столько денег на такое блюдо?')], verbose_name='Количество')),
            ],
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, verbose_name='name')),
                ('measurement_unit', models.CharField(max_length=30, verbose_name='единица измерения')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=200, verbose_name='name')),
                ('text', models.TextField(verbose_name='text')),
                ('cooking_time', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, 'Время приготовления не может быть меньше 1 минуты!')], verbose_name='Время приготовления(в минутах)')),
                ('image', models.ImageField(blank=True, upload_to='recipes/', verbose_name='картинка')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='pub_date')),
            ],
            options={
                'ordering': ('-pub_date',),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=120, verbose_name='name')),
                ('color', models.CharField(max_length=30, verbose_name='color')),
                ('slug', models.CharField(max_length=30, verbose_name='slug')),
            ],
            options={
                'verbose_name': 'Тег',
                'ordering': ('name',),
            },
        ),
        migrations.AddConstraint(
            model_name='tag',
            constraint=models.UniqueConstraint(fields=('name', 'slug'), name='unique_name_slug'),
        ),
    ]