from recipes.models import IngredientsInRecipe

# Можно я докстринги и аннотацию доработаю после диплома? а то время мало до дедлайна олсталось, все мысли о том как бы успеть сдать проект.


def add_ingredients_to_recipe(recipe, ingredients):
    IngredientsInRecipe.objects.bulk_create(
            [
                IngredientsInRecipe(
                    recipe=recipe,
                    ingredient_id=ingredient['ingredients']['id'],
                    amount=ingredient['amount'],
            )
                for ingredient in ingredients
            ]
        )