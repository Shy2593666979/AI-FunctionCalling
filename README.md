# Function Calling

version 1.0 🔺

通过函数调用的方式可使Open AI 有了`自动发邮箱`的功能：

example QQ Email：

```python
server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465
server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
server.sendmail(my_sender, [receiver_email,], message.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
```
QQ Email授权码登录后连接Email Server

prompt:  "给小魏这个人发条消息，告诉小魏晚上记得吃饭，语言要求好听一些"

content："已经给小魏发送信息：亲爱的小魏，晚上记得按时吃饭。"



version 2.0 🔺

与 version 1.0不同的是，一个prompt可以`发送多个收件人不同的信息`

prompt："给二鹏、明广分别发送消息，告诉二鹏晚上记得按时吃饭，告诉明广晚上要加班，语言要求好听一些。"

content："二鹏消息已经发送：亲爱的二鹏，晚上记得按时吃饭。明广消息已发送：亲爱的明广，晚上要加班哦"

version 3.0 🔺

在 version 3.0的基础上增加了:（以langchain为基础进行的）

`自动发送邮件信息的多轮对话功能` AND `执行shell 命令的function`

如果用户的问题中没有明确收件人或者邮件内容，大模型会进入多轮对话状态进行多次询问，直到发送的信息满足你想法。

通过用户的问题中来明确需要执行的Shell命令，再通过选择的function在终端执行Shell 命令
```
question: 创建一个 a.txt 的文件

交给 chat_qwen() 进行询问，返回一个json格式数据

json["comment"] = "touch a.txt"

使用py执行comment对应的shell命令
```

-----------------------function calling 先告一段落---------------------👏
