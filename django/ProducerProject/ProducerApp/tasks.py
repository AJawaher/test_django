# ProducerApp.tasks
from celery import shared_task
from customer.ConsumerProject.ConsumerApp.tasks import process_message as consumer_process_message

@shared_task
def send_message_to_consumer(message_data, webhook_url):
    consumer_process_message.apply_async(args=[message_data, webhook_url])
