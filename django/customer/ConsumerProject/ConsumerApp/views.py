from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .tasks import process_message
from rest_framework import viewsets
from django_celery_results.models import TaskResult
from .serializers import TaskResultSerializer
from rest_framework.permissions import AllowAny


class TaskResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TaskResult.objects.all()
    serializer_class = TaskResultSerializer
    permission_classes = [IsAuthenticated]


class TaskExecutionView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data
        message_data = data.get('message_data')
        webhook_url = data.get('webhook_url')

        # Call the Celery task
        task_result = process_message.delay(message_data, webhook_url)

        # Send back a response with the task ID to the producer
        return Response({'task_id': task_result.id})
