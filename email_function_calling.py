import os
import json
import requests
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
class SkillFunctions(Enum):
  SendEmail = 'send_email'

def run_conversation():
  MODEL = "gpt-3.5-turbo-0613"
  response = openai.ChatCompletion.create(
    model=MODEL,
    messages=[
      {"role": "user", "content": "给明广这个人发个邮件，告诉他晚上记得早点睡觉，晚安！说的好听一些，最好能写一首诗送给他让他做个好梦"},
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
              "description": "收件人名字即可",
            },
            "content": {"type": "string", "description": "邮件的内容"},
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

      if function_name == SkillFunctions.SendEmail.value:
          email_info = send_email(
              receiver=arguments.get('receiver'),
              content=arguments.get('content')
          )
          print(email_info)
          send_email_action(**email_info)
          print('邮件已发送')

run_conversation()
