import heapq
from collections import Counter, namedtuple
from typing import Dict, Tuple

class Node(namedtuple("Node", ["left", "right"])):
    def walk(self, code, acc):
        self.left.walk(code, acc + "0")
        self.right.walk(code, acc + "1")

class Leaf(namedtuple("Leaf", ["char"])):
    def walk(self, code, acc):
        code[self.char] = acc or "0"

def huffman_encode(text: str) -> Tuple[bytes, Dict[str, str], int]:
    freq = Counter(text)
    heap = []
    for ch, fr in freq.items():
        heap.append((fr, len(heap), Leaf(ch)))
    heapq.heapify(heap)
    count = len(heap)
    while len(heap) > 1:
        fr1, _c1, left = heapq.heappop(heap)
        fr2, _c2, right = heapq.heappop(heap)
        heapq.heappush(heap, (fr1 + fr2, count, Node(left, right)))
        count += 1
    if heap:
        [(_fr, _c, root)] = heap
        code = {}
        root.walk(code, "")
    else:
        code = {}
    encoded = ''.join(code[ch] for ch in text)
    padding = (8 - len(encoded) % 8) % 8
    encoded += '0' * padding
    b = bytearray()
    for i in range(0, len(encoded), 8):
        b.append(int(encoded[i:i+8], 2))
    return bytes(b), code, padding

def huffman_decode(data: bytes, codes: Dict[str, str], padding: int) -> str:
    inv_codes = {v: k for k, v in codes.items()}
    bits = ''.join(f'{byte:08b}' for byte in data)
    if padding:
        bits = bits[:-padding]
    res = []
    code = ''
    for bit in bits:
        code += bit
        if code in inv_codes:
            res.append(inv_codes[code])
            code = ''
    return ''.join(res) 