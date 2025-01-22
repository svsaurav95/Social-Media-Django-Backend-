from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
from rest_framework import serializers, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q



class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(max_length=280)
    created_at = models.DateTimeField(default=now)


class Follower(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')

    class Meta:
        unique_together = ('follower', 'following')


class UserAction(models.Model):
    ACTION_CHOICES = (
        ('HIDE', 'Hide'),
        ('BLOCK', 'Block'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actions')
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='targeted_by_actions')
    action = models.CharField(max_length=5, choices=ACTION_CHOICES)

    class Meta:
        unique_together = ('user', 'target_user', 'action')

