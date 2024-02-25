import os
import json
import requests
import re
from enum import Enum
from emailSkill import send_email, send_email_action
import openai

# openai.api_key = 'sess-JZjXeK9HssgkW95Olv8THXMFLBOGaj4P7Ragza5e'
openai.api_key = "sk-NYsoG3VBKDiTuvdtC969F95aFc4f45379aD3854a93602327"
openai.api_base = "https://key.wenwen-ai.com/v1"

"""
client = OpenAI(
    # This is the default and can be omitted
    api_key = Api_key,
)
"""
total_users = ["二鹏", "小田", "小魏", "明广", "二胖", "汉宏", "大头", "传词"]


class SkillFunctions(Enum):
    SendEmail = 'send_email'


prompt = "给名字叫做明广和小田这两人发送邮件。亲切的告诉明广今天要加班和告诉小田该去吃饭了。格式使用亲爱的：xxx"


def run_conversation():
    MODEL = "gpt-3.5-turbo-0613"
    # MODEL = "Qwen"
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "user",
             "content": prompt
             },
        ],
        functions=[
            {
                "name": SkillFunctions.SendEmail.value,
                "description": "send email assistant",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "receiver": {
                            "type": "string",
                            "description": "收件人名字，收件人可能有多个，多个的话中间用 ',' 隔开 ",
                        },
                        "content": {"type": "string", "description": "邮件的内容，可能有多个收件人的邮件内容"},
                    },
                    "required": ["receiver", "content"],
                },
            }
        ],
        function_call="auto",
    )
    message = response["choices"][0]["message"]
    print(message)

    if message.get("function_call"):
        function_name = message["function_call"]["name"]
        arguments = json.loads(message["function_call"]["arguments"])

        result_receiver = arguments.get('receiver')

        # 检查信息中是否包含所有人名，并记录他们的位置
        positions = {name: result_receiver.find(name) for name in total_users}

        # 过滤掉文本中不存在的人名
        filtered_positions = {name: pos for name, pos in positions.items() if pos != -1}

        # 根据位置信息对人名进行排序
        result_user = sorted(filtered_positions, key=lambda k: filtered_positions[k])  # 保存本次发送信息的所有对象
        print(result_user)

        result_content = []  # 保存每个收件人需要收到的信息
        pattern = r'亲爱的(.*?)(?=(亲爱的|$))'  # 正则表达式取出每个收件人对应的信息
        # 使用re.findall来查找所有匹配项
        model_content = arguments.get('content').replace("\n", "")
        matches = re.findall(pattern, model_content)

        print("------------------GPT function calling后返回的收件人和收件信息-------------------")
        print(arguments.get('receiver'))
        print(arguments.get('content'))

        # 保存结果
        print(matches)
        for match in matches:
            result_content.append("亲爱的" + match[0])

        # 进行function calling
        if function_name == SkillFunctions.SendEmail.value:
            for i in range(len(result_user)):
                email_info = send_email(
                    receiver=result_user[i],
                    content=result_content[i]
                )
                print(email_info)
                send_email_action(**email_info)
                print(result_user[i] + '的邮件已发送')


run_conversation()
