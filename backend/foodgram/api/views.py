from os import path

from api.serializers import (FollowAuthorSerializer, FollowSerializer,
                             IngredientSerializer, RecipeCreateSerializer,
                             RecipeGetSerializer, RecipeIngredient,
                             RecipeSampleSerializer, TagSerializer,
                             UserSerializer)
from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics, ttfonts
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from users.models import Follow, User

from foodgram.settings import NAME_OF_F

from api.mixins import FavoriteShoppingCartMixin
from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAdminOrReadOnlyPermission, IsAuthorOrReadOnly
from .serializers import RecipeSerializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=self.kwargs['id'])
        user = request.user
        if request.method == 'POST':
            serializer = FollowSerializer(
                author, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            get_object_or_404(
                Follow, user=user, author=author
            ).delete()
            return Response(
                {'detail': 'Отписка совершена успешно!'},
                status=status.HTTP_204_NO_CONTENT
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


class RecipeViewSet(FavoriteShoppingCartMixin, ModelViewSet):
    queryset = Recipe.objects.all()
    #serializer_class = RecipeSerializer
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

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        recipe_ingredient = RecipeIngredient()
        text = recipe_ingredient.get_shopping_cart_text(request.user)
        response = HttpResponse(content_type='application/pdf; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename={NAME_OF_F}'
        app_path = path.realpath(path.dirname(__file__))
        font_path = path.join(
            app_path, '/usr/share/fonts/truetype/ArialMT.ttf'
        )
        MyFontObject = ttfonts.TTFont('Arial', font_path)
        pdfmetrics.registerFont(MyFontObject)
        c = canvas.Canvas(response, pagesize=letter)
        c.setFont("Arial", 24)
        lines = text.split("\n")
        y = 700
        for line in lines:
            c.drawString(100, y, line)
            y -= 30
        c.save()
        return response
