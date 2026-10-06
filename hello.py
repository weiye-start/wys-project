import os
from openai import OpenAI

client = OpenAI(
    api_key= os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com")

user_input = input("What's your problem?")

response = client.chat.completions.create(
    model="deepseek-flash",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": user_input},
    ],
    stream = False,
    reasoning_effort="high",
    extra_body={"thinking":{"type":"enabled"}}
)

print(response.choices[0].message.content)

