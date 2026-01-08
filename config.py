# 请求参数
TARGET_URL="https://jw.ruc.edu.cn/resService/jwxtpt/v1/xsd/cjgl_xsxdsq/findKccjList?resourceCode=XSMH0526&apiCode=jw.xsd.xsdInfo.controller.CjglKccjckController.findKccjList"

# 基础请求头（不包含Cookie和TOKEN，这些会动态更新）
BASE_HEADERS={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Host": "jw.ruc.edu.cn",
    "Origin": "https://jw.ruc.edu.cn",
    "Referer": "https://jw.ruc.edu.cn/Njw2017/index.html",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Simulated-By": "",
    "X-Requested-With": "XMLHttpRequest",
    "app": "PCWEB",
    "locale": "zh_CN",
    "sec-ch-ua": "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "userRoleCode": "student"
}

PAYLOAD={"pyfa007id":"1","jczy013id":[],"fxjczy005id":"","cjckflag":"xsdcjck","kthList":[],"page":{"pageIndex":1,"pageSize":30,"orderBy":"[{\"field\":\"jczy013id\",\"sortType\":\"asc\"}]","conditions":"QZDATASOFTJddJJVIJY29uZGl0aW9uR3JvdXAlMjIlM0ElNUIlN0IlMjJsaW5rJTIyJTNBJTIyYW5kJTIyJTJDJTIyY29uZGl0aW9uJTIyJTNBJTVCJTVEJTdEyTTECTLE"}}

# 动态Cookie和Token（将在运行时更新）
HEADERS = BASE_HEADERS.copy()

def update_headers(cookies, debug=False):
    """根据cookies更新HEADERS中的Cookie和TOKEN"""
    global HEADERS
    HEADERS = BASE_HEADERS.copy()

    # 构建Cookie字符串
    cookie_parts = []

    # jw domain的cookies包含SESSION和token
    # 从v domain获取的cookies可能包含authcode
    if 'authcode' in cookies:
        cookie_parts.append(f"authcode={cookies['authcode']}")
    if 'SESSION' in cookies:
        cookie_parts.append(f"SESSION={cookies['SESSION']}")

    if cookie_parts:
        HEADERS['Cookie'] = '; '.join(cookie_parts)
    elif 'Cookie' not in HEADERS or not HEADERS['Cookie']:
        # 如果没有SESSION cookie，尝试使用原始的cookie字符串
        if isinstance(cookies, str):
            HEADERS['Cookie'] = cookies
        elif cookies:
            # 如果cookies是dict，尝试构建cookie字符串
            HEADERS['Cookie'] = '; '.join([f"{k}={v}" for k, v in cookies.items()])

    # 设置TOKEN
    if 'token' in cookies:
        HEADERS['TOKEN'] = cookies['token']

    # Debug输出
    if debug:
        print("\n=== Debug: Cookie和Token信息 ===")
        print(f"Cookies: {cookies}")
        print(f"Cookie Header: {HEADERS.get('Cookie', 'NOT SET')}")
        print(f"TOKEN Header: {HEADERS.get('TOKEN', 'NOT SET')}")
        print("================================\n")

# PUSHPLUS 令牌 (在 pushplus.plus 网站获取)
YOUR_TOKEN="e5a5198ce0a84c17b7846a8fcac36c6e"
