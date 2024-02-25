# Function Calling

通过函数调用的方式可使Open AI 有了自动发邮箱的功能：

example QQ Email：

```python
server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465
server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
server.sendmail(my_sender, [receiver_email,], message.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
```
QQ Email授权码登录后连接Email Server

version 1.0 🔺

prompt : "给小魏这个人发条消息，告诉小魏晚上记得吃饭，语言要求好听一些"

content ： "已经给小魏发送信息：亲爱的小魏，晚上记得按时吃饭。"



version 2.0 🔺

与 version 1.0不同的是，一个prompt可以发送多个收件人不同的信息

prompt: "给二鹏、明广分别发送消息，告诉二鹏晚上记得按时吃饭，告诉明广晚上要加班，语言要求好听一些。"

content ： "二鹏消息已经发送：亲爱的二鹏，晚上记得按时吃饭。明广消息已发送：晚上要加班哦"

