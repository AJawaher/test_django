from django.db.models.signals import post_save
from django.dispatch import receiver
from django_celery_results.models import TaskResult
import requests


@receiver(post_save, sender=TaskResult)
def send_result_to_producer(sender, instance, **kwargs):
    # Check if the task result is successful
    if instance.status == 'SUCCESS':
        # Send the result to the producer's webhook URL using requests
        payload = {'message_id': instance.task_args[0]['id'], 'result': instance.result}
        webhook_url = instance.task_args[1]
        response = requests.post(webhook_url, json=payload)
