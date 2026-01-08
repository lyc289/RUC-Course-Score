import requests
import time
import os
import json
import config
from ruclogin import get_cookies, check_cookies

# 本地保存爬取到的课程成绩信息
DB_FILE = "page.json"

def ensure_cookies_valid():
    """确保Cookie和Token有效，如果无效则自动重新获取"""
    try:
        # 尝试从缓存文件读取cookies
        cookies = get_cookies(cache=True, domain="jw")

        # 验证cookies是否有效
        msg = check_cookies(cookies, domain="jw")
        if msg:
            print(f"Cookie验证成功: {msg}")
            config.update_headers(cookies)
            return True
        else:
            for _ in range(3):
                print("缓存的Cookie已失效，正在重新获取...", f"{_+1}/3")
                cookies = get_cookies(cache=False, domain="jw")
                msg = check_cookies(cookies, domain="jw")
                if msg:
                    print(f"重新获取Cookie成功: {msg}")
                    config.update_headers(cookies)
                    return True
            print("❌ Cookie获取失败，请检查config.ini中的用户名和密码")
            return False
    except Exception as e:
        print(f"❌ Cookie获取过程出错: {e}")
        print("正在尝试重新获取Cookie...")
        try:
            for _ in range(3):
                print("正在尝试重新获取Cookie...", f"{_+1}/3")
                cookies = get_cookies(cache=False, domain="jw")
                msg = check_cookies(cookies, domain="jw")
                if msg:
                    print(f"重新获取Cookie成功: {msg}")
                    config.update_headers(cookies)
                return True
            else:
                print("❌ Cookie获取失败，请检查config.ini中的用户名和密码")
                return False
        except Exception as e2:
            print(f"❌ Cookie获取失败: {e2}")
            return False

def send_pushplus(content, channel='wechat'):
    """
    发送 PushPlus 消息
    :param channel: 'wechat' (微信) 或 'mail' (邮件)
    """
    url = 'http://www.pushplus.plus/send'

    data = {
        "token": config.YOUR_TOKEN,
        "title": "成绩监控通知",  # 标题
        "content": content,              # 内容
        "channel": channel,              # !!! 核心参数: 决定发给微信还是邮件 !!!
        "template": "html"               # 消息模板，推荐用 html
    }

    try:
        response = requests.post(url, json=data)
        res_json = response.json()

        if res_json.get('code') == 200:
            print(f"✅ [{channel}] 发送成功！请检查你的手机/邮箱。")
        else:
            print(f"❌ [{channel}] 发送失败，原因: {res_json.get('msg')}")

    except Exception as e:
        print(f"❌ [{channel}] 请求报错: {e}")

def get_current_courses():
    """爬取并解析当前课程列表"""
    try:
        # 确保Cookie有效
        if not ensure_cookies_valid():
            return None, None

        response = requests.post(config.TARGET_URL, headers=config.HEADERS, json=config.PAYLOAD, timeout=5)
        response.encoding = 'utf-8'

        if response.status_code != 200:
            print(f"访问失败，状态码: {response.status_code}")
            return None, None

        if "登录" in response.text or "login" in response.url:
            print("Cookie 可能已过期，请重新获取！")
            send_pushplus("Cookie已过期，脚本停止监控，请更新Cookie。")
            return None, None

        response_data = response.json()

        if response_data.get('errorCode') != 'success':
            print(f"API 返回错误: {response_data.get('errorMessage')}")
            # 如果是认证错误，尝试重新获取Cookie
            if '登录' in response_data.get('errorMessage', '') or '认证' in response_data.get('errorMessage', ''):
                print("检测到认证错误，尝试重新获取Cookie...")
                if ensure_cookies_valid():
                    # 重新发送请求
                    response = requests.post(config.TARGET_URL, headers=config.HEADERS, json=config.PAYLOAD, timeout=5)
                    response.encoding = 'utf-8'
                    response_data = response.json()
                    if response_data.get('errorCode') != 'success':
                        print(f"重新获取Cookie后仍然失败: {response_data.get('errorMessage')}")
                        return None, None
                else:
                    return None, None
            return None, None

        courses = response_data.get('data', [])

        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(response_data, f, ensure_ascii=False, indent=2)

        course_ids = {course['kth'] for course in courses}
        return courses, course_ids

    except Exception as e:
        print(f"爬取过程出错: {e}")
        return None, None

def main():
    print("开始监控成绩...")

    # 首先确保Cookie有效
    print("正在验证Cookie...")
    if not ensure_cookies_valid():
        print("❌ Cookie 多次验证失败，无法继续监控")
        return

    # 1. 读取历史记录
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            file_content = json.load(f)
            # 使用课程的唯一标识符 kth 来比较
            old_course_ids = {course['kth'] for course in file_content['data']}
    else:
        old_course_ids = set()
        print("初始化：首次运行，将保存当前所有课程作为基准。")

    # 2. 获取当前课程（返回完整信息和ID集合）
    current_courses, current_course_ids = get_current_courses()

    if current_courses is None:
        return # 爬取失败，跳过本次

    # 3. 比较差异，找出新课程的ID
    new_course_ids = current_course_ids - old_course_ids

    if new_course_ids:
        # 根据ID获取新课程的完整信息
        new_courses = [course for course in current_courses if course['kth'] in new_course_ids]

        # 格式化通知消息
        msg_parts = []
        for course in new_courses:
            course_info = f"课程名称：{course['kcname']}\n"
            course_info += f"成绩：{course['zcj']}\n"
            course_info += f"学分：{course['xf']}\n"
            course_info += f"学期：{course['xnxq']}\n"
            course_info += "-" * 30
            msg_parts.append(course_info)

        msg = f"发现 {len(new_courses)} 门新课程出分：\n\n" + "\n".join(msg_parts)
        print(msg)

        # 4. 发送通知（可以在这里访问所有课程信息）
        send_pushplus(msg)

        # 注意：DB_FILE 在 get_current_courses() 中已经自动更新了
    else:
        print(f"[{time.strftime('%H:%M:%S')}] 暂无新成绩...")

if __name__ == "__main__":
    while True:
        main()
        # 每 10 分钟 (600秒) 检查一次，太频繁会被封IP
        time.sleep(600)
