#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: PAN Leyi
# Email:  panleyi@kuaishou.com


from itertools import islice
import json
import os
import random
import requests
import traceback
from translate import Translator
from datetime import datetime

from orionagent.config import Config
from orionagent.tools.base import BaseResult, BaseTool
from orionagent.utils.date_utils import get_date_list, fix_date_to_format


KEY = os.getenv("WEATHER_API_KEY")
URL_CURRENT_WEATHER = "http://api.weatherapi.com/v1/current.json"
URL_FORECAST_WEATHER = "http://api.weatherapi.com/v1/forecast.json"
URL_HISTORY_WEATHER = "http://api.weatherapi.com/v1/history.json"


def translate_text(text):
    translator = Translator(to_lang="Chinese")
    translation = translator.translate(text)
    return translation


class WeatherResult(BaseResult):
    @property
    def answer(self):
        if not self.json_data:
            return ""
        else:
            item = self.json_data
            print(item)
            if "error" in json.dumps(item):
                if item["start_date"] == item["end_date"]:
                    return f'å¤©æ°”å·¥å…·æ— æ³•æŸ¥è¯¢åˆ°{item["location"]}åœ¨{item["start_date"]}è¿™ä¸€å¤©å¤©æ°”ï¼Œå»ºè®®ç”¨ç½‘é¡µæœç´¢'
                else:
                    return f'å¤©æ°”å·¥å…·æ— æ³•æŸ¥è¯¢åˆ°{item["location"]}åœ¨{item["start_date"]}å’Œ{item["end_date"]}ä¹‹é—´çš„å¤©æ°”ï¼Œå»ºè®®ç”¨ç½‘é¡µæœç´¢'
            rst = ""
            for main_key in item.keys():
                if isinstance(item[main_key], str):
                    continue
                if len(item[main_key]) != 0:
                    rst += f"{main_key}ï¼š \n"
                    keys = item[main_key][0].keys()
                    rst += ' | ' + ' | '.join(keys) + ' | ' + '\n'
                    for i in range(len(keys)):
                        rst += ' | ' + '---'
                    rst += ' |\n'

                    for row in item[main_key]:
                        rst += ' | ' + ' | '.join(row.values()) + ' | ' + '\n'
                rst += "\n"
            return rst


class WeatherTool(BaseTool):
    """
    Retrieve weather information for specified locations and dates.

    Args:
        location (str): Locations in English separated by commas, e.g., "Beijing,Vancouver,...,Chicago".
        start_date (str): Start date in format "yyyy-MM-dd".
        end_date (str): End date in format "yyyy-MM-dd".
        is_current (str): "yes" or "no" indicating if current time's weather is desired.

    Returns:
        str: Weather information between start date and end date.
    """
    name = "get_weather_info"
    zh_name = "æŸ¥è¯¢å¤©æ°”"
    description = 'Get weather info:"get_weather_info", args:"location": <location1,location2,...,in English,required>, "start_date":"<str: yyyy-MM-dd, required>", "end_date":"<str: yyyy-MM-dd, required>", "is_current":"<str, yes or no, required>"'
    tips = ""

    location_c2e ={
        # ä¸­å›½ä¸»è¦çœå¸‚
        "ä¸Šæµ·": "Shanghai",
        "äº‘å—": "Yunnan",
        "å†…è’™å¤": "Inner Mongolia",
        "åŒ—äº¬": "Beijing",
        "å°æ¹¾": "Taiwan",
        "å‰æž—": "Jilin",
        "å››å·": "Sichuan",
        "å¤©æ´¥": "Tianjin",
        "å®å¤": "Ningxia",
        "å®‰å¾½": "Anhui",
        "å±±ä¸œ": "Shandong",
        "å±±è¥¿": "Shanxi",
        "å¹¿ä¸œ": "Guangdong",
        "å¹¿è¥¿": "Guangxi",
        "æ–°ç–†": "Xinjiang",
        "æ±Ÿè‹": "Jiangsu",
        "æ±Ÿè¥¿": "Jiangxi",
        "æ²³åŒ—": "Hebei",
        "æ²³å—": "Henan",
        "æµ™æ±Ÿ": "Zhejiang",
        "æµ·å—": "Hainan",
        "æ¹–åŒ—": "Hubei",
        "æ¹–å—": "Hunan",
        "æ¾³é—¨": "Macao",
        "ç”˜è‚ƒ": "Gansu",
        "ç¦å»º": "Fujian",
        "è¥¿è—": "Tibet",
        "è´µå·ž": "Guizhou",
        "è¾½å®": "Liaoning",
        "é‡åº†": "Chongqing",
        "é™•è¥¿": "Shaanxi",
        "é’æµ·": "Qinhai",
        "é¦™æ¸¯": "Hong Kong",
        "é»‘é¾™æ±Ÿ": "Heilongjiang",
        "çŸ³å®¶åº„": "Shijiazhuang",
        "å¤ªåŽŸ": "Taiyuan",
        "å‘¼å’Œæµ©ç‰¹": "Huhehaote",
        "æ²ˆé˜³": "Shenyang",
        "é•¿æ˜¥": "Changchun",
        "å“ˆå°”æ»¨": "Haerbin",
        "å—äº¬": "Nanjing",
        "æ­å·ž": "Hangzhou",
        "åˆè‚¥": "Hefei",
        "ç¦å·ž": "Fuzhou",
        "æµŽå—": "Jinan",
        "å—æ˜Œ": "Nanchang",
        "éƒ‘å·ž": "Zhengzhou",
        "ä¹Œé²æœ¨é½": "Urumqi",
        "æ­¦æ±‰": "Wuhan",
        "é•¿æ²™": "Changsha",
        "å¹¿å·ž": "Guangzhou",
        "å—å®": "Nanning",
        "æµ·å£": "Haikou",
        "æˆéƒ½": "Chengdu",
        "è´µé˜³": "Guiyang",
        "æ˜†æ˜Ž": "Kunming",
        "æ‹‰è¨": "Lasa",
        "è¥¿å®‰": "Xi'an",
        "è¥¿å®": "Xining",
        "å…°å·ž": "Lanzhou",
        "é“¶å·": "Yinchuan",
        "æ·±åœ³": "Shenzhen",
        "è‹å·ž": "Suzhou",
        "ä¸œèŽž": "Dongwan",
        "å®æ³¢": "Ningbo",
        "ä½›å±±": "Foshan",
        "é’å²›": "Qingdao",
        "æ— é”¡": "Wuxi",
        "åŽ¦é—¨": "Xiamen",
        "æ¸©å·ž": "Wenzhou",
        "é‡‘åŽ": "Jinhua",
        "å¤§è¿ž": "Dalian",
        "æ³‰å·ž": "Quanzhou",
        "æƒ å·ž": "Huizhou",
        "å¸¸å·ž": "Changzhou",
        "å˜‰å…´": "Jiaxing",
        "å¾å·ž": "Xuzhou",
        "å—é€š": "Nantong",
        "ä¿å®š": "Baoding",
        "ç æµ·": "Zhuhai",
        "ä¸­å±±": "Zhongshan",
        "ä¸´æ²‚": "Linyi",
        "æ½åŠ": "Weifang",
        "çƒŸå°": "Yantai",
        "ç»å…´": "Shaoxing",
        "å°å·ž": "Taizhou",
        "æ´›é˜³": "Luoyang",
        "å»ŠåŠ": "Langfang",
        "æ±•å¤´": "Shantou",
        "æ¹–å·ž": "Huzhou",
        "å’¸é˜³": "Xianyang",
        "ç›åŸŽ": "Yancheng",
        "æµŽå®": "Jining",
        "æ‰¬å·ž": "Yangzhou",
        "èµ£å·ž": "Ganzhou",
        "é˜œé˜³": "Fuyang",
        "å”å±±": "Tangshan",
        "é•‡æ±Ÿ": "Zhenjiang",
        "é‚¯éƒ¸": "Handan",
        "å—é˜³": "Nanyang",
        "æ¡‚æž—": "Guilin",
        "æ³°å·ž": "Taizhou",
        "éµä¹‰": "Zunyi",
        "æ±Ÿé—¨": "Jiangmen",
        "æ­é˜³": "Jieyang",
        "èŠœæ¹–": "Wuhu",
        "å•†ä¸˜": "Shangqiu",
        "è¿žäº‘æ¸¯": "Lianyunguang",
        "æ–°ä¹¡": "Xinxiang",
        "æ·®å®‰": "Huaian",
        "æ·„åš": "Zibo",
        "ç»µé˜³": "Mianyang",
        "èæ³½": "Heze",
        "æ¼³å·ž": "Zhangzhou",
        "å‘¨å£": "Zhoukou",
        "æ²§å·ž": "Cangzhou",
        "ä¿¡é˜³": "Xinyang",
        "è¡¡é˜³": "Hengyang",
        "æ¹›æ±Ÿ": "Zhanjiang",
        "ä¸‰äºš": "Sanya",
        "ä¸Šé¥¶": "Shangrao",
        "é‚¢å°": "Xingtai",
        "èŽ†ç”°": "Putian",
        "æŸ³å·ž": "Liuzhou",
        "å®¿è¿": "Suqian",
        "ä¹æ±Ÿ": "Jiujiang",
        "è¥„é˜³": "Xiangyang",
        "é©»é©¬åº—": "Zhumadian",
        "å®œæ˜Œ": "Yichang",
        "å²³é˜³": "Yueyang",
        "è‚‡åº†": "Zhaoqing",
        "æ»å·ž": "Chuzhou",
        "å¨æµ·": "Weihai",
        "å¾·å·ž": "Dezhou",
        "æ³°å®‰": "Taian",
        "å®‰é˜³": "Anyang",
        "è†å·ž": "Jingzhou",
        "è¿åŸŽ": "Yuncheng",
        "å®‰åº†": "Anqing",
        "æ½®å·ž": "Chaozhou",
        "æ¸…è¿œ": "Qingyuan",
        "å¼€å°": "Kaifeng",
        "å®¿å·ž": "Suzhou",
        "æ ªæ´²": "Zhuzhou",
        "èšŒåŸ ": "Bengbu",
        "è®¸æ˜Œ": "Xuchang",
        "å®å¾·": "Ningde",
        "å…­å®‰": "Liuan",
        "å®œæ˜¥": "Yichun",
        "èŠåŸŽ": "Liaocheng",
        "æ¸­å—": "Weinan",
        "å®œå®¾": "Yibin",
        "éžå±±": "Anshan",
        "å—å……": "Nanchong",
        "ç§¦çš‡å²›": "Qinhuangdao",
        "æ¯«å·ž": "Haozhou",
        "å¸¸å¾·": "Changde",
        "æ™‹ä¸­": "Jinzhong",
        "å­æ„Ÿ": "Xiaogan",
        "ä¸½æ°´": "Lishui",
        "å¹³é¡¶å±±": "Pingdingshan",
        "é»„å†ˆ": "Huanggang",
        "é¾™å²©": "Longyan",
        "æž£åº„": "Zaozhuang",
        "éƒ´å·ž": "Chenzhou",
        "æ—¥ç…§": "Rizhao",
        "é©¬éžå±±": "Maanshan",
        "è¡¢å·ž": "Quzhou",
        "é„‚å°”å¤šæ–¯": "Ordos Barun Gar Domda",
        "åŒ…å¤´": "Baotou",
        "é‚µé˜³": "Shaoyang",
        "å¾·é˜³": "Deyang",
        "æ³¸å·ž": "Luzhou",
        "ä¸´æ±¾": "Linfen",
        "å—å¹³": "Nanping",
        "ç„¦ä½œ": "Jiaozuo",
        "å®£åŸŽ": "Xuancheng",
        "æ¯•èŠ‚": "Bijie",
        "æ·®å—": "Huainan",
        "é»”å—": "Qiannan",
        "æ»¨å·ž": "Binzhou",
        "é»”ä¸œå—": "Qiandongnan",
        "èŒ‚å": "Maoming",
        "ä¸‰æ˜Ž": "Sanming",
        "æ¹˜æ½­": "Xiangtan",
        "æ¢…å·ž": "Meizhou",
        "ä¹å±±": "Leshan",
        "é»„çŸ³": "Huangshi",
        "éŸ¶å…³": "Shaoguan",
        "è¡¡æ°´": "Hengshui",
        "æ€€åŒ–": "Huaihua",
        "å¼ å®¶å£": "Zhangjiakou",
        "æ°¸å·ž": "Yongzhou",
        "åå °": "Shiyan",
        "æ›²é–": "Qujing",
        "å¤§åº†": "Daqing",
        "èˆŸå±±": "Zhoushan",
        "å®é¸¡": "Baoji",
        "æ™¯å¾·é•‡": "Jingdezhen",
        "åŒ—æµ·": "Beihai",
        "å¨„åº•": "Loudi",
        "æ±•å°¾": "Shanwei",
        "é”¦å·ž": "Jinzhou",
        "å’¸å®": "Xianning",
        "å¤§åŒ": "Datong",
        "æ©æ–½": "Enshi",
        "è¥å£": "Yingkou",
        "é•¿æ²»": "Changzhi",
        "èµ¤å³°": "Chifeng",
        "æŠšå·ž": "Fuzhou",
        "æ¼¯æ²³": "Luohe",
        "çœ‰å±±": "Meishan",
        "ä¸œè¥": "Dongying",
        "é“œä»": "Tongren",
        "æ±‰ä¸­": "Hanzhong",
        "é»„å±±": "Huangshan",
        "é˜³æ±Ÿ": "Yangjiang",
        "å¤§ç†": "Dali",
        "ç›˜é”¦": "Panjin",
        "è¾¾å·ž": "Dazhou",
        "æ‰¿å¾·": "Chengde",
        "çº¢æ²³": "Honghe",
        "ç™¾è‰²": "Baise",
        "ä¸¹ä¸œ": "Dandong",
        "ç›Šé˜³": "Yiyang",
        "æ¿®é˜³": "Puyang",
        "æ²³æº": "Heyuan",
        "é“œé™µ": "Tongling",
        "é„‚å·ž": "Ezhou",
        "å†…æ±Ÿ": "Neijiang",
        "æ¢§å·ž": "Wuzhou",
        "æ·®åŒ—": "Huaibei",
        "å®‰é¡º": "Anshun",
        "æ™‹åŸŽ": "Jincheng",

        # å¤–å›½ä¸»è¦åŸŽå¸‚
        "å¤å¨å¤·æª€é¦™å±±": "Honolulu",
        "é˜¿æ‹‰æ–¯åŠ å®‰å…‹é›·å¥‡": "Anchorage",
        "æ¸©å“¥åŽ": "Vancouver",
        "æ—§é‡‘å±±": "San Francisco",
        "è¥¿é›…å›¾": "Seattle",
        "æ´›æ‰çŸ¶": "Los Angeles",
        "é˜¿å…‹æ‹‰ç»´å…‹": "Aklavik",
        "è‰¾å¾·è’™é¡¿": "Edmonton",
        "å‡°åŸŽ": "Phoenix",
        "ä¸¹ä½›": "Denver",
        "å¢¨è¥¿å“¥åŸŽ": "Mexico City",
        "æ¸©å°¼ä¼¯": "Winnipeg",
        "ä¼‘æ–¯æ•¦": "Houston",
        "æ˜Žå°¼äºšæ³¢åˆ©æ–¯": "Minneapolis",
        "åœ£ä¿ç½—": "St. Paul",
        "æ–°å¥¥å°”è‰¯": "New Orleans",
        "èŠåŠ å“¥": "Chicago",
        "è’™å“¥é©¬åˆ©": "Montgomery",
        "å±åœ°é©¬æ‹‰": "Guatemala",
        "åœ£è¨å°”ç“¦å¤š": "San Salvador",
        "ç‰¹å¤è¥¿åŠ å°”å·´": "Tegucigalpa",
        "é©¬é‚£ç“œ": "Managua",
        "å“ˆç“¦é‚£": "Havana",
        "å°åœ°å®‰çº³æ³¢åˆ©æ–¯": "Indianapolis",
        "äºšç‰¹å…°å¤§": "Atlanta",
        "åº•ç‰¹å¾‹": "Detroit",
        "åŽç››é¡¿": "Washington DC",
        "è´¹åŸŽ": "Philadelphia",
        "å¤šä¼¦å¤š": "Toronto",
        "æ¸¥å¤ªåŽ": "Ottawa",
        "æ‹¿éªš": "Nassau",
        "åˆ©é©¬": "Lima",
        "é‡‘æ–¯æ•¦": "Kingston",
        "æ³¢å“¥å¤§": "Bogota",
        "çº½çº¦": "New York",
        "è’™ç‰¹åˆ©å°”": "Montreal",
        "æ³¢å£«é¡¿": "Boston",
        "åœ£å¤šæ˜Žå„": "Santo Domingo",
        "æ‹‰å¸•å…¹": "La Paz",
        "åŠ æ‹‰åŠ æ–¯": "Caracas",
        "åœ£èƒ¡å®‰": "San Juan",
        "å“ˆé‡Œæ³•å…‹æ–¯": "Halifax",
        "åœ£åœ°äºšå“¥": "Santiago",
        "äºšæ¾æ£®": "Asuncion",
        "å¸ƒå®œè¯ºæ–¯è‰¾åˆ©æ–¯": "Buenos Aires",
        "è’™ç‰¹ç»´çš„äºš": "Montevideo",
        "å·´è¥¿åˆ©äºš": "Brasilia",
        "åœ£ä¿ç½—": "Sao Paulo",
        "é‡Œçº¦çƒ­å†…å¢": "Rio de Janeiro",
        "é›·å…‹é›…æœªå…‹": "Reykjavik",
        "é‡Œæ–¯æœ¬": "Lisbon",
        "å¡è¨å¸ƒå…°å¡": "Casablanca",
        "éƒ½æŸæž—": "Dublin",
        "ä¼¦æ•¦": "London",
        "é©¬å¾·é‡Œ": "Madrid",
        "å·´å¡žç½—é‚£": "Barcelona",
        "å·´é»Ž": "Paris",
        "æ‹‰å„æ–¯": "Lagos",
        "é˜¿å°”åŠå°”": "Algiers",
        "å¸ƒé²å¡žå°”": "Brussels",
        "é˜¿å§†æ–¯ç‰¹ä¸¹": "Amsterdam",
        "æ—¥å†…ç“¦": "Geneva",
        "è‹é»Žä¸–": "Zurich",
        "æ³•å…°å…‹ç¦": "Frankfurt",
        "å¥¥æ–¯é™†": "Oslo",
        "å“¥æœ¬å“ˆæ ¹": "Copenhagen",
        "ç½—é©¬": "Rome",
        "æŸæž—": "Berlin",
        "å¸ƒæ‹‰æ ¼": "Prague",
        "è¨æ ¼é›·å¸ƒ": "Zagreb",
        "ç»´ä¹Ÿçº³": "Vienna",
        "æ–¯å¾·å“¥å°”æ‘©": "Stockholm",
        "å¸ƒè¾¾ä½©æ–¯": "Budapest",
        "è´å°”æ ¼èŽ±å¾·": "Belgrade",
        "åŽæ²™": "Warsaw",
        "å¼€æ™®æ•¦": "Cape Town",
        "ç´¢éžäºš": "Sofia",
        "é›…å…¸åŸŽ": "Athens",
        "å¡”æž—": "Tallinn",
        "èµ«å°”è¾›åŸº": "Helsinki",
        "å¸ƒåŠ å‹’æ–¯ç‰¹": "Bucharest",
        "æ˜Žæ–¯å…‹": "Minsk",
        "çº¦ç¿°å°¼æ–¯å ¡": "Johannesburg",
        "ä¼Šæ–¯å¦å¸ƒå°”": "Istanbul",
        "åŸºè¾…": "Kyiv",
        "æ•–å¾·è¨": "Odesa",
        "å“ˆæ‹‰é›·": "Harare",
        "å¼€ç½—": "Cairo",
        "å®‰å¡æ‹‰": "Ankara",
        "è€¶è·¯æ’’å†·": "Jerusalem",
        "è´é²ç‰¹": "Beirut",
        "å®‰æ›¼": "Amman",
        "å–€åœŸç©†": "Khartoum",
        "å†…ç½—æ¯•": "Nairobi",
        "èŽ«æ–¯ç§‘": "Moscow",
        "äºšçš„æ–¯äºšè´å·´": "Addis Ababa",
        "å·´æ ¼è¾¾": "Baghdad",
        "äºšä¸": "Aden",
        "åˆ©é›…å¾—": "Riyadh",
        "å®‰å¡”é‚£é‚£åˆ©ä½›": "Antananarivo",
        "ç§‘å¨ç‰¹åŸŽ": "Kuwait City",
        "å¾·é»‘å…°": "Tehran",
        "é˜¿å¸ƒæ‰Žæ¯”": "Abu Dhabi",
        "å–€å¸ƒå°”": "Kabul",
        "å¡æ‹‰å¥‡": "Karachi",
        "å¡”ä»€å¹²": "Tashkent",
        "ä¼Šæ–¯å…°å ¡": "Islamabad",
        "æ‹‰åˆå°”": "Lahore",
        "å­Ÿä¹°": "Mumbai",
        "æ–°å¾·é‡Œ": "New Delhi",
        "æŸ¯å°”å–€å¡”": "Kolkata",
        "åŠ å¾·æ»¡éƒ½": "Kathmandu",
        "è¾¾å¡": "Dhaka",
        "ä»°å…‰": "Yangon",
        "é‡‘è¾¹": "Phnom Penh",
        "æ›¼è°·": "Bangkok",
        "æ²³å†…": "Hanoi",
        "é›…åŠ è¾¾": "Jakarta",
        "å‰éš†å¡": "Kuala Lumpur",
        "æ–°åŠ å¡": "Singapore",
        "ç€æ–¯": "Perth",
        "é©¬å°¼æ‹‰": "Manila",
        "é¦–å°”": "Seoul",
        "ä¸œäº¬": "Tokyo",
        "è¾¾å°”æ–‡": "Darwin",
        "å¸ƒé‡Œæ–¯ç­": "Brisbane",
        "å¢¨å°”æœ¬": "Melbourne",
        "å ªåŸ¹æ‹‰": "Canberra",
        "æ‚‰å°¼": "Sydney",
        "äºšç‰¹é›·å¾·": "Adelaide",
        "å ªå¯ŸåŠ " :"Kamchatka",
        "é˜¿çº³å¾·å°”": "Anadyr",
        "è‹ç“¦": "Suva",
        "æƒ çµé¡¿": "Wellington",
        "æŸ¥å¡”å§†ç¾¤å²›": "Chatham Island",
        "åœ£è¯žå²›": "Kiritimati",
    }

    location_e2c = {}


    def __init__(
        self,
        cfg=None,
        max_search_nums=5,
        lang="wt-wt",
        max_retry_times=5,
        *args,
        **kwargs,
    ):
        self.cfg = cfg if cfg else Config()
        self.max_search_nums = max_search_nums
        self.max_retry_times = max_retry_times
        self.lang = lang
        for key in self.location_c2e:
            value = self.location_c2e[key]
            self.location_e2c[value] = key
            self.location_e2c[value.lower()] = key 


    def get_current_weather(self, location: str):
        """Get current weather"""
        if location == "default" or location == "Default" or location == "Default Country" or location == "default country":
            location = "Beijing"
        param = {"key": KEY, "q": location, "aqi": "yes"}
        res_completion = requests.get(URL_CURRENT_WEATHER, params=param)
        data = json.loads(res_completion.text.strip())
        if "error" in data.keys():
            return {"æŸ¥è¯¢ç»“æžœ": "error"}
        
        # print(data["current"])

        output = {}
        overall = translate_text(f"{data['current']['condition']['text']}")[0]
        output["æ•´ä½“å¤©æ°”"] = f"{overall}"
        if "temp_c" in data['current'] and data['current']['temp_c']:
            output[
                "æ°”æ¸©"
            ] = f"{data['current']['temp_c']}(Â°C)"
        if "precip_mm" in data['current'] and data['current']['precip_mm']:
            output[
                "é™é›¨é‡"
            ] = f"{data['current']['precip_mm']}(mm)"
        if "pressure_mb" in data['current'] and data['current']['pressure_mb']:
            output["æ°”åŽ‹"] = f"{data['current']['pressure_mb']}(ç™¾å¸•)"
        if "humidity" in data['current'] and data['current']['humidity']:
            output["æ¹¿åº¦"] = f"{data['current']['humidity']}"
        if "feelslike_c" in data['current'] and data['current']['feelslike_c']:
            output[
                "ä½“æ„Ÿæ¸©åº¦"
            ] = f"{data['current']['feelslike_c']}(Â°C)"
        if "vis_km" in data['current'] and data['current']['vis_km']:
            output[
                "èƒ½è§åº¦"
            ] = f"{data['current']['vis_km']}(km)"
        if "air_quality" in data["current"] and data['current']['air_quality']:
            output[
                "ç©ºæ°”è´¨é‡"
            ] = f"pm2.5: {round(data['current']['air_quality']['pm2_5'], 2)}(Î¼g/m3), pm10: {round(data['current']['air_quality']['pm10'], 2)}(Î¼g/m3)"

        return output

    def forecast_weather(self, location: str, date: str):
        """Forecast weather in the upcoming days."""
        if location == "default" or location == "Default" or location == "Default Country" or location == "default country":
            param = {"key": KEY, "q": "Beijing", "dt": date, "aqi": "yes"}
        else:
            param = {"key": KEY, "q": location, "dt": date, "aqi": "yes"}
        res_completion = requests.get(URL_FORECAST_WEATHER, params=param)
        res_completion = json.loads(res_completion.text.strip())
        if "error" in res_completion.keys():
            return {"æŸ¥è¯¢ç»“æžœ": "error"}
        
        res_completion_item = res_completion["forecast"]["forecastday"][0]
        output_dict = {}
        for k, v in res_completion_item["day"].items():
            output_dict[k] = v
        for k, v in res_completion_item["astro"].items():
            output_dict[k] = v
        output = {}
        output["æ—¥æœŸ"] = str(date)
        overall = translate_text(f"{output_dict['condition']['text']}")[0]
        output["æ•´ä½“å¤©æ°”"] = f"{overall}"
        output[
            "æœ€é«˜æ¸©åº¦"
        ] = f"{output_dict['maxtemp_c']}(Â°C)"
        output[
            "æœ€ä½Žæ¸©åº¦"
        ] = f"{output_dict['mintemp_c']}(Â°C)"
        output[
            "å¹³å‡æ¸©åº¦"
        ] = f"{output_dict['avgtemp_c']}(Â°C)"
        output["é™é›¨æ¦‚çŽ‡"] = f"{output_dict['daily_chance_of_rain']}"
        output["é™é›ªæ¦‚çŽ‡"] = f"{output_dict['daily_will_it_snow']}"
        output[
            "å¹³å‡èƒ½è§åº¦"
        ] = f"{output_dict['avgvis_km']}(km)"
        output["å¹³å‡æ¹¿åº¦"] = f"{output_dict['avghumidity']}"
        output["æ—¥å‡ºæ—¶é—´"] = f"{output_dict['sunrise']}"
        output["æ—¥è½æ—¶é—´"] = f"{output_dict['sunset']}"
        if "air_quality" not in output_dict.keys() or len(output_dict["air_quality"].keys()) == 0:
            output["ç©ºæ°”è´¨é‡"] = ""
        else:
            output[
                "ç©ºæ°”è´¨é‡"
            ] = f"pm2.5: {round(output_dict['air_quality']['pm2_5'], 2)}(Î¼g/m3), pm10: {round(output_dict['air_quality']['pm10'], 2)}(Î¼g/m3)"

        return output

    def get_history_weather(self, location: str, date: str):
        """Find weather of a past date."""
        if location == "default" or location == "Default" or location == "Default Country" or location == "default country":
            param = {"key": KEY, "q": "Beijing", "dt": date}
        else:
            param = {"key": KEY, "q": location, "dt": date}
        
        res_completion = requests.get(URL_HISTORY_WEATHER, params=param)
        res_completion = json.loads(res_completion.text.strip())
        if "error" in res_completion.keys():
            return {"æŸ¥è¯¢ç»“æžœ": "error"}

        res_completion = res_completion["forecast"]["forecastday"][0]
        output_dict = {}
        for k, v in res_completion["day"].items():
            output_dict[k] = v
        for k, v in res_completion["astro"].items():
            output_dict[k] = v

        output = {}
        output["æ—¥æœŸ"] = str(date)
        overall = translate_text(f"{output_dict['condition']['text']}")[0]
        output["æ•´ä½“å¤©æ°”"] = f"{overall}"
        output[
            "æœ€é«˜æ¸©åº¦"
        ] = f"{output_dict['maxtemp_c']}(Â°C)"
        output[
            "æœ€ä½Žæ¸©åº¦"
        ] = f"{output_dict['mintemp_c']}(Â°C)"
        output[
            "å¹³å‡æ¸©åº¦"
        ] = f"{output_dict['avgtemp_c']}(Â°C)"
        output[
            "é™é›¨é‡"
        ] = f"{output_dict['totalprecip_mm']}(mm)"
        output[
            "å¹³å‡èƒ½è§åº¦"
        ] = f"{output_dict['avgvis_km']}(km)"
        output["å¹³å‡æ¹¿åº¦"] = f"{output_dict['avghumidity']}"
        output["æ—¥å‡ºæ—¶é—´"] = f"{output_dict['sunrise']}"
        output["æ—¥è½æ—¶é—´"] = f"{output_dict['sunset']}"

        return output

    def get_weather(self, location, start_date, end_date, is_current):
        start_date = fix_date_to_format(start_date)
        end_date = fix_date_to_format(end_date)
        if location == "default" or location == "Default" or location == "Default Country" or location == "default country":
            location_c = "åŒ—äº¬"
        # elif location in self.location_e2c.keys():
        #     location_c = self.location_e2c[location]
        else:
            location_c = self.location_e2c[location]

        final_dict = {}
        
        date_list = get_date_list(start_date, end_date)

        # èŽ·å–çŽ°åœ¨çš„æ—¶é—´
        curr_date = str(datetime.now())[:10]
        # å…¨éƒ½æ˜¯history
        if end_date <= curr_date:
            res = []
            for d in date_list:
                if d == curr_date:
                    try:
                        res.append(self.get_history_weather(location, d))
                    except:
                        res.append(self.forecast_weather(location, d))
                else:
                    res.append(self.get_history_weather(location, d))
                
            if start_date == end_date:
                final_dict[f"{location_c}{start_date}å¤©æ°”"] = res
            else:
                final_dict[f"{location_c}{start_date}è‡³{end_date}å¤©æ°”"] = res

        # å…¨éƒ½æ˜¯forecast
        elif start_date > curr_date:
            res = []
            i = 0
            for d in date_list:
                if i >= 10:
                    break
                res.append(self.forecast_weather(location, d))
                i += 1
            if start_date == end_date:
                final_dict[f"{location_c}{start_date}å¤©æ°”é¢„æŠ¥"] = res
            else:
                final_dict[f"{location_c}{start_date}è‡³{end_date}å¤©æ°”é¢„æŠ¥"] = res

        else:
            res = []
            # æœ‰çš„æ˜¯historyï¼Œæœ‰çš„æ˜¯forecast
            past_date_list = get_date_list(start_date, curr_date)
            future_date_list = (get_date_list(curr_date, end_date))[1:]
            for d in past_date_list:
                if d == curr_date:
                    try:
                        res.append(self.get_history_weather(location, d))
                    except:
                        res.append(self.forecast_weather(location, d))
                else:
                    res.append(self.get_history_weather(location, d))

            if start_date == curr_date:
                final_dict[f"{location_c}{start_date}å¤©æ°”"] = res
            else:
                final_dict[f"{location_c}{start_date}è‡³{curr_date}å¤©æ°”"] = res
            res = []
            i = 0
            for d in future_date_list:
                if i >= 10:
                    break
                res.append(self.forecast_weather(location, d))
                i += 1
            if future_date_list[0] == end_date:
                final_dict[f"{location_c}{end_date}å¤©æ°”é¢„æŠ¥"] = res
            else:
                final_dict[f"{location_c}{future_date_list[0]}è‡³{end_date}å¤©æ°”é¢„æŠ¥"] = res


        if is_current == "yes":

            final_dict[f"æ­¤æ—¶æ­¤åˆ»{location_c}å¤©æ°”"] = [self.get_current_weather(location)]

        return final_dict


    def __call__(self, start_date, end_date, is_current="yes", location="Beijing", *args, **kwargs):
        
        final_res = {
            "location": location,
            "start_date": start_date,
            "end_date": end_date
        }

        # å¦‚æžœè¿˜æ˜¯ç»™äº†å¤šä¸ªåœ°å€
        if ',' in location:
            location_list = location.split(',')
        elif 'ï¼Œ' in location:
            location_list = location.split('ï¼Œ')
        else:
            location_list = [location]
        
        for location_ in location_list:
            location_ = location_.strip()
            # å¦‚æžœç»™çš„æ˜¯ä¸­æ–‡ï¼Œä¸”åœ¨å­—å…¸ä¸­ï¼Œåˆ™æŸ¥å­—å…¸ç¿»è¯‘
            if location_ in self.location_c2e.keys():
                loc = self.location_c2e[location_]
            # å¦‚æžœç»™çš„æ˜¯ä¸­æ–‡ï¼Œä¸”ä¸åœ¨å­—å…¸ä¸­ï¼Œç›´æŽ¥è¿”å›žç»“æžœä¸å­˜åœ¨
            elif not (32 <= ord(location_[0]) <= 126):
                final_res['æŸ¥è¯¢ç»“æžœ'] = 'error'
                return WeatherResult(final_res)
            # å¦‚æžœæ˜¯è‹±æ–‡ï¼Œä¸”åœ¨å­—å…¸ä¸­ï¼Œç›´æŽ¥è¾“è¿›åŽ»
            elif location_ in self.location_e2c.keys():
                loc = location_
            # å¦‚æžœæ˜¯è‹±æ–‡ï¼Œä¸”ä¸åœ¨å­—å…¸ä¸­ï¼Œè¿”å›žä¸å­˜åœ¨
            else:
                final_res['æŸ¥è¯¢ç»“æžœ'] = 'error'
                return WeatherResult(final_res)
            # print(loc)
            
            if is_current == "æ˜¯":
                is_cur = "yes"
            elif is_current == "å¦" or is_current == "ä¸æ˜¯":
                is_cur = "no"
            else:
                is_cur = is_current
            try:
                result = self.get_weather(
                        loc, start_date, end_date, is_cur
                    )
                final_res.update(result)
            except:
                print(traceback.format_exc())
                final_res['æŸ¥è¯¢ç»“æžœ'] = 'error'

        return WeatherResult(final_res)
