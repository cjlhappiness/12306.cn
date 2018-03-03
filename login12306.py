# coding=utf-8


"""
    12306登录过程：
        1、获取验证码图片，地址imgUrl，获取回复头cookie，获取响应头Set-Cookie字段值，并将其加入到请求头_passport_ct字段中
        2、通过验证码验证，地址loginImgUrl，将1中装好的cookie用到本次请求头中，并post参数answer={0}&login_site=E&rand=sjrand
        3、登录用户账户，地址loginUserUrl，将1中装好的cookie用到本次请求头中，并post参数username={0}&password={1}&appid=otn，接收返回的json数据
        4、到此为止，1中装好的cookie成功通过12306验证
"""


import re
import requests
from io import BytesIO
from PIL import Image


baseUrl = "https://kyfw.12306.cn/otn/login/init"  # 登录界面url，GET
imgUrl = "https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand"  # 验证码图片url,GET
loginImgUrl = "https://kyfw.12306.cn/passport/captcha/captcha-check"  # 提交图片登录url,POST
otherCookiesParamsUrl = "https://kyfw.12306.cn/otn/HttpZF/logdevice"  # cookies必须的参数可在此url获取,GET
loginUerUrl = ("https://kyfw.12306.cn/passport/web/login",  # 提交登录url,POST
               "https://kyfw.12306.cn/otn/login/userLogin",  # 1次验证登录,POST
               "https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin",  # 2次验证登录,GET
               "https://kyfw.12306.cn/passport/web/auth/uamtk",  # 3次验证登录,POST
               "https://kyfw.12306.cn/otn/uamauthclient"  # 4次验证登录,POST
               )
imgRequestHeaders = {
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "Host": "kyfw.12306.cn",
    "Referer": "https://kyfw.12306.cn/otn/login/init",
    "User-Agent":
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
}

loginRequestHeaders = {
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

imgRequestParams = "answer={0}&login_site=E&rand=sjrand"
loginUserParams = (
    "username={0}&password={1}&appid=otn",
    "_json_att=",
    "redirect=/otn/login/userLogin",
    "appid=otn",
    "tk={0}"
)
imgLocation = ["null", "30,45", "105,45", "180,45", "250,45", "30,120", "105,120", "180,120", "250,120"]
test1User = ["1287513006@qq.com", "lp950125"]
testUser = ["570604900@qq.com", "lyj950422"]


_RESULT_OK = 1
_RESULT_FAIL = -1


def create_network_request(method, url, **kwargs):
    """
    通用的网络请求函数
    :param method:
    :param url:
    :param kwargs:
    :return:
    """
    session = requests.session()
    response = session.request(method, url, **kwargs)
    return response


def get_other_cookies_params(method, url, **kwargs):
    cookiesResponse = create_network_request(method, url, **kwargs)
    otherParamsDict = eval((re.findall(r"{.*}", cookiesResponse.text)[0]).replace("exp", "RAIL_EXPIRATION").replace("dfp", "RAIL_DEVICEID"))
    return requests.utils.add_dict_to_cookiejar(None, otherParamsDict)


def load_login_img(method, url, **kwargs):
    """
    加载验证码图片
    :param method:
    :param url:
    :return:
    """
    imgResponse = create_network_request(method, url, **kwargs)
    imgCookies = imgResponse.cookies
    loginImage = Image.open(BytesIO(imgResponse.content))
    loginImage.show()
    imgPosition = input("请输入验证码中对应图片的序号：")
    loginImage.close()
    imgPosition = str(",".join([imgLocation[int(x)] for x in imgPosition]))
    return imgPosition, imgCookies


def submit_login_img(method, url, **kwargs):
    """
    提交验证码
    :param method:
    :param url:
    :param kwargs:
    :return:
    """
    kwargs["params"] = imgRequestParams.format(kwargs["params"])
    imgResponse = create_network_request(method, url, **kwargs)
    if int(eval(imgResponse.text)["result_code"]) == 4:
        print("验证码校验成功！")
        return _RESULT_OK
    else:
        print("验证码校验失败！")
        return _RESULT_FAIL


def submit_login_user(method, urls, loginUserParams, userName, password, **kwargs):
    """
    :param method:
    :param urls:
    :param loginUserParams:
    :param userName:
    :param password:
    :param kwargs:
    :return:
    """
    kwargs["params"] = loginUserParams[0].format(userName, password)
    loginResponse = create_network_request(method, urls[0], **kwargs)
    requestCookies = kwargs["cookies"]
    requestCookies.update(loginResponse.cookies)
    firstLogin = create_network_request("POST", urls[1], headers=loginRequestHeaders, cookies=userCookies,
                                        params=loginUserParams[1])
    secondLogin = create_network_request("GET", urls[2], headers=loginRequestHeaders, cookies=userCookies,
                                         params=loginUserParams[2])
    userCookies.update(secondLogin.cookies)
    thirdLogin = create_network_request("POST", urls[3], headers=imgRequestHeaders, cookies=userCookies,
                                        params=loginUserParams[3]).json()
    userCookies["tk"] = thirdLogin["newapptk"]
    fourthlogin = create_network_request("POST", urls[4], headers=loginRequestHeaders, cookies=userCookies,
                                         params=loginUserParams[4].format(thirdLogin["newapptk"]))
    if int(eval(loginResponse.text)["result_code"]) == 0:
        print("用户登录成功！")
        return _RESULT_OK, requestCookies
    else:
        print("用户登录失败！")
        return _RESULT_FAIL, None


if __name__ == "__main__":
    otherParamsCookies = get_other_cookies_params("GET", otherCookiesParamsUrl, headers=imgRequestHeaders)
    initCookies = create_network_request("GET", baseUrl, headers=imgRequestHeaders, timeout=10).cookies
    imgPosition, userCookies = load_login_img("GET", imgUrl, headers=imgRequestHeaders, timeout=10)
    userCookies.update(initCookies)
    userCookies.update(otherParamsCookies)
    submit_login_img("POST", loginImgUrl, headers=loginRequestHeaders, params=imgPosition, cookies=userCookies)
    loginResponseCode, userCookies = submit_login_user("POST", loginUerUrl, loginUserParams, testUser[0], testUser[1],
                                                       headers=loginRequestHeaders, cookies=userCookies)
