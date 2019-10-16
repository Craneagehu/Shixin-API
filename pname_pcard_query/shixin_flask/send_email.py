#-*- coding:utf-8 -*-
import smtplib
from email.mime.text import MIMEText  # 用来创建文本格式的邮件体内容
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

class Send_Email:

    def __init__(self):
        self.smtp = self.get_conn()

    def get_conn(self):
        # 创建邮件对象
        smtp_obj = smtplib.SMTP_SSL('smtp.126.com', 465)
        # 登录邮箱
        smtp_obj.login("hu85650695@126.com", "huheling85650695")

        return smtp_obj

    def send_email(self,content):
        # 定义发送邮件的三要素
        sender = "hu85650695@126.com"
        receiver = "708881841@qq.com"
        # 获取发送邮件的 邮件体
        msg = self.get_msg(sender, receiver,content)
        # 发送邮件
        self.smtp.sendmail(from_addr=sender, to_addrs=receiver, msg=msg.as_string())
        print("send success")

    def get_msg(self, sender, receiver,content):
        # 定义邮件主题
        subject = "失信查询异常通知 "
        # 获取邮件体中的 文本内容（消息体）
        msg = MIMEText(content, "plain", "utf-8")
        # 生成邮件体的 三要素
        msg["From"] = sender
        msg["To"] = receiver
        msg["Subject"] = subject
        return msg

    def __del__(self):
        self.smtp.close()


if __name__ == "__main__":
    send = Send_Email()
    send.send_email('...')
