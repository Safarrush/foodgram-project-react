from django.shortcuts import get_object_or_404
from recipes.models import Favorite, Recipe, ShoppingCart
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import RecipeSampleSerializer


class FavoriteShoppingCartMixin:
    def perform_action(self, user, recipe, model, response_text):
        if self.request.method == 'POST':
            if model.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    response_text,
                    status=status.HTTP_400_BAD_REQUEST
                )
            model.objects.create(user=user, recipe=recipe)
            serializer = RecipeSampleSerializer(
                recipe, context={'request': self.request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            obj = model.objects.filter(user=user, recipe=recipe)
            if obj.exists():
                obj.delete()
            return Response(
                'Рецепт удален!',
                status=status.HTTP_204_NO_CONTENT
            )

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, **kwargs):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        return self.perform_action(
            user, recipe, Favorite,
            'Такой рецепт уже в избранном!'
        )

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, **kwargs):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        return self.perform_action(
            user, recipe, ShoppingCart, 'Такой рецепт уже есть!'
        )
