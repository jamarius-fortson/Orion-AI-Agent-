#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: PAN Leyi
# Email:  panleyi@kuaishou.com


from orionagent.tools.base import BaseResult, BaseTool
from datetime import datetime
from ephem import *
import math

solar_terms = ["å°å¯’", "å¤§å¯’", "ç«‹æ˜¥", "é›¨æ°´", "æƒŠè›°", "æ˜¥åˆ†", "æ¸…æ˜Ž", "è°·é›¨", "ç«‹å¤", "å°æ»¡", "èŠ’ç§",
    "å¤è‡³", "å°æš‘", "å¤§æš‘", "ç«‹ç§‹", "å¤„æš‘", "ç™½éœ²", "ç§‹åˆ†", "å¯’éœ²", "éœœé™", "ç«‹å†¬", "å°é›ª", "å¤§é›ª", "å†¬è‡³"]


class SolarTermsResult(BaseResult):
    @property
    def answer(self):
        if not self.json_data:
            return ""
        else:
            item = self.json_data
            print(item)
            rst = ""
            for main_key in item.keys():
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


class SolarTermsTool(BaseTool):
    """
    Retrieve solar terms in Chinese for a given year. 

    Args:
        year (int): Target year for query.

    Returns:
        str: Solar terms information of the given year.
    """
    name = "get_solar_terms_info"
    zh_name = "æŸ¥è¯¢èŠ‚æ°”æ—¥æœŸ"
    description = 'Get solar terms info:"get_solar_terms_info", args:"year": <int, required>'
    tips = "get_solar_terms_info retrieve solar terms in Chinese for a given year."

    def __init__(
        self,
        max_search_nums=5,
        lang="wt-wt",
        max_retry_times=5,
        *args,
        **kwargs,
    ):
        self.max_search_nums = max_search_nums
        self.max_retry_times = max_retry_times
        self.lang = lang

    def __call__(self, year, *args, **kwargs):
        # è®¡ç®—é»„ç»
        def ecliptic_lon(jd_utc):
            s = Sun(jd_utc)  # æž„é€ å¤ªé˜³
            equ = Equatorial(
                s.ra, s.dec, epoch=jd_utc
            )  # æ±‚å¤ªé˜³çš„è§†èµ¤ç»è§†èµ¤çº¬ï¼ˆepochè®¾ä¸ºæ‰€æ±‚æ—¶é—´å°±æ˜¯è§†èµ¤ç»è§†èµ¤çº¬ï¼‰
            e = Ecliptic(equ)  # èµ¤ç»èµ¤çº¬è½¬åˆ°é»„ç»é»„çº¬
            return e.lon  # è¿”å›žé»„çº¬

        # æ ¹æ®æ—¶é—´æ±‚å¤ªé˜³é»„ç»ï¼Œè®¡ç®—åˆ°äº†ç¬¬å‡ ä¸ªèŠ‚æ°”ï¼Œæ˜¥åˆ†åºå·ä¸º0
        def sta(jd):
            e = ecliptic_lon(jd)
            n = int(e * 180.0 / math.pi / 15)
            return n

        # æ ¹æ®å½“å‰æ—¶é—´ï¼Œæ±‚ä¸‹ä¸ªèŠ‚æ°”çš„å‘ç”Ÿæ—¶é—´
        def iteration(jd, sta):  # jdï¼šè¦æ±‚çš„å¼€å§‹æ—¶é—´ï¼Œstaï¼šä¸åŒçš„çŠ¶æ€å‡½æ•°
            s1 = sta(jd)  # åˆå§‹çŠ¶æ€(å¤ªé˜³å¤„äºŽä»€ä¹ˆä½ç½®)
            s0 = s1
            dt = 1.0  # åˆå§‹æ—¶é—´æ”¹å˜é‡è®¾ä¸º1å¤©
            while True:
                jd += dt
                s = sta(jd)
                if s0 != s:
                    s0 = s
                    dt = -dt / 2  # ä½¿æ—¶é—´æ”¹å˜é‡æŠ˜åŠå‡å°
                if abs(dt) < 0.0000001 and s != s1:
                    break
            return jd
        
        res = []
        jd = Date(datetime(int(year), 1, 1, 0, 0, 0))
        e = ecliptic_lon(jd)
        for i in range(24):
            jd = iteration(jd, sta)
            d = Date(jd + 1 / 3).tuple()
            res.append({"èŠ‚æ°”": solar_terms[i], "æ—¥æœŸ": "{0}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:02d}".format(d[0], d[1], d[2], d[3], d[4], int(d[5]))})

        return SolarTermsResult({
                f"{year}å¹´èŠ‚æ°”è¡¨": res
            })

