# Generated by Django 4.0.3 on 2022-03-29 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(blank=True, related_name='recipe', to='recipes.ingredient', verbose_name='ingridient'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='tag_recipe', to='recipes.tag', verbose_name='tag'),
        ),
    ]
