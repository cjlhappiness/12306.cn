# coding=utf-8


"""
    查询各种数据

"""


import re
import json
import time
from datetime import date
import public12306
import login12306


initRequestHeaders = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Host": "kyfw.12306.cn",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent":
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
}

queryTicketUrl = ("GET", "https://kyfw.12306.cn/otn/leftTicket/queryZ")  # 查询车票url,GET
stationNameUrl = ("GET", "https://kyfw.12306.cn/otn/resources/js/framework/station_name.js")  # 获取所有车站站名、电报码,GET
stationTimeUrl = ("GET", "https://kyfw.12306.cn/otn/resources/js/query/qss.js")  # 获取所有车站起售时间,GET
contactInformationUrl = ("GET", "https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs")  # 获取帐号关联的联系人信息,GET

queryTicketParams = "leftTicketDTO.train_date={0}&leftTicketDTO.from_station={1}&leftTicketDTO.to_station={2}&purpose_codes=ADULT"


def get_contact_information(session, method, url, **kwargs):
    """
    获取账号下的所有联系人信息，需要session
    :param session:
    :param method:
    :param url:
    :param kwargs:
    :return:
    """
    contactInformationDict = dict()
    contactInformationResponse = public12306.create_network_request(session, method, url, **kwargs)[1]
    contactInformationJson = contactInformationResponse.json()
    for contactInformation in contactInformationJson["data"]["normal_passengers"]:
        passenger_name = contactInformation.get("passenger_name")
        sex_name = contactInformation.get("sex_name")
        passenger_id_type_name = contactInformation.get("passenger_id_type_name")
        passenger_id_no = contactInformation.get("passenger_id_no")
        contactInformationList = [sex_name, passenger_id_type_name, passenger_id_no]
        contactInformationDict[passenger_name] = contactInformationList
        print(contactInformation)
    return contactInformationDict



def cloudCode():
    pass


def parse_station_code(method, url, **kwargs):
    """
    解析所有车站代码，无需session
    :param method:
    :param url:
    :param kwargs:
    :return:
    """
    stationResponse = public12306.create_network_request(None, method, url, **kwargs)[1]
    stationKey= list()
    stationValue = list()
    l1 = list()
    l2 = list()
    l3 = list()
    for i in re.finditer(r"@\w+\|(\w+)\|(\w+)\|(\w+)\|(\w+)", stationResponse.text):
        l1.append(i.group(1))
        l2.append(i.group(3))
        l3.append(i.group(4))
        stationValue.append(i.group(2))
    stationKey.extend(l1)
    stationKey.extend(l2)
    stationKey.extend(l3)
    if len(stationValue) * 3 != len(stationKey):
        raise ValueError("parse_station_code() Error!")
    return stationKey, stationValue


def get_station_code(stationKey, stationValue, *stationName):
    """
    获取某个车站代码
    :param stationKey:
    :param stationValue:
    :param stationName:
    :return:
    """
    length = len(stationValue)
    try:
        stationCode = list()
        for i in stationName:
            index = stationKey.index(i) % length
            stationCode.append(stationValue[index])
    except ValueError:
        print("ValueError: {0} is not in list".format(str(i)))
        return
    return stationCode


def query_ticket(method, url, stationCode, date=date.today(), **kwargs):
    """
    查询车票，无需session
    :param method:
    :param url:
    :param stationCode:
    :param date:
    :param kwargs:
    :return:
    """
    queryJson = None
    while not queryJson:
        kwargs["params"] = queryTicketParams.format(date, *stationCode)
        queryResponse = public12306.create_network_request(None, method, url, **kwargs)[1]
        try:
            queryJson = queryResponse.json()
        except json.decoder.JSONDecodeError as e:
            # print("JSONDecodeError: " + str(e))
            # print(queryJson)
            pass
    return queryJson


def parse_train_json(queryJson, seatFilter=None):
    """
    :param jsonData:
    :param seatFilter:
    :return:
    """
    queryStationCode = queryJson["data"]["map"]
    compile = re.compile(r"\|")
    trafficInformations = list()
    for train in queryJson["data"]["result"]:
        trainNo = re.split(compile, train)
        trafficInformation = list()  # 长度22
        trafficInformation.extend(trainNo[:1])  # 令牌，1
        trafficInformation.extend(half_turn_angle(trainNo[1:2]))  # 预订信息，1
        trafficInformation.extend(half_turn_angle(trainNo[3:4]))  # 车次，1
        trafficInformation.extend(code_turn_station(queryStationCode, trainNo[6:8]))  # 出发站，目的站，2
        trafficInformation.extend(half_turn_angle(trainNo[8:11]))  # 发车时间，到达时间，时长，3
        trafficInformation.extend(trainNo[11:12])  # 能否预定，1
        if seatFilter:
            seatInformation = trainNo[21:34]
            trafficInformation.extend(half_turn_angle([seatInformation[si] for si in seatFilter]))  # 坐席信息，自定义长度
        else:
            trafficInformation.extend(half_turn_angle(trainNo[21:34]))  # 坐席信息，13
        trafficInformations.append(trafficInformation)
    return queryStationCode, trafficInformations


def half_turn_angle(halfChars):
    """
    ascii半角字符转全角
    :param halfChars:
    :return:
    """
    turnLambda = lambda x: chr(ord(x) + 65248) if 0 < ord(x) < 127 else x
    newChars = []
    for halfChar in halfChars:
        if not halfChar:
            halfChar = "-"
        angleChars = ""
        for c in halfChar:
            angleChars += turnLambda(c)
        newChars.append(angleChars)
    return newChars


def code_turn_station(queryStationCode, stationCodes):
    """
    通过查询车票返回的车站码-车站字典，将对应车次车站码转为车站名
    :param queryStationCode: dict
    :param stationCodes: list等iter对象
    :return: list
    """
    stationName = list()
    for stationCode in stationCodes:
        stationName.append(queryStationCode[stationCode])
    return stationName


def assemble_query_result(stationf, stationt, queryd=date.today(), seatFilter=None):
    """
    :param stationf:
    :param stationt:
    :param queryd:
    :param seatFilter:
    :return:
    """
    stationKey, stationValue = parse_station_code(*stationNameUrl, headers=initRequestHeaders, timeout=5)
    stationCode = get_station_code(stationKey, stationValue, stationf, stationt)
    queryJson = query_ticket(*queryTicketUrl, stationCode, queryd, headers=initRequestHeaders, timeout=0.1)
    queryStationCode, trafficInformations = parse_train_json(queryJson, seatFilter)
    return echo_query_train(queryStationCode, trafficInformations)


def echo_query_title():
    echoTitleFormat = "{0:　<7}{1:　<7}{2:　<7}{3:　<7}{4:　<7}{5:　<7}{6:　<3}{7:　<3}{8:　<3}{9:　<3}" \
                        "{11:　<3}{13:　<3}{14:　<3}{15:　<3}{16:　<3}{17:　<3}{18:　<3}{19}"
    echoTitle = ("车次", "出发站", "到达站", "发车时间", "到达时间", "时长", "高软", "其他", "软卧",
                 "软座", "＊＊", "无座", "＊＊", "硬卧", "硬座", "二等", "一等", "商务", "动卧", "预定信息")
    return echoTitleFormat.format(*echoTitle)


def echo_query_train(queryStationCode, trafficInformations):
    echoTrainFormat = "{2:　<7}{3:　<7}{4:　<7}{5:　<7}{6:　<7}{7:　<7}{9:　<3}{10:　<3}{11:　<3}{12:　<3}" \
                      "{14:　<3}{16:　<3}{17:　<3}{18:　<3}{19:　<3}{20:　<3}{21:　<3}{1}"
    trainInformations = list()
    for train in trafficInformations:
        trainInformations.append(echoTrainFormat.format(*train))
    return trainInformations


if __name__ == "__main__":
    i = 0
    interval = 0.1
    t = time.time()
    nowDate = date.today()
    # while True:
    for _ in range(50):
        startTime = time.time()
        try:
            i += 1
            print(i, "正在查询：")
            print(echo_query_title())
            for train in assemble_query_result("hangzhou", "chongqing", queryd=date.today()):
                print(train)
            print("\n")
        except:
            pass
        endTime = time.time()
        s1 = (interval - (endTime - startTime))
        time.sleep(s1 if s1 > 0 else 0)
    print("耗时：", time.time() - t, "s")

