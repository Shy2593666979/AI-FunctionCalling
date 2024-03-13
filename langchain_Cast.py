from langchain.utilities import SerpAPIWrapper
from langchain_experimental.tools.python.tool import PythonAstREPLTool
from langchain.utilities import ArxivAPIWrapper
from langchain.utilities import OpenWeatherMapAPIWrapper
from typing import Dict, Tuple
import os
import json
import torch
import requests
import re
from emailSkill import send_email, send_email_action
from sentence_transformers.models import tokenizer
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from transformers.generation import GenerationConfig

total_users = ["二鹏", "小田", "小魏", "明广", "二胖", "汉宏", "大头", "传词"]

os.environ['SERPAPI_API_KEY'] = 'cdc3b207606843b4c883849c3a0f833c13057811bea964bef192707d8845f3d8'
os.environ["OPENWEATHERMAP_API_KEY"] = "843549913c1d5d4e2d95f865ea1ae1e7"

"""
tokenizer = AutoTokenizer.from_pretrained("/model/base_model/qwen/Qwen-72B-Chat", trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained("/model/base_model/qwen/Qwen-72B-Chat",
                                         device_map="auto",
                                         trust_remote_code=True).eval()
model.generation_config = GenerationConfig.from_pretrained("/model/base_model/qwen/Qwen-72B-Chat", trust_remote_code=True) # 可指定不同的生成长度、top_p等相关超参
model.eval()
"""


search = SerpAPIWrapper()
arxiv = ArxivAPIWrapper()
python = PythonAstREPLTool()
weather = OpenWeatherMapAPIWrapper()


def tool_wrapper_for_qwen(tool):
    def tool_(query):
        query = json.loads(query)["query"]
        return tool.run(query)

    return tool_


def chat_qwen_72B(prompt):
    """
    此处需要一些Qwen用户的隐私信息，所以隐藏了
    """
    return str(response, encoding='utf-8')


TOOLS = [
    {
        'name_for_human':
            'google search',
        'name_for_model':
            'Search',
        'description_for_model':
            'useful for when you need to answer questions about current events.',
        'parameters': [{
            "name": "query",
            "type": "string",
            "description": "search query of google",
            'required': True
        }],
        'tool_api': tool_wrapper_for_qwen(search)
    },
    {
        'name_for_human':
            'Weather search',
        'name_for_model':
            'Weather',
        'description_for_model':
            'Get the current weather in a given location.',
        'parameters': [{
            "name": "query",
            "type": "string",
            "description": "Search for the current weather for the location in question",
            'required': True
        }],
        'tool_api': tool_wrapper_for_qwen(weather)
    },
    {
        'name_for_human':
            'arxiv',
        'name_for_model':
            'Arxiv',
        'description_for_model':
            'A wrapper around Arxiv.org Useful for when you need to answer questions about Physics, Mathematics, Computer Science, Quantitative Biology, Quantitative Finance, Statistics, Electrical Engineering, and Economics from scientific articles on arxiv.org.',
        'parameters': [{
            "name": "query",
            "type": "string",
            "description": "the document id of arxiv to search",
            'required': True
        }],
        'tool_api': tool_wrapper_for_qwen(arxiv)
    },
    {
        'name_for_human':
            'python',
        'name_for_model':
            'python',
        'description_for_model':
            "A Python shell. Use this to execute python commands. When using this tool, sometimes output is abbreviated - Make sure it does not look abbreviated before using it in your answer. "
            "Don't add comments to your python code.",
        'parameters': [{
            "name": "query",
            "type": "string",
            "description": "a valid python command.",
            'required': True
        }],
        'tool_api': tool_wrapper_for_qwen(python)
    },
    {
        'name_for_human':
            'send email',
        'name_for_model':
            'Send Email',
        'description_for_model':
            'A tool for sending email messages.',
        'parameters': [{
            "name": "receiver",
            "type": "string",
            "description": "The person who received the email message",
            'required': True
        },
            {
                "name": "content",
                "type": "string",
                "description": "Email information to be sent",
                'required': True
            }
        ]
    },
    {
        'name_for_human':
            'run shell',
        'name_for_model':
            'run shell',
        'description_for_model':
            'A tool for executing shell commands.',
        'parameters': [{
            "name": "content",
            "type": "string",
            "description": "An executable shell command",
            'required': True
        }
        ]
    }

]

TOOL_DESC = """{name_for_model}: Call this tool to interact with the {name_for_human} API. What is the {name_for_human} API useful for? {description_for_model} Parameters: {parameters} Format the arguments as a JSON object."""

REACT_PROMPT = """Answer the following questions as best you can. You have access to the following tools:

{tool_descs}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can be repeated zero or more times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {query}"""


def build_planning_prompt(TOOLS, query):
    tool_descs = []
    tool_names = []
    for i in range(len(TOOLS)):
        info = TOOLS[i]
        tool_descs.append(
            TOOL_DESC.format(
                name_for_model=info['name_for_model'],
                name_for_human=info['name_for_human'],
                description_for_model=info['description_for_model'],
                parameters=json.dumps(
                    info['parameters'], ensure_ascii=False),
            )
        )
        tool_names.append(info['name_for_model'])

    tool_descs = '\n\n'.join(tool_descs)
    tool_names = ','.join(tool_names)

    prompt = REACT_PROMPT.format(tool_descs=tool_descs, tool_names=tool_names, query=query)
    return prompt


"""
stop = ["Observation:", "Observation:\n"]
react_stop_words_tokens = [tokenizer.encode(stop_) for stop_ in stop]
"""


def parse_latest_plugin_call(text: str) -> Tuple[str, str]:
    i = text.rfind('\nAction:')
    j = text.rfind('\nAction Input:')
    k = text.rfind('\nObservation:')
    if 0 <= i < j:  # If the text has `Action` and `Action input`,
        if k < j:  # but does not contain `Observation`,
            # then it is likely that `Observation` is ommited by the LLM,
            # because the output text may have discarded the stop word.
            text = text.rstrip() + '\nObservation:'  # Add it back.
            k = text.rfind('\nObservation:')
    if 0 <= i < j < k:
        plugin_name = text[i + len('\nAction:'):j].strip()
        plugin_args = text[j + len('\nAction Input:'):k].strip()
        return plugin_name, plugin_args

    return '', ''

def email_receiver(action_input):

    # print("-------------------type--------------" + type(action_input))
    action_input_json = json.loads(action_input)
    result_receiver = action_input_json['receiver']
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
    model_content = action_input_json['content'].replace("\n", "")
    matches = re.findall(pattern, model_content)

    print("------------------GPT function calling后返回的收件人和收件信息-------------------")
    print(action_input_json['receiver'])
    print(action_input_json['content'])

    # 保存结果

    print(matches)
    for match in matches:
        result_content.append("亲爱的" + match[0])

    return result_user,result_content


def send_to_email(result_user,result_content):
    for i in range(len(result_user)):
        email_info = send_email(
            receiver=result_user[i],
            content=result_content[i]
        )
        print(email_info)
        send_email_action(**email_info)
        print(result_user[i] + '的邮件已发送')

def use_api(tools, response):
    use_toolname, action_input = parse_latest_plugin_call(response)
    if use_toolname == "":
        return "no tool founds", "no tool founds"

    used_tool_meta = list(filter(lambda x: x["name_for_model"] == use_toolname, tools))
    if len(used_tool_meta) == 0:
        return "no tool founds", "no tool founds"
    if use_toolname == 'Send Email':

        return "send email", "send email Successful"
    else:
        api_output = used_tool_meta[0]["tool_api"](action_input)
        return use_toolname, api_output


def run_conversation(prompt):
    use_function = True  # 判断是否使用function

    prompt_1 = build_planning_prompt(TOOLS[0:6], query=prompt)
    print(prompt_1)

    response_1 = chat_qwen_72B(prompt_1)
    print(response_1)

    response_1 = json.loads(response_1)
    message = response_1["choices"][0]["message"]

    api_tool, api_output = use_api(TOOLS, message["content"])

    print("-----------------------api_output---------------------")
    print(api_output)

    if api_tool == "no tool founds":
        return False, "no tool founds"
    elif api_tool == "send email":
        return use_function, "send email Successful"
    else:
        """
        # 第二次调用模型，将第一次模型的输入以及工具的输出全部拼接
        prompt_2 = str(prompt_1) + '\n' + str(message["content"]) + ' ' + str(api_output)

        stop = ["Observation:", "Observation:\n"]
        react_stop_words_tokens = [tokenizer.encode(stop_) for stop_ in stop]

        response_2 = chat_qwen_72B(prompt_2)
        print(prompt_2, "\n", response_2)

        response_2 = json.loads(response_2)

        text = response_2["choices"][0]["message"]["content"]
        """
        text = message["content"]

        start_marker = "Final Answer: "

        start_index = text.find(start_marker) + len(start_marker)
        final_answer = text[start_index:]

        return use_function, final_answer

# run_conversation(prompt)
