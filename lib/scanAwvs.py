# -*- coding: utf-8 -*-
import random, subprocess, hashlib, logging, time, os, redis
from xml.dom import minidom
from config import *

NAME, VERSION, AUTHOR, LICENSE = "PublicSecScan", "V0.1", "咚咚呛", "Public (FREE)"


class AWVS_Scan():
    def __init__(self, target):
        self.target = target
        self.risk_num = 0
        self.save_dir = os.path.dirname(os.path.realpath(__file__)) + '/tmp/' + (
            str(random.randint(1000000, 10000000))) + '/'
        if not os.path.exists(os.path.dirname(os.path.realpath(__file__)) + '/tmp/'):
            os.mkdir(os.path.dirname(os.path.realpath(__file__)) + '/tmp/')
        wvs_scan_sentence = '/Scan "%s" /Profile default /ExportXML /SaveFolder %s  --tooltimeout=10 --GetFirstOnly=false --FetchSubdirs=true --RestrictToBaseFolder=true --ForceFetchDirindex=true --ScanningMode=Quick'
        self.scan_sentence = wvs_scan_sentence % (target, self.save_dir)
        if not os.path.exists('log'):
            os.mkdir('log')
        self.logger = self.loging()

    def loging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(message)s'
        )
        logger = logging.getLogger('LogInfo')
        fh = logging.FileHandler('log/process.log')
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        return logger

    def infostring(self, infostring):
        self.logger.info(infostring)

    def do_scan(self):
        try:
            res = subprocess.Popen(wvs_location + 'wvs_console.exe ' + self.scan_sentence, shell=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            (output, error) = res.communicate()
            if error:
                self.infostring('awvs scan error,awvs rpocess error')
                self.result = {"target": self.target, "scan_result": {}}
                return
            self.infostring('wvs sec scan finsh')
            self.result = {"target": self.target, "scan_result": {}}
            self.result['scan_result'] = self.parse_xml(self.save_dir + 'export.xml')
        except Exception, e:
            self.logger.info("awvs scan error, function do_scan error: %s" % (str(e)))
            self.result['scan_result'] = {}

    def md5(self, str):
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest()

    def GetNowTime(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

    def parse_xml(self, file_name):
        self.infostring('start parse scan result')
        bug_list = {}
        try:
            root = minidom.parse(file_name).documentElement
            ReportItem_list = root.getElementsByTagName('ReportItem')
            bug_list['starturl'] = root.getElementsByTagName('StartURL')[0].firstChild.data.encode('utf-8')
            bug_list['startime'] = root.getElementsByTagName('StartTime')[0].firstChild.data.encode('utf-8')
            bug_list['finishtime'] = root.getElementsByTagName('FinishTime')[0].firstChild.data.encode('utf-8')
            bug_list['scantime'] = root.getElementsByTagName('ScanTime')[0].firstChild.data.encode('utf-8')
            bug_list['banner'] = root.getElementsByTagName('Banner')[0].firstChild.data.encode('utf-8') if \
                root.getElementsByTagName('Banner')[0].firstChild else ""
            bug_list['os'] = root.getElementsByTagName('Os')[0].firstChild.data.encode('utf-8') if \
                root.getElementsByTagName('Os')[0].firstChild else ""
            bug_list['webserver'] = root.getElementsByTagName('WebServer')[0].firstChild.data.encode('utf-8') if \
                root.getElementsByTagName('WebServer')[0].firstChild else ""
            bug_list['technolog'] = root.getElementsByTagName('Technologies')[0].firstChild.data.encode('utf-8') if \
                root.getElementsByTagName('Technologies')[0].firstChild else ""
            bug_list['risk'] = []

            if ReportItem_list:
                for ReportItem_node in ReportItem_list:
                    risk_temp = {}
                    risk_temp["host"] = self.target
                    risk_temp["risk_name"] = ReportItem_node.getElementsByTagName("Name")[0].firstChild.data.encode(
                        'utf-8')  # 风险名称
                    risk_temp["risk_level"] = ReportItem_node.getAttribute("color")  # 风险等级

                    risk_temp["risk_parameter"] = ReportItem_node.getElementsByTagName("Parameter")[
                        0].firstChild.data.encode('utf-8') if \
                        ReportItem_node.getElementsByTagName("Parameter")[0].firstChild else ""  # 风险参数

                    risk_temp["risk_affects"] = ReportItem_node.getElementsByTagName("Affects")[
                        0].firstChild.data.encode('utf-8') if \
                        ReportItem_node.getElementsByTagName("Affects")[0].firstChild else ""  # 风险地址

                    risk_temp["risk_details"] = ReportItem_node.getElementsByTagName("Details")[
                        0].firstChild.data.encode('utf-8') if \
                        ReportItem_node.getElementsByTagName("Details")[0].firstChild else ""  # 风险描述

                    risk_temp["risk_request"] = ReportItem_node.getElementsByTagName("Request")[
                        0].firstChild.data.encode('utf-8') if \
                        ReportItem_node.getElementsByTagName("Request")[0].firstChild else ""  # 风险访问

                    risk_temp["risk_response"] = ReportItem_node.getElementsByTagName("Response")[
                        0].firstChild.data.encode('utf-8') if \
                        ReportItem_node.getElementsByTagName("Response")[0].firstChild else ""  # 风险访问

                    risk_temp["md5"] = self.md5(
                        risk_temp['host'] + risk_temp['risk_name'] + risk_temp['risk_level'] + risk_temp[
                            'risk_parameter'] + risk_temp['risk_affects'])
                    risk_temp["create_time"] = self.GetNowTime()
                    bug_list["risk"].append(risk_temp)
            self.infostring('parse result finsh')
        except Exception, e:
            self.infostring('parse result error, error: %s' % str(e))
        return bug_list

    def tryConnetRedis(self, r, count=3):
        for i in range(count):
            if not r.ping():
                r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=REDIS_DB)
            else:
                return r
        if not r.ping():
            return False

    def do_callback(self):
        self.infostring('start push reslut into redis')
        if os.path.exists(self.save_dir):
            __import__('shutil').rmtree(self.save_dir)
        if self.result:
            if self.result['scan_result']:
                self.risk_num = len(self.result['scan_result']['risk'])
                r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=REDIS_DB)
                r = self.tryConnetRedis(r)
                for risk in self.result['scan_result']['risk']:
                    try:
                        r.set('risk_' + risk['md5'], risk)
                        r.expire('risk_' + risk['md5'], risk_timeout)
                    except Exception, e:
                        self.infostring('result to redis error,function do_callback error: %s' % str(e))
                r.execute_command("QUIT")

    def run(self):
        self.infostring('start sec scan target: %s ...' % self.target)
        self.do_scan()
        self.do_callback()
        self.infostring('Complete this task ,target: %s ,find risk num: %d' % (self.target, self.risk_num))
