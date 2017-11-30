# -*- coding: utf-8 -*-
from tasks import *
from lib.createXLS import *
from lib.publicEmail import *

NAME, VERSION, AUTHOR, LICENSE = "PublicSecScan", "V0.1", "咚咚呛", "Public (FREE)"


def loging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(message)s'
    )
    if not os.path.exists('log'):
        os.mkdir('log')
    logger = logging.getLogger('LogInfo')
    fh = logging.FileHandler('log/process.log')
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


def sec_add(logger):
    logger.info('start push the task data...')
    with open(os.path.dirname(os.path.realpath(__file__)) + '/domain.txt', 'r') as f:
        for line in f.readlines():
            logger.info('[+] push targer domain %s ' % line)
            sec_dispath.delay(line)


def create_report(logger):
    return Create_Xls(logger).run()


def send_mail(file_xls, risk_num, risk_red, risk_orange, risk_blue, logger):
    conf = {'email_user': email_user, 'email_pass': email_pass, 'smtp_server': smtp_server,
            'target_email': target_email, 'xlsfile': file_xls, 'risk_num': risk_num, 'logger': logger,
            'risk_red': risk_red, 'risk_orange': risk_orange, 'risk_blue': risk_blue}
    if email_user and email_pass and smtp_server and target_email:
        Send_Email(conf).run()


if __name__ == '__main__':
    logger = loging()
    file_xls, risk_num, risk_red, risk_orange, risk_blue = create_report(logger)
    send_mail(file_xls, risk_num, risk_red, risk_orange, risk_blue, logger)
    sec_add(logger)
