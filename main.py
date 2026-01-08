import requests
import time
import os
import json
from config import TARGET_URL, HEADERS, PAYLOAD, YOUR_TOKEN

# 本地保存爬取到的课程成绩信息
DB_FILE = "page.json"

def send_pushplus_test(content, channel='wechat'):
    """
    发送 PushPlus 消息
    :param channel: 'wechat' (微信) 或 'mail' (邮件)
    """
    url = 'http://www.pushplus.plus/send'
    
    data = {
        "token": YOUR_TOKEN,
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
        response = requests.post(TARGET_URL, headers=HEADERS, json=PAYLOAD, timeout=5)
        response.encoding = 'utf-8'

        if response.status_code != 200:
            print(f"访问失败，状态码: {response.status_code}")
            return None, None

        if "登录" in response.text or "login" in response.url:
            print("Cookie 可能已过期，请重新获取！")
            send_pushplus_test("Cookie已过期，脚本停止监控，请更新Cookie。")
            return None, None

        response_data = response.json()

        if response_data.get('errorCode') != 'success':
            print(f"API 返回错误: {response_data.get('errorMessage')}")
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
        send_pushplus_test(msg)

        # 注意：DB_FILE 在 get_current_courses() 中已经自动更新了
    else:
        print(f"[{time.strftime('%H:%M:%S')}] 暂无新成绩...")

if __name__ == "__main__":
    while True:
        main()
        # 每 10 分钟 (600秒) 检查一次，太频繁会被封IP
        time.sleep(600)