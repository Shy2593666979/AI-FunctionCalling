import json

from flask import Flask
from flask import request
from flask import jsonify
from function_calling_Cast import chat_qwen_72B, TOOLS, build_planning_prompt, send_to_email, email_receiver
from function_calling_Cast import parse_latest_plugin_call
from run_shell import run_Shell

is_send_email = False
prompt_send_email = ""
user_receiver = ""
user_content = ""

app = Flask(__name__)


@app.route('/function', methods=['POST'])
def function():
    global prompt_send_email
    global is_send_email
    global user_receiver
    global user_content

    data = request.get_data()
    json_data = json.loads(data)

    question = json_data['data']['question']
    # use_functions,result = run_conve::wqrsation(question)

    if is_send_email and question != "发送" and question != "退出":
        question = prompt_send_email + question

    prompt_1 = build_planning_prompt(TOOLS[0:6], query=question)
    print(prompt_1)

    response_1 = chat_qwen_72B(prompt_1)
    print(response_1)

    response_1 = json.loads(response_1)
    message = response_1["choices"][0]["message"]

    if is_send_email:

        print("is_send_email ======================= True")

        api_tool, api_output = parse_latest_plugin_call(message["content"])
        if question == "发送":
            # user, content = email_receiver(api_output)
            send_to_email(user_receiver,user_content)
            prompt_send_email = ""
            is_send_email = False

            pmt = "邮件已发送，请问还有什么帮助你的？"
            response = {"code": 200, "message": "success", 'use_function': True, 'result': pmt}
            return jsonify(response)
        elif question == "退出":

            prompt_send_email = ""
            is_send_email = False

            # 收件人和邮件内容
            user_content = ""
            user_receiver = ""

            pmt = "退出成功，请问还有什么帮助你的？"
            response = {"code": 200, "message": "success", 'use_function': True, 'result': pmt}
            return jsonify(response)
        else:
            # 用户输入的其他信息
            user, content = email_receiver(api_output)
            result = "请确认收件人和邮件信息是否无误： \n收件人：" + str(user) +  "\n 邮件内容：" +  str(content) + "\n" + "\n如果正确请输入：发送\n" + "取消发送请输入：退出"
            if len(user) == 0 and len(content) == 0:
                result = "非常抱歉，我未能理解您要想要发送邮件的收件人和邮件内容.\n您可以说的清楚一些吗？"
            elif len(user) == 0 and len(content) != 0:
                result = "非常抱歉，目前我已经知道您想要发送的邮件内容是" + str(content) + ",但是我没有理解您想要发送的收件人姓名是谁？\n您可以说的清楚一些吗？"
            elif len(user) != 0 and len(content) == 0:
                result = "非常抱歉，目前我已经知道您想要发送邮件的收件人是" + str(user) + ",但是我没有理解您想要发送的邮件内容是什么？\n您可以说的清晰一点吗?"
            response = {"code": 200, "message": "success", 'use_function': True, 'result': result}

            user_receiver = user
            user_content = content

            prompt_send_email = question + "，"
            return jsonify(response)
    else:
        print("is_send_email ========================= False")
        api_tool, api_output = parse_latest_plugin_call(message["content"])
        if api_tool == "Send Email":
            is_send_email = True
            user, content = email_receiver(api_output)
            result = "请确认收件人和邮件信息是否无误： \n收件人：" + str(user) +  "\n 邮件内容：" +  str(content) + "\n" + "\n如果正确请输入：发送\n" + "取消发送请输入：退出"
            if len(user) == 0 and len(content) == 0:
                result = "非常抱歉，我未能理解您要想要发送邮件的收件人和邮件内容.\n您可以说的清楚一些吗？"
            elif len(user) == 0 and len(content) != 0:
                result = "非常抱歉，目前我已经知道您想要发送的邮件内容是" + str(content) + ",但是我没有理解您想要发送的收件人姓名是谁？\n您可以说的清楚一些吗？"
            elif len(user) != 0 and len(content) == 0:
                result = "非常抱歉，目前我已经知道您想要发送邮件的收件人是" + str(user) + ",但是我没有理解您想要发送的邮件内容是什么？\n您可以说的清晰一点吗?"
            response = {"code": 200, "message": "success", 'use_function': True, 'result': result}

            # 收件人和邮件内容
            user_receiver = user
            user_content = content

            prompt_send_email = question + "，"
            return jsonify(response)

        elif api_tool == "no tool founds":

            response = {"code": 200, "message": "success", 'no_function': True, 'question': question}
            return jsonify(response)
        elif api_tool == "run shell":

            print("\nshell ---------------------------------------- " + message["content"] + "\n")
            action_input_json = json.loads(api_output)
            shell_command = action_input_json['content']

            shell_answer = run_Shell(shell_command)

            text = message["content"]

            start_marker = "Final Answer: "

            start_index = text.find(start_marker) + len(start_marker)
            final_answer = text[start_index:]

            result = final_answer

            if shell_answer != "":
                result = shell_answer

            response = {"code": 200, "message": "success", 'use_function': True, 'result': result}
            return jsonify(response)
        else:
            text = message["content"]

            start_marker = "Final Answer: "
            start_index = text.find(start_marker) + len(start_marker)
            final_answer = text[start_index:]

            response = {"code": 200, "message": "success", 'use_function': True, 'result': final_answer}
            return jsonify(response)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5500)
