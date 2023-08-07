from rest_framework import status
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
