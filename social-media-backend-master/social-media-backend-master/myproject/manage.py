from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
from rest_framework import serializers, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q


import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')


# Models
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


# Serializers
class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'created_at']


class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follower
        fields = ['follower', 'following']


class UserActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAction
        fields = ['user', 'target_user', 'action']


# Views
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author__username=author)
        return queryset


class FollowerViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def follow(self, request, username=None):
        try:
            target_user = User.objects.get(username=username)
            if target_user == request.user:
                return Response({'detail': 'You cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)
            Follower.objects.get_or_create(follower=request.user, following=target_user)
            return Response({'detail': 'Followed successfully.'})
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def unfollow(self, request, username=None):
        try:
            target_user = User.objects.get(username=username)
            Follower.objects.filter(follower=request.user, following=target_user).delete()
            return Response({'detail': 'Unfollowed successfully.'})
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def followers(self, request, username=None):
        try:
            user = User.objects.get(username=username)
            followers = user.followers.all()
            serializer = FollowerSerializer(followers, many=True)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def following(self, request, username=None):
        try:
            user = User.objects.get(username=username)
            following = user.following.all()
            serializer = FollowerSerializer(following, many=True)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)


class UserActionViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def action(self, request, username=None):
        try:
            target_user = User.objects.get(username=username)
            if target_user == request.user:
                return Response({'detail': 'You cannot perform actions on yourself.'}, status=status.HTTP_400_BAD_REQUEST)

            action = request.data.get('action')
            if action not in ['HIDE', 'BLOCK']:
                return Response({'detail': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)

            UserAction.objects.update_or_create(
                user=request.user, target_user=target_user, defaults={'action': action}
            )
            return Response({'detail': f'{action} action performed successfully.'})
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['delete'])
    def remove_action(self, request, username=None):
        try:
            target_user = User.objects.get(username=username)
            UserAction.objects.filter(user=request.user, target_user=target_user).delete()
            return Response({'detail': 'Action removed successfully.'})
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def list_actions(self, request):
        actions = UserAction.objects.filter(user=request.user)
        serializer = UserActionSerializer(actions, many=True)
        return Response(serializer.data)


class FeedViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        hidden_users = UserAction.objects.filter(user=request.user, action='HIDE').values_list('target_user', flat=True)
        blocked_users = UserAction.objects.filter(user=request.user, action='BLOCK').values_list('target_user', flat=True)
        following = Follower.objects.filter(follower=request.user).values_list('following', flat=True)

        posts = Post.objects.filter(
            author__in=following
        ).exclude(
            author__in=hidden_users
        ).exclude(
            author__in=blocked_users
        ).order_by('-created_at')

        paginator = PageNumberPagination()
        paginated_posts = paginator.paginate_queryset(posts, request)
        serializer = PostSerializer(paginated_posts, many=True)
        return paginator.get_paginated_response(serializer.data)


# URL Configuration
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'users', FollowerViewSet, basename='user')
router.register(r'actions', UserActionViewSet, basename='action')
router.register(r'feed', FeedViewSet, basename='feed')

urlpatterns = [
    path('api/', include(router.urls)),
]
