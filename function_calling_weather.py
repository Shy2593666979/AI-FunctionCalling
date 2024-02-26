import os
import json
import requests
import re
from enum import Enum
from emailSkill import send_email, send_email_action
from googleapiclient.discovery import build
import openai

openai.api_key = "sk-NYsoG3VBKDiTuvdtC969F95aFc4f45379aD3854a93602327"
openai.api_base = "https://key.wenwen-ai.com/v1"
weather_key = "fac0ad465078da96a3ec6ba1ccc6746f"
os.environ['SERPAPI_API_KEY'] = 'cdc3b207606843b4c883849c3a0f833c13057811bea964bef192707d8845f3d8'
weather_url = 'https://restapi.amap.com/v3/weather/weatherInfo?parameters'

total_users = ["二鹏", "小田", "小魏", "明广", "二胖", "汉宏", "大头", "传词"]

prompt = "先查询今天郑州市的天气情况，再然后将这个天气情况发送到姓名叫做明广的邮箱里，要使用亲爱的xxx"

MODEL = "gpt-3.5-turbo-0613"

# MODEL = "Qwen"


def call_google(query: str, **kwargs):
    service = build(serviceName="customsearch",
                    version="v1",
                    developerKey='cdc3b207606843b4c883849c3a0f833c13057811bea964bef192707d8845f3d8',
                    static_discovery=False)

    res = service.cse().list(q=query, cx="01d8e4d716aae45db", **kwargs).execute()
    res_items = res["items"]
    res_snippets = [r['snippet'] for r in res_items]
    return res_snippets

def call_weather(location):

    params_realtime = {
        'key': weather_key,
        'city': location,
        'extensions': 'all'
    }

    res = requests.get(url=weather_url, params=params_realtime)
    weather = res.json()

    report_time = weather.get('forecasts')[0].get("reporttime")  # 获取发布数据时间
    date = weather.get('forecasts')[0].get("casts")[0].get('date')  # 获取日期
    day_weather = weather.get('forecasts')[0].get("casts")[0].get('dayweather')  # 白天天气现象
    night_weather = weather.get('forecasts')[0].get("casts")[0].get('nightweather')  # 晚上天气现象
    day_temp = weather.get('forecasts')[0].get("casts")[0].get('daytemp')  # 白天温度
    night_temp = weather.get('forecasts')[0].get("casts")[0].get('nighttemp')  # 晚上温度
    day_wind = weather.get('forecasts')[0].get("casts")[0].get('daywind')  # 白天风向
    night_wind = weather.get('forecasts')[0].get("casts")[0].get('nightwind')  # 晚上风向
    day_power = weather.get('forecasts')[0].get("casts")[0].get('daypower')  # 白天风力
    night_power = weather.get('forecasts')[0].get("casts")[0].get('nightpower')  # 晚上风力

    global prompt
    prompt += f"地点是{location}" + f"发布数据的时间{report_time}" + f"现在的日期是{date}" + f"白天天气现象{day_weather}" + f"晚上天气现象{night_weather}" + f"白天温度{day_temp}" + f"晚上温度{night_temp}" + f"白天风向{day_wind}" + f"晚上风向{night_wind}" + f"白天风力{day_power}" + f"晚上风力{night_power}"

    # weather_prompt += "请你根据这些信息给我回复当地的天气如何？说话要求温柔一些"
    # prompt += "将这些信息总结一下，然后发送到姓名叫做明广的邮箱里，要使用亲爱的xxx"
    messages = [{"role": "user", "content": prompt}, ]
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages,
        functions = function
    )
    return response

class SkillFunctions(Enum):
    SendEmail = 'send_email'
    Call_Google = 'call_google'
    Call_Weather = 'call_weather'

available_functions = {
    "call_google": call_google,
}

function = [
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
    },
    {
        "name": SkillFunctions.Call_Google.value,
        "description": "Use the Google Chrome questions about current events or something you are not sure",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "user's query for you to answer for",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": SkillFunctions.Call_Weather.value,
        "description": "Use this to check the weather conditions of the location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The location of the user's query",
                },
            },
            "required": ["location"],
        },
    }
]




def run_conversation():
    messages = [{"role": "user", "content": prompt}, ]
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages,
        functions=function,
        function_call="auto",
    )

    message = response["choices"][0]["message"]
    print(message)
    messages.append(message)

    if message.get("function_call"):
        function_name = message["function_call"]["name"]
        arguments = json.loads(message["function_call"]["arguments"])

        if function_name == SkillFunctions.SendEmail.value:
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
            # if function_name == SkillFunctions.SendEmail.value:
            for i in range(len(result_user)):
                email_info = send_email(
                    receiver=result_user[i],
                    content=result_content[i])
            print(email_info)
            send_email_action(**email_info)
            print(result_user[i] + '的邮件已发送')

        # 对用户的问题调用 Google Search
        elif function_name == SkillFunctions.Call_Google.value:

            function_name = message["function_call"]["name"]
            function_to_call = available_functions[function_name]

            function_args = json.loads(message["function_call"]["arguments"])
            function_response = function_to_call(query=function_args.get("query"))

            messages.append(
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                }
            )
            response = openai.ChatCompletion.create(
                model=MODEL,
                messages=messages,
                functions=function,
            )
            print(response["choices"][0]["message"]["content"])

        elif function_name == SkillFunctions.Call_Weather.value:

            response = call_weather(arguments.get('location'))
            print(response["choices"][0]["message"]["content"])
            run_conversation()


# def run_multiple_conversation():

run_conversation()
