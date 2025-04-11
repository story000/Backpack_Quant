import requests
import os
import time
import base64
import nacl.signing

def generate_signature(private_key, request_body, timestamp, window=5000):
    sorted_params = '&'.join(f"{key}={value}" for key, value in sorted(request_body.items()))
    
    # 生成签名字符串
    signing_string = f"instruction=balanceQuery&timestamp={timestamp}&window={window}"
    
    # 使用 ED25519 签名
    signing_key = nacl.signing.SigningKey(private_key, encoder=nacl.encoding.Base64Encoder)
    signed_message = signing_key.sign(signing_string.encode())
    
    # 返回 base64 编码的签名
    return base64.b64encode(signed_message.signature).decode()

def signed_request(url, request_body, api_key, private_key):
    timestamp = int(time.time() * 1000)  # 获取当前时间戳（毫秒）
    window = 5000  # 默认时间窗口

    # 生成签名
    signature = generate_signature(private_key, request_body, timestamp, window)

    headers = {
        "X-Timestamp": str(timestamp),
        "X-Window": str(window),
        "X-API-Key": api_key,
        "X-Signature": signature
    }

    response = requests.post(url, json=request_body, headers=headers)
    return response

def fetch_assets():
    url = os.getenv("BACKPACK_API_URL") + "/api/v1/capital"
    response = signed_request(url, {}, os.getenv("BACKPACK_API_KEY"), os.getenv("BACKPACK_API_SECRET"))
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"请求失败，状态码: {response.status_code}")

assets = fetch_assets()
print(assets)
