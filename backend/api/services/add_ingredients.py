from recipes.models import IngredientsInRecipe


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