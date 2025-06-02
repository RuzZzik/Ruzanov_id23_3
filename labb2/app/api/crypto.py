from fastapi import APIRouter, HTTPException
from app.schemas.crypto import EncodeRequest, EncodeResponse, DecodeRequest, DecodeResponse
from app.services.huffman import huffman_encode, huffman_decode
from app.services.xor_cipher import xor_encrypt, xor_decrypt
import base64
import uuid
from app.celery.tasks import encode_task
from celery.result import AsyncResult
from app.celery.config import celery_app
import traceback
import logging

logging.basicConfig(level=logging.INFO)

router = APIRouter()

@router.post("/encode", response_model=EncodeResponse)
def encode(data: EncodeRequest):
    try:
        encoded_bytes, codes, padding = huffman_encode(data.text)
        encrypted_bytes = xor_encrypt(encoded_bytes, data.key)
        encoded_data = base64.b64encode(encrypted_bytes).decode()
        return EncodeResponse(
            encoded_data=encoded_data,
            key=data.key,
            huffman_codes=codes,
            padding=padding
        )
    except Exception as e:
        tb = traceback.format_exc()
        print("ERROR in encode:", tb)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/decode", response_model=DecodeResponse)
def decode(data: DecodeRequest):
    try:
        encrypted_bytes = base64.b64decode(data.encoded_data)
        decoded_bytes = xor_decrypt(encrypted_bytes, data.key)
        decoded_text = huffman_decode(decoded_bytes, data.huffman_codes, data.padding)
        return DecodeResponse(decoded_text=decoded_text)
    except Exception as e:
        tb = traceback.format_exc()
        print("ERROR in decode:", tb)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/encode-async/")
def encode_async(data: EncodeRequest):
    logging.info("[API] /encode-async/ called with: %s", data)
    try:
        task_id = str(uuid.uuid4())
        encode_task.apply_async(
            args=("encode", data.text, data.key),
            kwargs={"task_id": task_id},
            task_id=task_id
        )
        return {"task_id": task_id, "operation": "encode"}
    except Exception as e:
        tb = traceback.format_exc()
        print("ERROR in encode_async:", tb)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/decode-async/")
def decode_async(data: DecodeRequest):
    logging.info("[API] /decode-async/ called with: %s", data)
    try:
        task_id = str(uuid.uuid4())
        encode_task.apply_async(
            args=("decode", None, data.key, data.encoded_data, data.huffman_codes, data.padding),
            kwargs={"task_id": task_id},
            task_id=task_id
        )
        return {"task_id": task_id, "operation": "decode"}
    except Exception as e:
        tb = traceback.format_exc()
        print("ERROR in decode_async:", tb)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/task-status/{task_id}")
def get_task_status(task_id: str):
    logging.info("[API] /task-status/ called with: %s", task_id)
    result = AsyncResult(task_id, app=celery_app)
    response = {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.status == "SUCCESS" else None,
        "progress": result.info.get("progress") if result.info and isinstance(result.info, dict) and "progress" in result.info else None
    }
    return response
