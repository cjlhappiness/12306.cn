# coding = utf-8


import re
import time
from datetime import date
import public12306
import login12306


checkUserUrl = ("POST", "https://kyfw.12306.cn/otn/login/checkUser")
submitTrainUrls = (
    ("POST", "https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest"),
    (),
    (),
    (),
)

checkUserParams = "_json_att="
submitTrainParams = (
    "secretStr={0}&query_from_station_name={1}&query_to_station_name={2}&train_date={3}&tour_flag={4}&back_train_date={5}&purpose_codes={6}&undefined=",
    "_json_att=&seatType={0}&train_no={1}&leftTicket={2}&purpose_codes={3}&toStationTelecode={4}&stationTrainCode={5}&train_date={6}&fromStationTelecode={7}",
    "",
    "",
)


def check_user_state(session, method, url, **kwargs):
    """
    :param session:
    :param method:
    :param url:
    :param kwargs: params:_json_att=
    :return:
    """
    checkResponse = public12306.create_network_request(session, method, url, **kwargs)[1]
    if checkResponse.json()["data"]["flag"]:
        print("用户校验成功！")
    else:  # 重新登录
        session = login12306.get_login_user()
    return session


def submit_train_ticket(session, method, url, secretS, stationF, stationT, deaprtureD, tourF="dc", purposeC="ADULT",
                        returnD=date.today(), **kwargs):
    """
    ---------------Steep1
    :param session:
    :param method:
    :param url:
    :param secretS: 口令
    :param stationF: 出发站
    :param stationT: 到达站
    :param deaprtureD: 出发日期
    :param tour_flag: dc单程，wc往返
    :param purpose_codes: ADULT成人，0X00学生
    :param returnD: 返程日期
    :param kwargs:
    :return:
    """
    kwargs["params"] = submitTrainParams[0].format(secretS, stationF, stationT, deaprtureD, tourF, returnD, purposeC)
    submitResponse = public12306.create_network_request(session, method, url, **kwargs)[1]
    submitJson = submitResponse.json()
    if not (submitJson["status"] & submitJson["httpstatus"] == 200):  # 需要重试
        pass


def get_submit_token(session, method, url, **kwargs):
    """
    :param session:
    :param method:
    :param url:
    :param kwargs: params:_json_att=
    :return:
    """
    tokenResponse = public12306.create_network_request(session, method, url, **kwargs)[1]
    token = re.search("globalRepeatSubmitToken = '(.*?)'", tokenResponse).groups()[0]
    if not token:  # 需要重试
        pass
    return token


def submit_train_ticket(session, method, url):

    """
    https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest
        POST        secretStr=口令, train_date=出发时间, back_train_date=返程时间, tour_flag=dc, purpose_codes=ADULT
                    , query_from_station_name=出发站名, query_to_station_name=到达站名, undefined=
    https://kyfw.12306.cn/otn/confirmPassenger/initDc       POST        _json_att=      找到返回数据中的globalRepeatSubmitToken = '278e64761b75a00f8426a10c3011649f'字段

    :return:
    """
    public12306.create_network_request(session, "POST", )
    pass



get_submit_token(None,None,None)