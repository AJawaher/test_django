from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskResultViewSet, TaskExecutionView

router = DefaultRouter()
router.register(r'task-results', TaskResultViewSet, basename='task-result')

urlpatterns = [
    path('execute-task/', TaskExecutionView.as_view(), name='execute_task'),
    path('', include(router.urls)),

]
