from api.mixins import ActionBasedRelationshipMixin
from api.serializers import (FollowAuthorSerializer, FollowSerializer,
                             IngredientSerializer, RecipeCreateSerializer,
                             RecipeGetSerializer, RecipeIngredient,
                             RecipeSampleSerializer, TagSerializer,
                             UserSerializer)
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from users.models import Follow, User

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAdminOrReadOnlyPermission, IsAuthorOrReadOnly


class CustomUserViewSet(ActionBasedRelationshipMixin, UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        user = self.request.user
        serializer = FollowSerializer
        return self.perform_action(
            user, Follow, serializer, 'Уже подписан', **kwargs
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='subscriptions'
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowAuthorSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnlyPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnlyPermission,)
    pagination_class = None


class RecipeViewSet(ActionBasedRelationshipMixin, ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (IsAuthorOrReadOnly,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'recipe_ingredients__ingredient', 'tags'
        ).all()
        return recipes

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeGetSerializer
        return RecipeCreateSerializer

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, **kwargs):
        user = self.request.user
        serializer = RecipeSampleSerializer
        return self.perform_action(
            user, Favorite, serializer, 'Такой рецепт уже в избранном!',
            **kwargs
        )

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, **kwargs):
        user = self.request.user
        serializer = RecipeSampleSerializer
        return self.perform_action(
            user, ShoppingCart, serializer, 'Такой рецепт уже есть!', **kwargs
        )

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        recipe_ingredient = RecipeIngredient()
        response = recipe_ingredient.generate_shopping_cart_pdf(request.user)
        return response
