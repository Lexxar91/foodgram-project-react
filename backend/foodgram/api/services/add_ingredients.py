from recipes.models import AmountIngredient


def add_ingredients_to_recipe(recipe, ingredients):
    AmountIngredient.objects.bulk_create(
            [
                AmountIngredient(
                    recipe=recipe,
                    ingredient_id=ingredient['ingredients']['id'],
                    amount=ingredient['amount'],
            )
                for ingredient in ingredients
            ]
        )