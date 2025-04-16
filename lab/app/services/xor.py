def xor_encrypt(text: str, key: str) -> bytes:
    text_bytes = text.encode('utf-8')
    key_bytes = key.encode('utf-8')

    repeated_key = (key_bytes * (len(text_bytes) // len(key_bytes) + 1))[:len(text_bytes)]

    encrypted_bytes = bytes(a ^ b for a, b in zip(text_bytes, repeated_key))
    return encrypted_bytes

def xor_decrypt(encrypted_bytes: bytes, key: str) -> str:
    key_bytes = key.encode('utf-8')

    repeated_key = (key_bytes * (len(encrypted_bytes) // len(key_bytes) + 1))[:len(encrypted_bytes)]

    decrypted_bytes = bytes(a ^ b for a, b in zip(encrypted_bytes, repeated_key))
    return decrypted_bytes.decode('utf-8') 