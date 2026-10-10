import os

from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

messages = [{"role": "system", "content": "You are a helpful assistant"}]
print("AI助手已启动！输入 exit 结束对话…\n")

while True:
    user_input = input("你:").strip()

   
    if user_input.lower() in {"exit", "quit"}:
        print("再见！")
        break

    if not user_input:
        continue

    messages.append({"role": "user", "content": user_input})
    print("正在思考中…")

    try:
        response = client.chat.completions.create(
            model="deepseek-flash",
            messages=messages,
            stream=False,
            reasoning_effort="high",
            extra_body={"thinking": {"type": "enabled"}},
        )
    except Exception as exc:
        messages.pop()
        print(f"请求失败：{exc}\n")
        continue

    ai_reply = response.choices[0].message.content
    print(f"AI助手:{ai_reply}\n")
    messages.append({"role": "assistant", "content": ai_reply})
