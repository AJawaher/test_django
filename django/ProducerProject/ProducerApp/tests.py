# ProducerApp/tests.py
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Message
from django.test import TestCase
from django.urls import reverse
from django.http import JsonResponse
from rest_framework.test import force_authenticate
from django.contrib.auth.models import User
from django.test import RequestFactory
from rest_framework.test import APIClient
from rest_framework import status

from celery.result import AsyncResult
from .tasks import send_message_to_consumer


class MessageViewSetTest(APITestCase):
    def setUp(self):
        # Create two messages for testing
        self.message1 = Message.objects.create(text='Message 1')
        self.message2 = Message.objects.create(text='Message 2')

        # Generate URL for the message endpoints
        self.url = '/api/messages/messages/'

    def test_create_message_via_api(self):
        data = {'text': 'Test Message'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_messages(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_message(self):
        response = self.client.get(f'{self.url}{self.message1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['text'], 'Message 1')

    def test_update_message(self):
        updated_data = {'text': 'Updated Message'}
        response = self.client.put(f'{self.url}{self.message1.id}/', updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['text'], 'Updated Message')

    def test_delete_message(self):
        response = self.client.delete(f'{self.url}{self.message1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Message.objects.filter(id=self.message1.id).exists())

    def test_create_message_missing_data(self):
        data = {}  # Missing required data
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

from django.test import TestCase
from django.urls import reverse
from django.http import JsonResponse
from rest_framework import status
from rest_framework.test import APIClient
from celery.contrib.testing.worker import start_worker
from celery.app.task import Task
from celery.contrib.testing.app import Celery


class CeleryConnectionTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Initialize Celery app for testing
        cls.app = Celery('your_app_name')
        cls.app.config_from_object({
            'broker_url': 'pyamqp://guest:guest@localhost:5672//',
            'result_backend': 'rpc://',
        })

        # Ensure the 'celery.ping' task is available
        class PingTask(Task):
            def run(self):
                return 'pong'

        cls.app.tasks['celery.ping'] = PingTask()

        cls.worker = start_worker(cls.app, loglevel="info")
        cls.worker.__enter__()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.worker.stop()

    def test_celery_connection(self):
        # Call the Celery task
        result = send_message_to_consumer.apply_async(args=[{'id': 1, 'text': 'Test message'}, 'http://example.com/webhook/'])

        # Wait for the task to complete
        result.get()

        # Check if the task completed successfully
        self.assertTrue(result.successful())

    def test_celery_consumer_view(self):
        # Assuming you have a view that triggers the Celery task
        url = reverse('execute_task')  # Replace with your actual URL
        client = APIClient()

        # Create a user and authenticate the request
        user = User.objects.create(username='testuser')
        client.force_authenticate(user=user)

        # Make a request to the view
        response = client.post(url, {'id': 1, 'text': 'Test message'})

        # Check if the response is a successful JSON response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response, JsonResponse)
