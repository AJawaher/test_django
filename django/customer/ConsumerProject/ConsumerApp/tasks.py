
from celery import shared_task
import sys
from celery import Celery

app = Celery('ConsumerProject')

# Other Celery configurations...

if 'test' in sys.argv:
    # Use a testing-specific result backend, such as 'db+sqlite:///:memory:'
    app.conf.CELERY_RESULT_BACKEND = 'db+sqlite:///:memory:'


class ProcessMessageFailedException(Exception):
    pass


# @shared_task
# def process_message(message_data, webhook_url):
#     try:
#         # Attempt to perform the message processing
#         processed_text = message_data['text'][::-1]  # Reverse the text as an example
#
#         # Store the task result in the Django database
#         task_result = TaskResult.objects.create(
#             task_name='ConsumerApp.tasks.process_message',
#             task_args=f'({message_data}, {webhook_url})',
#             task_kwargs={},
#             date_done=timezone.now(),
#             result=processed_text,
#         )
#
#         # Send the result back to the producer's webhook URL using requests
#         payload = {'message_id': message_data['id'], 'result': processed_text}
#         response = requests.post(webhook_url, json=payload)
#
#         return processed_text
#     except Exception as e:
#         # Raise a specific exception when the processing fails
#         raise ProcessMessageFailedException(str(e))
@shared_task
def process_message(message_data, webhook_url):
    try:
        print("Task process_message started")
        # Your task logic here
        processed_text = message_data['text'][::-1]  # Reverse the text as an example
        print("Task process_message finished")
        return processed_text
    except Exception as e:
        print(f"Task process_message failed: {str(e)}")
        # Log the exception or handle it appropriately
        raise