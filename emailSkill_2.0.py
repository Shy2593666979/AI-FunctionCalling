import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr

# 发送邮件操作
my_sender = '2593666979@qq.com'  # 发件人邮箱账号
my_pass = 'xxxxxxxxxxxxx'  # 发件人邮箱密码
my_user = ["2593666979@qq.com"]  # 收件人邮箱账号


def send_email_action(receiver, content):
    if not receiver: return
    # 邮件配置
    smtp_server = "smtp.qq.com"
    smtp_port = 465
    sender_email = "2593666979@qq.com"
    receiver_email = receiver
    password = "xxxxxxxxxxx"

    # 构建邮件内容
    message = MIMEMultipart() 
    message["From"] = Header('AI <%s>' % sender_email)
    message["To"] = receiver_email
    message["Subject"] = "我是您的AI助理，您有一封邮件请查看"

    body = content
    message.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465
    server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
    server.sendmail(my_sender, [receiver_email,], message.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
    server.quit()  # 关闭连接


# 供Function Calling使用的输出处理函数
def send_email(receiver, content=''):
    # 通讯录
    Contact = {
        "二鹏": "1692534832@qq.com",
        "小田": "2490139200@qq.com",
        "小魏": "2964985343@qq.com",
        "明广": "2593666979@qq.com",
        "二胖": "2652958667@qq.com",
        "汉宏": "3154203631@qq.com",
        "大头": "1729188963@qq.com",
        "传词": "1175783304@qq.com",
    }

    email_info = {
        "receiver": Contact[receiver],
        "content": content
    }

    return email_info
