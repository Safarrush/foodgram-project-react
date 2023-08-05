from django_filters.rest_framework import FilterSet, filters
from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(
        method='filters_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filters_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'author', 'tags',
        )

    def filters_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous or not value:
            return queryset
        return queryset.filter(favorite__user=user)

    def filters_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous or not value:
            return queryset
        return queryset.filter(cart__user=user)
