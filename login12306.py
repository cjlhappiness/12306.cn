# coding=utf-8


"""
    12306登录过程：

"""


import re
import json
import public12306
from io import BytesIO
from PIL import Image


initRequestHeaders = {
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "Host": "kyfw.12306.cn",
    "Referer": "https://kyfw.12306.cn/otn/login/init",
    "User-Agent":
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
}
commitRequestHeaders = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Host": "kyfw.12306.cn",
    "Origin": "https://kyfw.12306.cn",
    "Referer": "https://kyfw.12306.cn/otn/login/init",
    "User-Agent":
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

baseUrl = ("GET", "https://kyfw.12306.cn/otn/login/init")  # 登录界面url，GET
imgUrl = ("GET", "https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand")  # 验证码图片url,GET
loginImgUrl = ("POST", "https://kyfw.12306.cn/passport/captcha/captcha-check")  # 提交图片登录url,POST
otherCookiesParamsUrl = ("GET", "https://kyfw.12306.cn/otn/HttpZF/logdevice")  # cookies必须的参数可在此url获取,GET
loginUerUrls = (
    ("POST", "https://kyfw.12306.cn/passport/web/login"),  # 提交登录url,POST
    ("POST", "https://kyfw.12306.cn/otn/login/userLogin"),  # 1次验证登录,POST
    ("GET", "https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin"),  # 2次验证登录,GET
    ("POST", "https://kyfw.12306.cn/passport/web/auth/uamtk"),  # 3次验证登录,POST
    ("POST", "https://kyfw.12306.cn/otn/uamauthclient"),  # 4次验证登录,POST
)

imgRequestParams = "answer={0}&login_site=E&rand=sjrand"
loginUserParams = (
    "username={0}&password={1}&appid=otn",
    "_json_att=",
    "redirect=/otn/login/userLogin",
    "appid=otn",
)

imgLocation = [-1, "30,45", "105,45", "180,45", "250,45", "30,120", "105,120", "180,120", "250,120"]  # 验证码坐标系

stateCode = (0, 1)


def get_other_cookies(session, method, url, **kwargs):
    """
    获取必要的cookies字段
    :param session:
    :param method:
    :param url:
    :param kwargs:
    :return:
    """
    otherSession, otherResponse = public12306.create_network_request(session, method, url, **kwargs)
    otherCookiesDict = eval(re.search(r"{.*?exp.*?dfp.*?}", otherResponse.text).group())
    otherCookiesDict = {"RAIL_EXPIRATION": otherCookiesDict["exp"], "RAIL_DEVICEID": otherCookiesDict["dfp"]}
    otherSession.cookies.update(otherCookiesDict)
    return otherSession


def load_login_img(session, method, url, **kwargs):
    """
    加载图片验证码
    :param session:
    :param method:
    :param url:
    :param kwargs:
    :return:
    """
    immgSession, imgResponse = public12306.create_network_request(session, method, url, **kwargs)
    loginImage = Image.open(BytesIO(imgResponse.content))
    loginImage.show()
    imgPosition = input("输入验证码中对应图片的序号：")
    imgPosition = str(",".join([imgLocation[int(x)] for x in imgPosition]))
    return immgSession, imgPosition


def submit_login_img(session, method, url, **kwargs):
    """
    提交验证码
    :param session:
    :param method:
    :param url:
    :param kwargs:
    :return:
    """
    imgSession, imgResponse = public12306.create_network_request(session, method, url, **kwargs)
    if imgResponse.json()["result_code"] == "4":
        print("验证码校验成功！")
        return imgSession, stateCode[1]
    else:

        print("验证码校验失败！")
        return imgSession, stateCode[0]


def submit_login_user(session, methodAndUrls, loginUserParams, userName, password, **kwargs):
    """
    提交用户登录，共1个提交，3个验证
    :param session:
    :param method:
    :param urls:
    :param loginUserParams:
    :param userName:
    :param password:
    :param kwargs:
    :return:
    """
    kwargs["params"] = loginUserParams[0].format(userName, password)
    loginSession, loginResponse = public12306.create_network_request(session, *methodAndUrls[0], **kwargs)
    kwargs["params"] = loginUserParams[1]
    loginSession, _ = public12306.create_network_request(loginSession, *methodAndUrls[1], **kwargs)
    kwargs["params"] = loginUserParams[2]
    loginSession, _ = public12306.create_network_request(loginSession, *methodAndUrls[2], **kwargs)
    kwargs["params"] = loginUserParams[3]
    loginSession, thirdResponse = public12306.create_network_request(loginSession, *methodAndUrls[3], **kwargs)
    subCookies = {"tk": thirdResponse.json()["newapptk"]}
    loginSession.cookies.update(subCookies)
    kwargs["params"] = subCookies
    loginSession, fourthResponse = public12306.create_network_request(loginSession, *methodAndUrls[4], **kwargs)
    rc = "result_code"
    if loginResponse.json()[rc] == 0 & thirdResponse.json()[rc] == 0 & fourthResponse.json()[rc] == 0:
        print("用户登录成功！")
        return loginSession, stateCode[1]
    else:
        print("用户登录失败！")
        return loginSession, stateCode[0]


def get_login_user(userName, password):
    """
    获取登录的用户session
    :param userName:
    :param password:
    :return:
    """
    otherSession = get_other_cookies(None, *otherCookiesParamsUrl, headers=initRequestHeaders)
    initSession = public12306.create_network_request(otherSession, *baseUrl, headers=initRequestHeaders)[0]
    userSession, imgPosition = load_login_img(initSession, *imgUrl, headers=initRequestHeaders)
    userSession, imgCode = submit_login_img(userSession, *loginImgUrl, headers=commitRequestHeaders,
                                            params=imgRequestParams.format(imgPosition))
    userSession, userCode = submit_login_user(userSession, loginUerUrls, loginUserParams,
                                              userName, password, headers=commitRequestHeaders)
    return userSession


if __name__ == "__main__":
    userName = input("输入用户帐号：")
    password = input("输入用户密码：")
    userSession = get_login_user(userName, password)
    print(userSession.cookies)
