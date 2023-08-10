from django.shortcuts import get_object_or_404
from recipes.models import Recipe
from rest_framework import status
from rest_framework.response import Response
from users.models import User


class ActionBasedRelationshipMixin:
    def perform_action(self, user, model, serializer, response_text, **kwargs):
        action = self.action
        id_key = 'id' if action == 'subscribe' else 'pk'

        actions_mapping = {
            'favorite': (Recipe, 'recipe'),
            'shopping_cart': (Recipe, 'recipe'),
            'subscribe': (User, 'author'),
        }

        if action not in actions_mapping:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        model_class, relation_name = actions_mapping[action]
        target_obj = get_object_or_404(model_class, id=self.kwargs[id_key])

        if self.request.method == 'POST':
            create_args = {'user': user, relation_name: target_obj}
            existing_instance = model.objects.filter(**create_args).exists()

            if action == 'subscribe':
                serializer_instance = serializer(
                    target_obj,
                    data=self.request.data,
                    context={'request': self.request}
                )
                serializer_instance.is_valid(raise_exception=True)
            else:
                serializer_instance = serializer(
                    target_obj, context={'request': self.request}
                )

            if not existing_instance:
                model.objects.create(**create_args)
                return Response(
                    serializer_instance.data,
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    response_text,
                    status=status.HTTP_400_BAD_REQUEST
                )

        elif self.request.method == 'DELETE':
            obj = model.objects.filter(
                user=user,
                **{relation_name: target_obj}
            )
            obj.delete()
            return Response(
                'Успешно выполнено!',
                status=status.HTTP_204_NO_CONTENT
            )

        return Response(status=status.HTTP_400_BAD_REQUEST)
