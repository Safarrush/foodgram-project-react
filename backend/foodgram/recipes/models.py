from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum

from .validators import validate_hex_color

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        unique=True,
        max_length=200,
        verbose_name='Название'
    )
    color = models.CharField(
        unique=True,
        max_length=7,
        verbose_name='Цвет в HEX',
        validators=[validate_hex_color]
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Уникальный слаг'
    )


class Recipe(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Список id тегов'
    )
    cooking_time = models.PositiveIntegerField(
        validators=[
            MinValueValidator(
                1, message='Минимальное значение 1!'
            )
        ],
        verbose_name='Время приготовления (в минутах)'
    )
    text = models.TextField(verbose_name='Описание')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Список ингредиентов'
    )
    image = models.ImageField(
        blank=True,
        verbose_name='Ссылка на картинку на сайте'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_ingredients',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(
        validators=[
            MinValueValidator(
                1, message='Минимальное значение 1!'
            )
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'

    def __str__(self):
        return (
            f'{self.ingredient.name}'
            f'{self.ingredient.measurement_unit}'
            f'{self.amount}'
        )

    def get_shopping_cart_text(self, user):
        recipe_list = RecipeIngredient.objects.filter(
            recipe__cart__user=user
        ).values('ingredient__name', 'ingredient__measurement_unit').annotate(
            amount=Sum('amount')
        )
        text = 'Список покупок для готовки:\n'
        for i in recipe_list:
            ingredient = i['ingredient__name']
            unit = i['ingredient__measurement_unit']
            amount = i['amount']
            text += f'{ingredient} - {amount} {unit}\n'
        return text


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил в избранное рецепт {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил в корзину {self.recipe}'
