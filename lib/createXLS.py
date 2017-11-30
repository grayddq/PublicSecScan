# -*- coding: utf-8 -*-
from xlwt import *
from config import *
import os, time, redis, logging

NAME, VERSION, AUTHOR, LICENSE = "PublicSecScan", "V0.1", "咚咚呛", "Public (FREE)"


class Create_Xls:
    def __init__(self, logger):
        self.results = []
        self.logger = logger
        self.risk_num, self.risk_red, self.risk_orange, self.risk_blue = 0, 0, 0, 0

    def get_result(self):
        self.logger.info('read risk result')
        r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=REDIS_DB)
        keys = r.keys('risk_*')
        for k in keys:
            self.results.append(eval(r.get(k)))
        self.risk_num = len(keys)

    def create_xls(self):
        try:
            file = Workbook(encoding='utf-8')
            table = {}
            application = u'WEB安全扫描详情'
            sheet_name = file.add_sheet(application)
            table[application] = sheet_name
            table[application + 'row'] = 1

            pattern = Pattern()  # Create the Pattern
            pattern.pattern = Pattern.SOLID_PATTERN
            pattern.pattern_fore_colour = 22
            style = XFStyle()  # Create the Pattern
            style.pattern = pattern  # Add Pattern to Style

            sheet_name.write(0, 0, u'风险目标', style)
            sheet_name.write(0, 1, u'风险名称', style)
            sheet_name.write(0, 2, u'风险等级', style)
            sheet_name.write(0, 3, u'风险参数', style)
            sheet_name.write(0, 4, u'风险地址', style)
            sheet_name.write(0, 5, u'风险描述', style)
            sheet_name.write(0, 6, u'风险请求request', style)
            sheet_name.write(0, 7, u'风险应答response', style)
            sheet_name.write(0, 8, u'风险标志MD5', style)

            for result in self.results:
                row = table[application + 'row']
                table[application].write(row, 0, result['host'])
                table[application].write(row, 1, result['risk_name'])
                table[application].write(row, 2, result['risk_level'])
                table[application].write(row, 3, result['risk_parameter'])
                table[application].write(row, 4, result['risk_affects'])
                table[application].write(row, 5, result['risk_details'])
                table[application].write(row, 6, result['risk_request'])
                table[application].write(row, 7, result['risk_response'])
                table[application].write(row, 8, result['md5'])
                table[application + 'row'] += 1
                if result['risk_level'] == 'red':
                    self.risk_red += 1
                elif result['risk_level'] == 'orange':
                    self.risk_orange += 1
                elif result['risk_level'] == 'blue':
                    self.risk_blue += 1

            if not os.path.exists('out'):
                os.mkdir('out')
            filename = 'out/%s.xls' % time.strftime('%Y-%m-%d', time.localtime(time.time()))
            if os.path.exists(filename):
                os.remove(filename)
            file.save(filename)
            self.logger.info('Generate the report file %s' % filename)
            return filename
        except Exception, e:
            self.logger.info("report create error, function create_xls error: %s" % (str(e)))
        return False

    def run(self):
        self.get_result()
        filename = self.create_xls()
        return filename, self.risk_num, self.risk_red, self.risk_orange, self.risk_blue
