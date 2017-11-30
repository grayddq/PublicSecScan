# -*- coding: utf-8 -*-
import smtplib
from config import *
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

NAME, VERSION, AUTHOR, LICENSE = "PublicSecScan", "V0.1", "咚咚呛", "Public (FREE)"


class Send_Email:
    def __init__(self, conf):
        self.xlsfile, self.risk_num, self.logger = conf['xlsfile'], conf['risk_num'], conf['logger']
        self.risk_red, self.risk_orange, self.risk_blue = conf['risk_red'], conf['risk_orange'], conf['risk_blue']

    def send(self):
        self.logger.info('start sending mail...')
        msg = MIMEMultipart()
        msg["Subject"] = "每周WEB风险总结信息详情"
        msg["From"] = email_user
        msg["To"] = target_email

        if self.xlsfile:
            part = MIMEApplication(open(self.xlsfile, 'rb').read())
            part.add_header('Content-Disposition', 'attachment', filename=self.xlsfile)
            msg.attach(part)

            part = MIMEText("WEB安全扫描发现风险漏洞总数为： %d\n\n高风险：%d ,中风险：%d ,低风险：%d\n\n注：漏洞风险详情请查阅附件信息。" % (
                self.risk_num, self.risk_red, self.risk_orange, self.risk_blue))
            msg.attach(part)
        else:
            part = MIMEText("请注意本次风险报告生成失败，请查阅日志。")
            msg.attach(part)
        error = 0
        while True:
            if error == 3:
                break
            try:
                s = smtplib.SMTP(smtp_server, timeout=30)
                s.login(email_user, email_pass)
                s.sendmail(email_user, target_email, msg.as_string())
                s.close()
                break
            except smtplib.SMTPException, e:
                error += 1
                self.logger.info('sending mail failure,error: %s' % e.message)
                continue
        self.logger.info('sending mail success')

    def run(self):
        self.send()
