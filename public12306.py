# coding=utf-8


"""
    公共字段、函数
"""


import requests
from selenium import webdriver


def create_network_request(session, method, url, **kwargs):
    """
    通用的网络请求函数
    :param session:
    :param method:
    :param url:
    :param kwargs:
    :return:
    """
    if not session:
        session = requests.session()
    try:
        response = session.request(method, url, **kwargs)
    except requests.exceptions.SSLError:
        response = session.request(method, url, verify=False, **kwargs)
    return session, response


def open_webdriver(session):
    driver = webdriver.Chrome()
    driver.get("https://kyfw.12306.cn/otn/login/init")
    driver.delete_all_cookies()
    for key, value in requests.utils.dict_from_cookiejar(session.cookies).items():
        cookieDict = dict()
        cookieDict["name"] = key
        cookieDict["value"] = value
        driver.add_cookie(cookieDict)
    driver.get("https://kyfw.12306.cn/otn/passport?redirect=/otn/index/initMy12306")
    input("输入任意内容以继续：")


