from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
from rest_framework import serializers, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q

# Import models and serializers
from .models import Post, Follower, UserAction
from .serializers import PostSerializer, FollowerSerializer, UserActionSerializer


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
            followers = Follower.objects.filter(following=user)
            serializer = FollowerSerializer(followers, many=True)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def following(self, request, username=None):
        try:
            user = User.objects.get(username=username)
            following = Follower.objects.filter(follower=user)
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
