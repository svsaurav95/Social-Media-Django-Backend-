from django.urls import path


from .views import PostViewSet, FollowerViewSet, UserActionViewSet, FeedViewSet


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
