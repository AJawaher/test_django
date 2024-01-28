# ConsumerApp/tests.py
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from ConsumerApp.tasks import app as celery_app, process_message

celery_app.config_from_object('django.conf:settings', namespace='CELERY')


@override_settings(CELERY_TASK_EAGER_PROPAGATES=True, CELERY_TASK_ALWAYS_EAGER=True)
class ProcessMessageTaskTest(TestCase):
    def test_process_message_task_success(self):
        message_data = {'id': 1, 'text': 'Test Message'}
        webhook_url = 'http://example.com/webhook/'
        expected_result = 'egasseM tseT'

        # Use apply_async to run the task in the background and get the result
        result = process_message.apply_async(args=[message_data, webhook_url]).get()

        # Check if the result matches the expected reversed format
        self.assertEqual(result, expected_result)

    def test_process_message_task_failure(self):
        # Test the case where the message processing intentionally fails
        message_data = {'id': 2, 'text': 'Fail Message'}
        webhook_url = 'http://example.com/webhook/'

        try:
            task_result = process_message.apply_async(args=[message_data, webhook_url]).get()
        except Exception as e:
            print(f"Exception caught: {e}")
            raise  # Re-raise the exception

        print(f"Task result: {task_result}")

        with self.assertRaises(Exception):
            # Raise an AssertionError if the task result is not an exception
            raise AssertionError(f"Expected an exception, but got result: {task_result}")


@override_settings(CELERY_TASK_EAGER_PROPAGATES=True, CELERY_TASK_ALWAYS_EAGER=True)
class TaskExecutionViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.execution_url = reverse('execute_task')

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_execute_task_view(self):
        # Test the case where a valid task is executed
        data = {'message_data': {'id': 1, 'text': 'Test message'}, 'webhook_url': 'http://example.com/webhook/'}
        response = self.client.post(self.execution_url, data, format='json')

        # Ensure the response status code is '200 OK'
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure the response contains the task_id
        self.assertIn('task_id', response.data)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_execute_task_view_invalid_data(self):
        # Test the case where invalid data is provided
        data = {'message_data': {'id': 1, 'text': 'Test message'}, 'webhook_url': 'http://example.com/webhook/'}

        # Use a try-except block to catch the expected 400 Bad Request status code
        try:
            response = self.client.post(self.execution_url, data, format='json')
        except Exception as e:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)






