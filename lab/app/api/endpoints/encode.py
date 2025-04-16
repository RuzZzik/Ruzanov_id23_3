from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import base64
from app.services.huffman import huffman_encode, decode_text
from app.services.xor import xor_encrypt, xor_decrypt
from app.api.deps import get_current_user

router = APIRouter()

class EncodeRequest(BaseModel):
    text: str
    key: str

class EncodeResponse(BaseModel):
    encoded_data: str
    key: str
    huffman_codes: dict
    padding: int

class DecodeRequest(BaseModel):
    encoded_data: str
    key: str
    huffman_codes: dict
    padding: int

class DecodeResponse(BaseModel):
    decoded_text: str

@router.post("/encode", response_model=EncodeResponse)
def encode_text(request: EncodeRequest, current_user = Depends(get_current_user)):
    try:
        # First, apply Huffman encoding
        encoded_text, huffman_codes, padding = huffman_encode(request.text)
        
        # Then, apply XOR encryption
        encrypted_bytes = xor_encrypt(encoded_text, request.key)
        
        # Convert to base64 for safe transmission
        encoded_data = base64.b64encode(encrypted_bytes).decode('utf-8')
        
        return EncodeResponse(
            encoded_data=encoded_data,
            key=request.key,
            huffman_codes=huffman_codes,
            padding=padding
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/decode", response_model=DecodeResponse)
def decode_text(request: DecodeRequest, current_user = Depends(get_current_user)):
    try:
        # Convert from base64
        encrypted_bytes = base64.b64decode(request.encoded_data)
        
        # Apply XOR decryption
        encoded_text = xor_decrypt(encrypted_bytes, request.key)
        
        # Remove padding
        encoded_text = encoded_text[:-request.padding] if request.padding > 0 else encoded_text
        
        # Apply Huffman decoding
        decoded_text = decode_text(encoded_text, request.huffman_codes)
        
        return DecodeResponse(decoded_text=decoded_text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 