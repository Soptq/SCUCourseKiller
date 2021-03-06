import datetime

from django.http import HttpResponse

from SCUKiller import utils
from .config import *

import json

from urllib import error, parse, request
from . import jwcAccount as jwcVal
from .exceptions import *

logger = jwcVal.logger


def specificWatch(opener, keyword, kch, kxh, type, term):
    latestRemaining = -100
    #  根据课程类型构造POST数据
    if type == '自由选课':
        post_params = {'searchtj': kch, 'xq': '0', 'jc': '0', 'kclbdm': ''}
        watch_data_parsed = parse.urlencode(post_params).encode('utf-8')
        Request = request.Request(query_url, watch_data_parsed, headers=headers)
    elif type == '方案选课':
        post_params = {'kch': kch, 'xq': '0', 'jc': '0', 'kclbdm': '', 'jhxn': term}
        watch_data_parsed = parse.urlencode(post_params).encode('utf-8')
        Request = request.Request(planCourse_url, watch_data_parsed, headers=headers)

    Response = opener.open(Request)
    if Response.url == 'http://zhjw.scu.edu.cn/login':
        raise CookieInvalidException("Cookie已经失效！")
    req = Response.read().decode('utf-8')
    dic = json.loads(req)
    selectList = []
    if type == '自由选课':
        parser = json.loads(dic['rwRxkZlList'])
    elif type == '方案选课':
        parser = json.loads(dic['rwfalist'])

    # print(parser)  # DEBUG

    if len(parser) == 0:
        raise NoSuchCourseException("找不到提供的课程信息所对应的课程！")
    for i in range(len(parser)):
        if kxh == parser[i]['kxh'] and kch == parser[i]['kch']:
            latestRemaining = parser[i]['bkskyl']
        if parser[i]['bkskyl'] > 0:
            if kxh == '' or kxh == parser[i]['kxh']:
                if kch == '' or kch == parser[i]['kch']:
                    selectList.append(parser[i])

    return selectList, latestRemaining  # 没有watch到仍有课余量的课程 返回空List

    # 返回数据示例
    # {'bkskrl': 416, 'bkskyl': 0, 'cxjc': '3', 'id': '4077', 'jasm': '水上报告厅', 'jxlm': '一教A座', 'kc
    # h': '999005030', 'kclbdm': '700', 'kclbmc': '人文艺术与中华文化传承', 'kcm': '中华文化（历史篇）', 'k
    # kxqh': '03', 'kkxqm': '江安', 'kkxsh': '106', 'kkxsjc': '历史文化学院（旅游学院）', 'kslxdm': '02', '
    # kslxmc': '考查', 'kxh': '01', 'sflbdm': '', 'sfxzskyz': '', 'sfxzxdlx': '否', 'sfxzxslx': '', 'sfxzxs
    # nj': '', 'sfxzxsxs': '', 'sfxzxxkc': '', 'sjdd': [{'cxjc': '3', 'jasm': '水上报告厅', 'jxlm': '一教A
    # 座', 'skjc': '10', 'skxq': '1', 'skzc': '111111111111111110000000', 'xqm': '江安', 'zcsm': '1-17周'}]
    # , 'skjc': '10', 'skjs': '李晓宇* ', 'skxq': '1', 'skzc': '111111111111111110000000', 'xf': 3, 'xkbz':
    #  '', 'xkkzdm': '01', 'xkkzh': '', 'xkkzsm': '可选可退', 'xkmsdm': '01', 'xkmssm': '直选式', 'xkxzsm':
    #  ';', 'xqm': '江安', 'xs': 48, 'zcsm': '1-17周', 'zxjxjhh': '2019-2020-1-1'}


def postCourse(opener, availCourse):
    for j in range(1, postSelectAttempt):
        # print("Posting Attempt #" + str(j) + ", for " + str(course.kcm) + ',' + str(course.kch) + '_' + str(
        #     course.kxh))
        token = utils.getToken(opener)
        selectData = utils.getSelectData(token,
                                         availCourse)

        utils.postToken(token, availCourse, opener)  # 验证码不能为空在这里出现，提交了选课信息
        try:
            selectResponse = utils.postSelect(selectData, opener)  # 进入waitingfor查询结果，在这里可能出现logout
        except error.HTTPError as e:
            print("Failed..." + str(e))
            continue
        result_data, success = utils.getResultData(selectResponse)  # 解析selectResponse
        success = utils.checkResult(result_data, opener)  # 查询选课结果
        if success == 'Conflict' or success == 'No Available Courses':
            break  # 课被抢完了 或者 课程冲突
        elif not success:  # 查询选课结果失败，再抢一次
            continue
        else:  # 成功 success为'success'  有验证码 success为'验证码'
            return success

    return success  # 循环完成也返回



