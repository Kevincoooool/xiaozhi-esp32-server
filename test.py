import requests
import json

class CozeAPI:
    def __init__(self, api_token, bot_id, api_base="https://api.coze.cn/open_api/v2"):
        self.api_token = api_token
        self.bot_id = bot_id
        self.api_base = api_base

    def chat_stream(self, user, query, conversation_id="123"):
        url = f"{self.api_base}/chat"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "Accept": "*/*"
        }
        # 在 query 前添加中文提示，确保回复为中文
        modified_query = f"请用中文回答：{query}"
        payload = {
            "conversation_id": conversation_id,
            "bot_id": self.bot_id,
            "user": user,
            "query": modified_query,
            "stream": True
        }
        response = requests.post(url, headers=headers, json=payload, stream=True)
        if response.status_code != 200:
            raise Exception(f"请求失败: {response.status_code} {response.text}")

        for line in response.iter_lines(decode_unicode=True):
            if line:
                if line.startswith("data:"):
                    data_str = line[len("data:"):].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        # 如果返回内容存在，尝试重新编码修正乱码
                        if "message" in data and "content" in data["message"]:
                            content = data["message"]["content"]
                            try:
                                # 将错误解码的字符串先编码为 latin1，再用 utf-8 解码
                                decoded_content = content.encode("latin1").decode("utf8")
                                data["message"]["content"] = decoded_content
                            except Exception as e:
                                # 如果转换失败，保持原样
                                pass
                        yield data
                    except json.JSONDecodeError:
                        yield data_str


if __name__ == "__main__":
    # 请将以下 API_TOKEN 与 BOT_ID 替换成你自己的值
    API_TOKEN = "pat_RsytD2BcuhFNiOfS626QoTyVp4Wj6kVcGQxY8KvvZFzlGrrmxLkrMIUQ4YtlYXOr"
    BOT_ID = "7471518435345121321"
    USER = "7455669479939473462"  # 用户标识（可自定义）
    QUERY = "你好，你是谁？"

    coze = CozeAPI(API_TOKEN, BOT_ID)
    print("开始流式调用 Coze API：")
    # 调用 chat_stream 方法，并实时输出返回的每一块数据
    for chunk in coze.chat_stream(USER, QUERY):
        print(chunk)
