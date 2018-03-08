# coding = utf-8


import re
import public12306


methodAndUrl = (
    ("POST", "https://kyfw.12306.cn/otn/login/checkUser"),



)

requestParams = (
    "_json_att=",

)


def commmit_train_ticket(session):
    """
    https://kyfw.12306.cn/otn/login/checkUser       POST        _json_att=
    https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest
        POST        secretStr=口令, train_date=出发时间, back_train_date=返程时间, tour_flag=dc, purpose_codes=ADULT
                    , query_from_station_name=出发站名, query_to_station_name=到达站名, undefined=
    https://kyfw.12306.cn/otn/confirmPassenger/initDc       POST        _json_att=      找到返回数据中的globalRepeatSubmitToken = '278e64761b75a00f8426a10c3011649f'字段

    :return:
    """
    public12306.create_network_request(session, "POST", )
    pass
