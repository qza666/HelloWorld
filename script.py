import random
import string
import requests
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial
import asyncio
from Hello_World import mains

# 创建全局 session 以便复用连接
session = requests.Session()

def get_random_port():
    return random.randint(30000, 32999)

# 综合请求
def make_request(method, url, **kwargs):
    proxies = {
        'http': 'http://127.0.0.1:823',
        'https': 'http://127.0.0.1:823',
    }
    try:
        if url == "https://api-console.helloworldtranslate.com/api/v1/console/user/send/code" or url == "https://api-console.helloworldtranslate.com/api/v1/console/user/register":
            response = session.request(method, url, timeout=5, proxies=proxies, **kwargs)
            #print(f"请求成功: {response.text}")
        else:
            response = session.request(method, url, timeout=5, **kwargs)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        #print(f"请求失败: {e}")
        return None

get = partial(make_request, 'GET')
post = partial(make_request, 'POST')

# 随机邮箱生成
def random_email():
    return f"{''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(10, 15)))}@{random.choice(['nqmo.com', 'qabq.com', 'end.tw', 'uuf.me', 'yzm.de'])}"

# 获取邮箱auth_token
def get_email_info():
    email = random_email()
    response = get(f"https://mail.td/zh/mail/{email}")
    if response:
        auth_token = response.headers.get('Set-Cookie', '').split('auth_token=')[1].split(';')[0]
        return email, auth_token, email.split('@')[0]
    return None

# 通用请求头
def api_request(url, payload):
    return post(url, json=payload, headers={'Content-Type': "application/json"})

# 发送注册请求验证码
def send_email_code(email, username):
    payload = {"userName": username, "passWord": username, "passWord1": username, "email": email}
    return api_request("https://api-console.helloworldtranslate.com/api/v1/console/user/send/code", payload)

# 获取收到的验证码
def fetch_email_code(email, auth_token):
    headers = {'authorization': f"bearer {auth_token}"}
    retries = 0
    while retries < 100:  # 限制重试次数
        response = get(f"https://mail.td/api/api/v1/mailbox/{email}", headers=headers)
        if response:
            for mail in response.json():
                if 'id' in mail:
                    code_response = get(f"https://mail.td/api/api/v1/mailbox/{email}/{mail['id']}", headers=headers)
                    if code_response:
                        match = re.search(r'\b[A-Za-z0-9]{6}\b', code_response.json()["body"]["text"])
                        if match:
                            return match.group()
        retries += 1
        time.sleep(0.5)  # 更短的时间间隔
    return None

# 登录账号获取Hello world的token
def register_and_login(code, email, username):
    #提交注册请求
    register_payload = {"userName": username, "passWord": username, "passWord1": username, "code": code, "email": email, "type": 1}
    login_api = api_request("https://api-console.helloworldtranslate.com/api/v1/console/user/register", register_payload)
    if login_api:
        login_response = post("https://edgeone-api.helloworld88.com/login", data={'userName': username, 'passWord': username})
        if login_response and login_response.json().get('code') == 200:
            return login_response.json().get('token')
    return None

# 注册并获取token的异步任务
def register_task():
    email_info = get_email_info()
    if not email_info:
        print("随机邮箱生成失败")
        return None

    email, auth_token, username = email_info
    #print(email)
    if not send_email_code(email, username):
        print(f"{username}: 验证码发送失败")
        return None

    code = fetch_email_code(email, auth_token)
    if not code:
        print(f"{username}: 验证码解析失败")
        return None

    token = register_and_login(code, email, username)
    if not token:
        print(f"{username}: 注册或登录失败")
        return None
    
    print(f"{username}: 注册成功，token: {token}")
    # 调用异步函数，确保正确使用 asyncio.run
    asyncio.run(mains(token))

def main():
    max_workers = 10  # 定义线程池中的最大线程数，根据需求调整
    tasks = []

    # 创建线程池
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        while True:
            # 提交任务到线程池
            for _ in range(max_workers):
                tasks.append(executor.submit(register_task))

            time.sleep(0.1)

if __name__ == "__main__":
    main()
