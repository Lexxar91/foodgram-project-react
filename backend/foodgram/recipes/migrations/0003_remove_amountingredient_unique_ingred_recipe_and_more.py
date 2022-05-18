# Generated by Django 4.0.3 on 2022-05-03 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='amountingredient',
            name='unique_ingred_recipe',
        ),
        migrations.RenameField(
            model_name='amountingredient',
            old_name='ingredients',
            new_name='ingredient',
        ),
        migrations.AddConstraint(
            model_name='amountingredient',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredient'), name='unique_ingred_recipe'),
        ),
    ]