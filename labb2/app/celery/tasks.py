from .config import celery_app
import time
import asyncio
from app.websocket.manager import manager

@celery_app.task(bind=True)
def encode_task(self, operation: str, text: str = None, key: str = None, encoded_data: str = None, huffman_codes: dict = None, padding: int = None, task_id: str = None):
    loop = asyncio.get_event_loop()
    if task_id:
        loop.run_until_complete(manager.send_json(task_id, {
            "status": "STARTED",
            "task_id": task_id,
            "operation": operation
        }))
    self.update_state(state='STARTED', meta={"status": "STARTED", "operation": operation})
    for i in range(5):
        if task_id:
            loop.run_until_complete(manager.send_json(task_id, {
                "status": "PROGRESS",
                "task_id": task_id,
                "operation": operation,
                "progress": (i+1)*20
            }))
        self.update_state(state='PROGRESS', meta={"status": "PROGRESS", "operation": operation, "progress": (i+1)*20})
        time.sleep(1)
    if operation == "encode":
        result = {
            "encoded_data": "base64_encoded_string",
            "huffman_codes": {"A": "0"},
            "padding": 4
        }
    else:
        result = {
            "decoded_text": "Hello, World!"
        }
    if task_id:
        loop.run_until_complete(manager.send_json(task_id, {
            "status": "COMPLETED",
            "task_id": task_id,
            "operation": operation,
            "result": result
        }))
    return {"status": "COMPLETED", "operation": operation, "result": result}
