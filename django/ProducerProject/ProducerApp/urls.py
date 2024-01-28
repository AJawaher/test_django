from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MessageViewSet, WebhookReceiverView, ExecuteTaskView, list_tasks

router = DefaultRouter()
router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    path('webhook/', WebhookReceiverView.as_view(), name='webhook_receiver'),
    path('messages/', include(router.urls)),
    path('api/', include(router.urls)),
    path('', include(router.urls)),

    path('execute_task/', ExecuteTaskView.as_view(), name='execute_task'),
    path('list_tasks/', list_tasks, name='list_tasks'),
]
