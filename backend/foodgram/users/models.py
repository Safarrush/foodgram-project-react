from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username

MAX_LENGTH = 254


class User(AbstractUser):
    username = models.CharField(
        blank=True,
        max_length=150,
        unique=True,
        validators=[validate_username],
        verbose_name='Уникальный юзернейм',
        help_text='Имя пользователя'
    )
    email = models.EmailField(
        verbose_name="Email",
        max_length=MAX_LENGTH,
        unique=True,
        help_text='Адрес электронной почты'
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Подписка на блогеров'
        verbose_name_plural = 'Подписки на блогеров'

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
