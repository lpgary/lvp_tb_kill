#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import json
import urllib
import hashlib
import time
import datetime
import requests

"""
h5页面中sign可验证当前访问是否合法，sign为普通md5加密
加密字符串由token + "&" + t + "&" + appKey + "&" + data 组成，其中
token从cookie中的_m_h5_tk获取，_m_h5_tk组成方式为token_时间戳
t为时间戳乘以1000
appKey为固定值，当前为12574478
data为所发送参数字典，进行json编码并去除':'，','后的空格后所生成的字符串
"""
def get_h5_sign():
    _m_h5_tk = ''
    token = _m_h5_tk.split('_')[0]
    appKey = '12574478'
    t = int(time.time()*1000)
    data = {}
    data_json = json.dumps(data)
    data_json = re.sub(r',\s"', ',"', data_json)
    data_json = re.sub(r'":\s', '":', data_json)
    e = '{0}&{1}&{2}&{3}'.format(token, t, appKey, data_json)
    m = hashlib.md5()
    m.update(e.encode(encoding='utf-8'))
    h5_sign = m.hexdigest()
    return h5_sign

def get_h5_link():
    killtime = '2021-05-11 20:00:00'
    _time_array = time.strptime(killtime, '%Y-%m-%d %H:%M:%S')
    _t = int(time.mktime(_time_array)) * 1000 + 5
    paras = {
        "jsv": "2.6.1",
        "appKey": "12574478",
        "t": _t,
        "sign": "9b3b4bb535efe6bef4aedbed0c92f53b",
        "v": "1.0",
        "type": "originaljsonp",
        "dataType": "originaljsonp",
        "timeout": "20000",
        "LoginRequest": "true",
        "H5Request": "true",
        "api": "mtop.taobao.seattle.activitydetail.get",
        "callback": "mtopjsonp3",
        "data": '{"source":"activityDetail","activityId":"1021017961819530"}'
    }#source 值如何确定有待研究，目前有观察到"activityDetail"和"memberPlatform2019
    _paras_urlencode = urllib.parse.urlencode(paras)
    h5_url = 'https://h5api.m.taobao.com/h5/mtop.taobao.seattle.activity.apply/1.0/?' + _paras_urlencode
    return  h5_url

