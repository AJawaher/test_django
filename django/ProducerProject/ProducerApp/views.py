# ProducerApp/views.py
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Message
from .serializers import MessageSerializer
from rest_framework import status
from django.shortcuts import render
from django.http import JsonResponse
from .tasks import send_message_to_consumer
from django.views import View
from celery.result import AsyncResult
from django.contrib import messages


class ExecuteTaskView(View):
    template_name = 'execute_task.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        # Get the data from the POST request
        message_data = {
            'text': request.POST.get('text'),
        }

        # Create a new Message instance and save it to the database
        new_message = Message.objects.create(**message_data)

        # Store the task ID in the session
        request.session['last_task_id'] = str(new_message.id)

        # Log the session data for debugging
        print(request.session.items())

        # Replace 'http://example.com/webhook/' with your actual webhook URL
        webhook_url = 'http://example.com/webhook/'
        # Send the message to the consumer
        task = send_message_to_consumer.apply_async(args=[message_data, webhook_url])

        # Log the task ID for debugging
        print(f'Task ID: {task.id}')

        return JsonResponse({'status': 'Task scheduled successfully'})


class WebhookReceiverView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        message_id = data.get('message_id')
        result = data.get('result')

        try:
            message = Message.objects.get(pk=message_id)
            message.result = result
            message.save()
            serializer = MessageSerializer(message)
            return Response(serializer.data)
        except Message.DoesNotExist:
            return Response({'error': 'Message not found'}, status=404)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

# def list_tasks(request):
#     # Print the session data for debugging
#     print(request.session.items())
#
#     # Assuming you have a task ID stored in the session
#     task_id = request.session.get('last_task_id')
#
#     if task_id:
#         # Retrieve task result using Celery's AsyncResult
#         result = AsyncResult(task_id)
#         # You may want to customize this based on your task result structure
#         task_result = {'id': task_id, 'status': result.status, 'result': result.result}
#     else:
#         task_result = None
#
#     return render(request, 'list_tasks.html', {'task_result': task_result})

def list_tasks(request):
    # Get all tasks from the database
    all_tasks = Message.objects.all()

    # Pass the list of tasks to the template context
    return render(request, 'list_tasks.html', {'all_tasks': all_tasks})