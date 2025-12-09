from binance.um_futures import UMFutures
#import finplot as fplt
import pandas as pd
import pandas_ta as ta
import numpy as np
import time
import websocket
import websockets
import threading
import json
import telebot
import datetime
import statistics
import asyncio
import requests
import mplfinance as mpf
import csv
import joblib
import openpyxl
import xlsxwriter
import io
from datetime import datetime as dt
from datetime import timedelta, timezone
from matplotlib import pyplot as plt
from memory_profiler import profile
from scipy.signal import argrelextrema
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error as mae # для подсчета ширины канала
import matplotlib 
from scipy.signal import savgol_filter, find_peaks
matplotlib.use("agg")

key = '###'


stat_tg = '-###' 
screen_tg = '-###' # ver5
red_stop_tg = '-###'
screen_v20 = '-###'
max_8_take_40_tg = '-###'
clear_pnl_10_tg = '-###'
take_clear_pnl_80_tg = '-###'
error_tg = '-###'  
stat_tg = '-###'
TG_Bot_token = "###"   
# TG_Bot_token='###'  
client = UMFutures(key=key) # клиент для бинанса, КЛЮЧ обязателен для выгрузки трейдов
smooth_emoji = '🌊🌊🌊'
fast_emoji  = '💥💥💥'
btc_emoji = '‼️‼️‼️‼️‼️'
long_emoji = '🟢'
p_emoji = '❗️'
legendary_16 = '❗️❗️❗️❗️'
legendary_20 = '❗️❗️❗️❗️❗️'
legendary_30 = '🤯🤯🤯🤯🤯'
legendary_40 = '☠️☠️☠️☠️☠️'
legendary_60 = '🌋🗽🌋🗽'
legendary_100 = '🩻🤖🩻🤖🩻'
stats_emoji = '📈📈📈📈📈'

time_frame = '1m'

bot = telebot.TeleBot(TG_Bot_token)

f = open('/projects/data/price_acc.txt', 'r')
last = f.read()
price_acc = json.loads(last)
f.close()

symbols = []
for key in price_acc:
    symbols.append(key)

try:
    f = open('/projects/Ver33/stats/alerts_stat.txt', 'r')
    last = f.read()
    alerts_stat = json.loads(last)
    f.close()
except:
    alerts_stat = {'all_clear': float(0.0), 'all_potential': float(0.0), 'all_count_per_day':int(0), 'wtp_potential':float(0.0), 'wtp_clear': float(0.0), 'wtp_count': int(0), 'commission': float(0.0), 'commission_wtp': float(0.0)}

try:
    f = open('/projects/Ver33/stats/day_check.txt', 'r')
    last = f.read()
    day_check = json.loads(last)
    f.close()
except:
    day_check = 0

try:
    f = open('/projects/Ver33/stats_4h/alerts_stat_4h.txt', 'r')
    last = f.read()
    alerts_stat_4h = json.loads(last)
    f.close()
except:
    alerts_stat_4h = {'clear': float(0.0), 'potential': float(0.0), 'wtp_clear':int(0), 'wtp_potential':float(0.0)}

try:
    f = open('/projects/Ver33/stats_4h/alerts_stat_1h.txt', 'r')
    last = f.read()
    alerts_stat_1h = json.loads(last)
    f.close()
except:
    alerts_stat_1h = {'plus_30': [0,0,0], 'plus_20': [0,0,0], 'plus_16': [0,0,0], 'plus_12': [0,0,0], 'plus_6': [0,0,0],
                       'plus_3': [0,0,0], 'plus_1.5': [0,0,0], 'noise': [0,0,0], 'minus_1.5': [0,0,0], 'minus_3': [0,0,0], 
                       'minus_6': [0,0,0], 'minus_12': [0,0,0], 'minus_16': [0,0,0], 'minus_20': [0,0,0], 'minus_30': [0,0,0]}

сap_name_1h = ['P!!!!!+', 'P!!!!!', 'P!!!!', 'P!!!', 'P!!', 'P!', 'P', 'N', 'D', 'D!', 'D!!', 'D!!!', 'D!!!!', 'D!!!!!', 'D!!!!!+'] 


try:
    f = open('/projects/Ver33/stats_4h/hour_check_1h.txt', 'r')
    last = f.read()
    hour_check_1h = json.loads(last)
    f.close()
except:
    hour_check_1h = 0

try:
    
    f = open('/projects/Ver33/channel_price.txt', 'r')
    last = f.read()
    channel_price = json.loads(last)
    f.close()
    f = open('/projects/Ver33/channel_time.txt', 'r')
    last = f.read()
    channel_time = json.loads(last)
    f.close()
    f = open('/projects/Ver33/alerts_MT.txt', 'r')
    last = f.read()
    alerts_MT = json.loads(last)
    f.close()

except:
    
    channel_price = {symbol: [[],[]] for symbol in symbols}
    channel_time = {symbol: [[],[]] for symbol in symbols}
    alerts_MT = {symbol: [0,0] for symbol in symbols}

try:
    f = open('/projects/Ver33/channel_cond.txt', 'r')
    last = f.read()
    channel_cond = json.loads(last)
    f.close()
except:
    channel_cond = {symbol: [[],[]] for symbol in symbols}

symbols_old = []
for key in alerts_MT:            
    symbols_old.append(key)


####### volume classifier ############
# словарь порогов для антифрода от 0506
LIMITS_VOL = {"label": ['v1/avg', 'v2/avg', 'v2/v1'],
                0:       [2,         0.0001,   0.0001],
                1:       [3.15,      0.5,      0.0001],
                2:       [4.3,       0.8,      0.0001],
                3:       [5.0,       1.1,      0.0001],
                4:       [5.7,       1.8,      0.0001],
                5:       [6.4,       2.5,      0.06  ],
                "comment": ['во сколько раз объёмы 1 свечи выше средних ДО A1', 
                            'во сколько раз объёмы 2 свечи выше средних ДО A1', 
                            'во сколько раз объёмы 1 свечи выше чем на 2 свече']}

def max_vol(x, max_v):
    if x >= max_v:
        return x/5
    else:
        return x

def vol_features_calc(data_in, alert_time=None):
    data = data_in.reset_index(drop=True).copy()      # без copy() меняем значение в базе, особенно важно при повторных запусках!
    if "Time_alert" in data.columns:
        alert_time = data.loc[data.index[0], 'Time_alert'] // 60000 * 60000     ### перестраховка, чтобы не было ошибок с timestamp
        ind = data[data['Time'] >= alert_time].index.values.astype(int)[0]
    elif alert_time:
        ind = data[data['Time'] >= int(alert_time)].index.values.astype(int)[0]
    else:
        print("не задано время алерта, беру 90 минут от начала датафрейма")
        ind = 90    
    data = data.loc[ind - 90:].copy().reset_index(drop=True)  # на случай приёма более 90 минут до А1
    
    for _ in range(5):
        max_volume = max(data.loc[: ind - 10, 'Volume'])   # подрезаю только на отрезке ДО А1 (-90:-10 мин.)
        data.loc[: ind - 10, 'Volume'] = data.loc[: ind - 10, 'Volume'].apply(lambda x: max_vol(x, max_volume))

    avg_vol = statistics.mean(data.loc[: ind - 10, 'Volume'])  # также только на отрезке ДО А1 (-90:-10 мин.)
    avg1 = round(float(data.iloc[ind]['Volume']) / avg_vol, 2)
    avg2 = round(float(data.iloc[ind + 1]['Volume']) / avg_vol, 2)
    features_tpl = (avg1, avg2, round(float(data.loc[ind + 1, 'Volume']) / float(data.loc[ind, 'Volume']), 2))
    return features_tpl

def vol_marc_detect(features_tpl, LIMITS_VOL):
    mark = 6                                        # 6 == хорошо
    for mrk in (0, 1, 2, 3, 4, 5):
        iterator = zip(LIMITS_VOL[mrk], features_tpl, LIMITS_VOL["label"])
        labels = [f"{lab} < {lim}" for lim, val, lab in iterator if abs(val) < lim]
        if len(labels) > 0:
            mark = mrk
            break
    return mark, "\n    ".join(labels)


# новый словарь порогов для объемов с 0.5 от 0506
LIMITS_V05 = {
    "label": ["maxV_10min_b", "maxV_10min_a1", "maxV_5min_a1", "trN_10min_a1", "trN_5min_a1", "maxGreenV_5_a1", "avgGreenV_10_b"], 
    0:       [ 0.001,          0.98,            0.71,           0.95,           0.75,          0.001,            0.001          ],
    1:       [ 1.0,            1.22,            0.82,           1,              0.75,          0.8,              0.6            ],
    2:       [ 1.35,           1.27,            3.77,           1.11,           0.76,          1.17,             0.71           ],
    3:       [ 1.38,           1.41,            6.58,           1.11,           0.76,          1.91,             1.17           ],
    4:       [ 1.9,            1.9,             7,              1.29,           1.14,          2.12,             2.73           ],
    5:       [ 3.0,            2.89,            8,              1.85,           5.69,          3.95,             5              ],
    8:       [ 1000,           1000,            30,             1000,           1000,          1000,             1000           ],
    10:      [ 1000,           1000,            60,             1000,           1000,          1000,             1000           ],
    12:      [ 1000,           100,             100,            1000,           1000,          1000,             1000           ],
    "comment": ['макс.объём за 10 мин. к ср.объёмам до 0.5', 
                'макс.объём за 10 мин. к ср.объёмам до A1',
                'макс.объём за 5 мин. к ср.объёмам до A1', 
                'макс.число трейдов за 10 мин. к ср.числу до A1', 
                'макс.число трейдов за 5 мин. к ср.числу до A1', 
                'макс.зелёный объём за 5 мин. к ср.зелёным до А1',
                'сред.зелёный объём за 10 мин. к ср.зелёным до 0.5']
}
# pd.DataFrame(LIMITS_V05)  # отобразить таблицу лимитов с описанием

def get_05_time(data_in, alert_time=None, alert_price=None):
    """Определяет таймштамп достижения ценой 0.5, если не задан"""
    # эти две вспомогательные функции применял для определения времени 0.5
    # по идее, если время задаётся, они не нужны.
    # Но если   first_time_trade  не будет определяться, v05_calc() будет обращаться к ним    
    data = data_in.reset_index(drop=True).copy() 
    if "Time_alert" in data.columns:
        alert_time = data.loc[data.index[0], 'Time_alert'] // 60000 * 60000
        ind = data[data['Time'] >= alert_time].index.values.astype(int)[0]
    elif alert_time:
        ind = data[data['Time'] >= int(alert_time) // 60000 * 60000].index.values.astype(int)[0]
    else:
        print("не задано время алерта, беру 90 минут от начала датафрейма")
        ind = 90  
    if (not alert_price) and ("Price_alert" in data.columns):
        alert_price = float(data.Price_alert.values[0])
    elif (not alert_price) and ("Close" in data.columns):
        print("не задана цена алерта, беру цену закрытия минуты алерта")
        alert_price = float(data.loc[ind, "Close"])
    time_ser = data.loc[ind: ind + 121].loc[data.High >= alert_price * 1.005, "Time"]
    if len(time_ser) == 0:
        return 0
    else:
        time05 = int(time_ser.iloc[0]) // 60000 * 60000
        if data.loc[data['Time'] == time05, "High"].iloc[0] < 1.005 * alert_price:
            time05 = time05 + 60000
        return time05
    
def dt2ts(dtime: str) -> int:
    """Переврдит строку дату-время МОСКОВСКОЕ в метку времени"""
    dt_str = str(dtime).partition(".")[0].replace("T", " ").partition("+")[0]
    dt_str = f'{dt_str}.+0300'
    return int(dt_str.strptime(dt_str, '%Y-%m-%d %H:%M:%S.%z').timestamp()) * 1000    

def vol_05_calc(data_in, alert_time=None, first_time_trade=None):
    """Считатет 7 параметров объёмов в минуту 0.5"""
    data = data_in.reset_index(drop=True).copy()      # без copy() меняем значение в базе

    if "Time_alert" in data.columns:
        alert_time = data.loc[data.index[0], 'Time_alert'] // 60000 * 60000
        ind = data[data['Time'] >= alert_time].index.values.astype(int)[0]
    elif alert_time:
        try:
            alert_time = dt2ts(alert_time) 
        except: pass
        ind = data[data['Time'] >= int(alert_time) // 60000 * 60000].index.values.astype(int)[0]
    else:
        print("не задано время алерта, беру 90 минут от начала датафрейма")
        ind = 90    
    data = data.loc[ind - 90:].reset_index(drop=True)  # на случай приёма более 90 минут до А1
    
    if first_time_trade is None:
        first_time_trade = get_05_time(data, alert_time=alert_time)
    ind05 = data[data['Time'] >= int(first_time_trade) // 60000 * 60000].index.values.astype(int)[0]

    if not first_time_trade or not ind05:
        return [0.000001] * 7 + [-89]      # нет 0.5
    
    ind05 = max(90, ind05)
    avg_green_vol = statistics.mean(data.loc[: ind - 10, 'Taker buy base asset volume'])
    avg_vol = statistics.mean(data.loc[: ind - 10, 'Volume'])  # также только на отрезке ДО А1 (-90:-10 мин.)
    avg_vg90b = data.iloc[ind05 - 90: ind05 - 10]['Taker buy base asset volume'].mean()
    avg_v90b = data.iloc[ind05 - 90: ind05 - 10]['Volume'].mean()
    avg_n_a1 = statistics.mean(data.loc[ind - 90: ind - 10, 'Number of trades'])  # также только на отрезке ДО А1 (-90:-10 мин.)

    maxV_10min_b = round(data.iloc[ind05 - 9: ind05 + 1]['Volume'].max() / avg_v90b, 2)            # макс.объём за 10 мин. к ср.объёмам до 0.5
    maxV_10min_a1 = round(data.iloc[ind05 - 9: ind05 + 1]['Volume'].max() / avg_vol, 2)            # макс.объём за 10 мин. к ср.объёмам до A1
    maxV_5min_a1 = round(data.iloc[ind05 - 4: ind05 + 1]['Volume'].max() / avg_vol, 2)             # макс.объём за 5 мин. к ср.объёмам до A1
    trN_10min_a1 = round(data.iloc[ind05 - 9: ind05 + 1]['Number of trades'].max() / avg_n_a1, 2)  # макс.число трейдов за 10 мин. к ср.числу до A1
    trN_5min_a1 = round(data.iloc[ind05 - 4: ind05 + 1]['Number of trades'].max() / avg_n_a1, 2)   # макс.число трейдов за 5 мин. к ср.числу до A1
    maxGreenV_5_a1 = round(data.iloc[ind05 - 4: ind05 + 1]['Taker buy base asset volume'].max() / avg_green_vol, 2)  # макс.зелёный объём за 5 мин. к ср.зелёным до А1
    avgGreenV_10_b = round(data.iloc[ind05 - 9: ind05+1]['Taker buy base asset volume'].mean() / avg_vg90b, 2)       # сред.зелёный объём за 10 мин. к ср.зелёным до 0.5

    return maxV_10min_b, maxV_10min_a1, maxV_5min_a1, trN_10min_a1, trN_5min_a1, maxGreenV_5_a1, avgGreenV_10_b, ind05 - 90

def vol_05_marc_detect(features_tpl, LIMITS_V05=LIMITS_V05):
    """Ставит оценку и комментарий по 7 параметрам объёмов с 0.5"""
    for mrk in range(6):
        iterator = zip(LIMITS_V05[mrk], features_tpl[:7], LIMITS_V05["label"])
        labels = [f"{lab} < {lim}" for lim, val, lab in iterator if abs(val) < lim]
        if len(labels) > 0:
            return mrk, "\n    ".join(labels)
    for mrk in range(12, 6, -2):
        iterator = zip(LIMITS_V05[mrk], features_tpl[:7], LIMITS_V05["label"])
        labels = [f"{lab} > {lim}" for lim, val, lab in iterator if abs(val) > lim]
        if len(labels) > 0:
            return mrk, "\n    ".join(labels)
    return 6, ""

####### volume classifier ############
# словарь порогов для антифрода от 0506
LIMITS_SHL = {
    "label": ['total_real', 'total_33', 'short_real', 'long_real', 'short2_real', 'short2_time'], 
    0:       [12.1,          10.1,       8.0,          9.7,         8.4,           100         ],
    1:       [11.15,         8.4,        6.25,         7.9,         6.3,           100         ],
    2:       [10.2,          6.7,        4.5,          6.1,         4.2,           100         ],
    3:       [9.55,          5.9,        4.4,          4.5,         3.85,          100         ],
    4:       [8.9,           5.1,        4.3,          2.9,         3.5,           60.0        ],
    5:       [8.0,           4.3,        3.5,          2.5,         3.15,          36.0        ],
    "comment": [
        'суммарный % шорт-лонг реализации ДО A1', 'лонг-реализация 100% + шорт-реализация 33%',
        'абсолюное занчение 1й шорт-реализации в %', 'абсолюное занчение лонг-реализации в %',
        'абсолюное занчение 2й шорт-реализации в %', 'долгая 2я шорт-реал. (разница с лонг в мин.)'
    ]
}

def realis_calc(hi, lo, alert_price):
    """Считает числовые параметры шорт/лонг реализации по спискам Hi и Low за 90 минут до А1"""
    if lo[2:-2] == []:
        bot.send_message(error_tg, f"ver 9 lo[2:-2] == [] in realis_calc")  ### отладка - поиск min([])   -nk-
    low_p = min(lo[2:-2])
    low_t = lo.index(low_p, 2, -2)
    hi_p = max(hi[1:low_t])
    hi_t = hi.index(hi_p, 1, low_t)
    hi2_p = max(hi[low_t + 1: -1])
    hi2_t = hi.index(hi2_p, low_t + 1)
    low_p = round((low_p - alert_price) / alert_price * 100, 1)
    hi_p = round((hi_p - alert_price) / alert_price * 100, 1)
    hi2_p = round((hi2_p - alert_price) / alert_price * 100, 1)
    lo2_p = round((lo[-1] - alert_price) / alert_price * 100, 1)    
    sh_r = round(low_p - hi_p, 1)
    low_r = round(hi2_p - low_p, 1)
    sh2_r = round(lo2_p - hi2_p, 1)
    pts = [[(hi_t, hi_p), (low_t, low_p)], [(low_t, low_p), (hi2_t, hi2_p)], [(hi2_t, hi2_p), (len(lo) - 1, lo2_p)]]
    s2l = max(len(lo) - 1 + low_t - hi2_t * 2, 0) 
    if hi2_t >= len(lo) - 2:
        pts[1] = [pts[1][0], pts.pop(2)[1]]
        low_r = round(low_r + sh2_r, 1)
        sh2_r = 0
    tot_r = round(sum(x for x in (-sh_r, low_r, -sh2_r) if x > 1), 1)
    t33_r = round((low_r if low_r > 1 else 0) - 0.33 * sum(num for num in (-3, sh_r, sh2_r) if num < -1) - 0.99, 1)
    return pts, (tot_r, t33_r, sh_r, low_r, sh2_r, s2l)


def af_realis_detect(features_tpl):
    """Определяет превышен ли порог антифрода по одному из показателей"""
    
    global LIMITS_SHL
    
#     features_tpl = (sh_r + low_r + sh2_r, low_r + 0.33 * (sh_r + sh2_r), sh_r, low_r, sh2_r, s2l)
    mark = 6                                       # 6 хорошо
    for mrk in (0, 1, 2, 3, 4, 5):
        iterator = zip(LIMITS_SHL[mrk], features_tpl, LIMITS_SHL["label"])
        labs = [f"{lab} > {lim}" for lim, val, lab in iterator if abs(val) > lim]
        if len(labs) > 0:
            mark = mrk
            break
    return mark, "\n    ".join(labs)


# делаю отдельным словарём веса и порог суммы, которые будем ещё настраивать
# пороги, веса и проходной балл - лучшее комбо на 0806
WEIGHTS = {"vol_lim": 6, "v05_lim": 0, "real_lim": 0, "w30_lim": 0, "w5_lim": 0,
           "V": 0, "05": 1, "R": 1, "W": 1, "w": 7, "Total": 42}

############### long/short ############

symbol_new=list(set(symbols)-set(symbols_old))
if len(symbol_new) != 0:
    for symbol in symbol_new:
        channel_price[symbol] = [[],[]]
        channel_time[symbol] = [[],[]] 
        alerts_MT[symbol] = [1,1] 
        channel_cond[symbol] = [[],[]]

try:
    f = open('/projects/Ver33/count_trades.txt', 'r')
    last = f.read()
    count_trades = json.loads(last)
    f.close()
except:
    count_trades = 0


def send_photo(chat_id, file, cap):
        url = f'https://api.telegram.org/bot{TG_Bot_token}/sendPhoto'
        files = {'photo': file}
        data = {'chat_id': chat_id, "caption": cap}
        response = requests.post(url, files=files, data=data)
        json_response = response.json()
        return json_response

name_col_a1 = ['symbol', 'time_open', 'time_close', 'open_price', 'close_price', 'pnl',
               'predict_vol', 'predict_05_vol','long_short', 'w30_score', 'w5_score']


def ver_trade(symb, price_last_alert_algo_1, time_last_alert_algo_1, time_tick, price, alerts, trends):

        
        def kline_MT(i):    

            if alerts_MT[symb][i] == 1 and\
                trends[symb][-1][1] == 2 and trends[symb][-2][1] == 1:
                channel_price[symb][i] = channel_price[symb][i] + [price]
                channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                alerts_MT[symb][i] = 2
                channel_cond[symb][i] = channel_cond[symb][i] + ['switch']
                #bot.send_message(error_tg, f'{symb} kline_MT {i}\nswitch long')

            elif alerts_MT[symb][i] == 2 and\
                trends[symb][-1][1] == 1 and trends[symb][-2][1] == 2:
                channel_price[symb][i] = channel_price[symb][i] + [price]
                channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                alerts_MT[symb][i] = 1
                channel_cond[symb][i] = channel_cond[symb][i] + ['switch']
                #bot.send_message(error_tg, f'{symb} kline_MT {i}\nswitch short')

            elif (alerts_MT[symb][i] == 2 or alerts_MT[symb][i] == 1) and time_tick > time_last_alert_algo_1[symb][i] + 2 * 60 * 60 * 1000:
                alerts_MT[symb][i] = 3
                channel_price[symb][i] = channel_price[symb][i] + [price]
                channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                channel_cond[symb][i] = channel_cond[symb][i] + ['e']
                #bot.send_message(error_tg, f'{symb} kline_MT {i}\ne')

                    

        if alerts[symb][0] >= 1 and time_tick < time_last_alert_algo_1[symb][0] + 2.1 * 60 * 60 * 1000:
            try:
                
                
                kline_MT(0)
            except Exception as e:
                bot.send_message(error_tg, f'ver 33 kline_MT(0,k) fail {symb}\n\n{e}')

        if alerts[symb][1] >= 1 and time_tick < time_last_alert_algo_1[symb][1] + 2.1 * 60 * 60 * 1000:
            try:
                
                kline_MT(1)
            except Exception as e:
               bot.send_message(error_tg, f'ver 33 kline_MT(1,k) fail {symb}\n\n{e}')


def rewrite(symb, price, time, trends):
    try:
        channel_price[symb][0] = channel_price[symb][1]
        channel_time[symb][0] = channel_time[symb][1]
        channel_cond[symb][0] = channel_cond[symb][1]
        alerts_MT[symb][0] = alerts_MT[symb][1]

        channel_price[symb][1] = [price]
        channel_time[symb][1] = [time]
        
        alerts_MT[symb][1] = trends[symb][-1][1]

        if trends[symb][-1][1] == 1:
            channel_cond[symb][1] = ['long']
        elif trends[symb][-1][1] == 2:
            channel_cond[symb][1] = ['short']
        #bot.send_message(error_tg, f'{symb} rewrite\n{channel_cond[symb][1]}')
    except Exception as e:
        bot.send_message(error_tg, f'rewrite 33\n\n{e}')


def save():
    try:
        with open('/projects/Ver33/channel_price.txt', 'w') as file:
            file.write(json.dumps(channel_price))
                
        with open('/projects/Ver33/channel_time.txt', 'w') as file:
            file.write(json.dumps(channel_time))

        with open('/projects/Ver33/alerts_MT.txt', 'w') as file:
            file.write(json.dumps(alerts_MT)) 

        with open('/projects/Ver33/channel_cond.txt', 'w') as file:
            file.write(json.dumps(channel_cond))   

        with open(f'/projects/Ver33/stats/{str(day_check)}_stat.txt', 'w') as file:
            file.write(json.dumps(alerts_stat))

        with open('/projects/Ver33/stats/alerts_stat.txt', 'w') as file:
            file.write(json.dumps(alerts_stat))
            
        with open('/projects/Ver33/stats/day_check.txt', 'w') as file:
            file.write(json.dumps(day_check))

        with open('/projects/Ver33/stats_4h/alerts_stat.txt', 'w') as file:
            file.write(json.dumps(alerts_stat_4h))

        with open('/projects/Ver33/stats_4h/alerts_stat_1h.txt', 'w') as file:
            file.write(json.dumps(alerts_stat_1h))
            
        with open('/projects/Ver33/stats_4h/hour_check_1h.txt', 'w') as file:
            file.write(json.dumps(hour_check_1h))

        with open('/projects/Ver33/count_trades.txt', 'w') as file:
            file.write(json.dumps(count_trades))

    except:
        pass


###############


def make_new_features_for_trend_class(df_target, period_atr=15, rsi_period=15, w_length=31, porder=3):
    
    df_target['atr_15'] = ta.atr(high=df_target["High"],
                                low=df_target["Low"],
                                close=df_target["Close"]).rolling(period_atr).mean()
    
    df_target['smoth_atr'] = savgol_filter(df_target["atr_15"].fillna(0), w_length, porder)
    if len(df_target['smoth_atr']) == 0:
        bot.send_message(error_tg, f"ver 33 len(df_target['smoth_atr']) == 0 in make_new_features_for_trend_class")  ### отладка - поиск min([])   -nk-
    atr_min = df_target['smoth_atr'].min()
    atr_max = df_target['smoth_atr'].max()

    rsi = ta.rsi(df_target["Close"], timeperiod=rsi_period)

    df_target['smooth'] = savgol_filter(df_target["Close"], w_length, porder)

    # Включение rsi выглядит сомнительно, но atr ужно уравновестить колебанием тренда, иначе боковик захватывает
    # много места
    df_target['percent_atr'] = np.log1p((df_target['atr_15'] - atr_min) / (atr_max - atr_min))
    return df_target

def classify_trend_2(df):
    # Поиск пиков и впадин

    smooth_prices = df.reset_index()['smooth'].values
    atr_price = df.reset_index()['percent_atr'].values
    peaks, _ = find_peaks(smooth_prices, distance=15)#, prominence=df.reset_index()['atr_15'].iloc[-1])
    troughs, _ = find_peaks(-smooth_prices, distance=15)#, prominence=df.reset_index()['atr_15'].iloc[-1])

    # Инициализация списка с классификацией трендов
    # colors = {1: 'green'-все что связанно с ростом, 2: 'red' - все что связанно с падением, 3: 'blue'-неактуально,
    # 4: 'grey' - боковик}
    # Trend  это сама линия тренда, change это точки перехода от одного треда к другому
    trends = [1] * len(df)  # Изначально все неопределенный тренд (4)
    change = [0] * len(df)

    last_trend = 4  # Последний тренд перед боковиком
    in_sideways = False  # Флаг нахождения в боковике

    # Классификация трендов
    for k in range(1, len(smooth_prices)):
        '''# Идея в том, что среднее значение по percent_atr за 4 минуты меньше 0.15 и изменяется незначительно, за это отвечает
        # atr_price[k - 5:k].std()
        if k > 5 and atr_price[k - 4:k].mean() <= 0.5 and atr_price[k - 5:k].std() <= 0.0001 and not in_sideways:
            last_trend = trends[k - 1]  # Запоминаем тренд перед боковиком
            trends[k] = 4
            change[k] = 4
            in_sideways = True
        # Это нужно, если глобальный тренд изменился внутри боковика и не проспать точку изменения паравления рост/радение
        # Иначе на выходе из боковика можно получить не ту точку
        elif atr_price[k - 5:k].mean() <= 5 and in_sideways and (k in peaks or k in troughs):
            if k in peaks:
                last_trend = 2
                trends[k] = trends[k - 1]
            elif k in troughs:
                last_trend = 1
                trends[k] = trends[k - 1]
        elif (atr_price[k - 4:k].mean() >= 0.5 and in_sideways) or (atr_price[k - 3:k].std() >= 0.0004 and in_sideways):
            in_sideways = False
            # Возвращаемся к последнему тренду перед боковиком
            trends[k] = last_trend
            change[k] = last_trend'''
        
        if k in peaks and not in_sideways:
            trends[k] = 2  # Нисходящий тренд
            change[k] = 2
        elif k in troughs and not in_sideways:
            trends[k] = 1  # Восходящий тренд
            change[k] = 1
        elif k - 1 in peaks and not in_sideways:
            trends[k] = 2
        elif k - 1 in troughs and not in_sideways:
            trends[k] = 1
        else:
            trends[k] = trends[k - 1]  # Продолжающийся тренд

    return trends, change

def screen(symb, i, df, time_last_alert_algo_1, price_last_alert_algo_1, df_vol, df_btc):
        global day_check, hour_check_1h, count_trades, CV_pnl_long, CV_pnl_short, CV_pnl_all, last_k
        try:
            print('start send screen' , symb) 
            #time.sleep(0.01)
            
            df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume']
            time_alert = int(time_last_alert_algo_1[i] - (time_last_alert_algo_1[i] % 60000))
            ########
            df_chanels = df.copy()
            df_chanels['Close'] = df_chanels['Close'].astype(float)
            df_chanels['High'] = df_chanels['High'].astype(float)
            df_chanels['Low'] = df_chanels['Low'].astype(float)
            df_chanels['Open'] = df_chanels['Open'].astype(float)
            ########
            df['Time_alert'] = time_alert
            df['Price_alert'] = price_last_alert_algo_1[i]
            
            ###############
            df['Close'] = df['Close'].astype(float)
            df['High'] = df['High'].astype(float)
            df['Low'] = df['Low'].astype(float)
            df['Open'] = df['Open'].astype(float)
            df['Time'] = df['Time'].astype(int)
            df['Number of trades'] = df['Number of trades'].astype(int)
            df['Volume'] = df['Volume'].astype(float)
            df['Taker buy base asset volume'] = df['Taker buy base asset volume'].astype(float)
            #df_avg_vol = df.copy()
            
            try:
                df_viktor = df.copy()
                tr = make_new_features_for_trend_class(df_viktor)
                tr = tr.fillna(0)
                
                trend, change = classify_trend_2(tr)
                df['trend'] = trend
                #df['change'] = change
                
            except Exception as e:
                bot.send_message(error_tg, f'viktor {symb}\n\n{e}')

            

            ### parabolic ###
            df['psar_high'] = None
            df['psar_low'] = None
            psar = ta.psar(high=pd.Series(df['High'], copy=False), low=pd.Series(df['Low'], copy=False), close=pd.Series(df['Close'], copy=False), af0=0.01, af=0.01, max_af=0.05)
            df['psar_high'] = pd.DataFrame(psar)['PSARs_0.01_0.05']
            df['psar_low'] = pd.DataFrame(psar)['PSARl_0.01_0.05']
            df['psar_high'] = round((df['psar_high'] - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
            df['psar_low'] = round((df['psar_low'] - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
            

            

            df['signal'] = None
            df['line_alert'] = 0
            df['price_open'] = None
            df['price_close'] = None
            df['price_switch'] = None
            df['open_cond'] = None
            df['close_cond'] = None 
            df['switch_cond'] = None 
            df['pnl_description'] = None 

            ind = df[df['Time'] >= time_alert].index.values.astype(int)[:1]
            ##### atr ####
            try:
                df['atr'] = ta.atr(high=df['High'], low=df['Low'], close=df['Close'], length=10)
                df['atr_real'] = None
                df['atr_real_ind'] = None
                is_outlier_max = df.atr > df.atr
                df.loc[is_outlier_max, 'atr_real'] = df.atr.quantile(0.75)
                is_outlier_min = df.atr < df.atr.quantile(0.25)
                df.loc[is_outlier_min, 'atr_real'] = df.atr.quantile(0.25)
                for k in range(ind[0], len(df)-10):

                    df.loc[k, 'atr_real'] = np.where(df['atr'].iloc[k] > df.atr.iloc[:k+1].quantile(0.75), df.atr.iloc[:k+1].quantile(0.75), df['atr'].iloc[k])
                    
                    df.loc[k, 'atr_real'] = np.where(df['atr'].iloc[k] < df.atr.iloc[:k+1].quantile(0.25), df.atr.iloc[:k+1].quantile(0.25), df['atr'].iloc[k])

                    if len(df['atr_real'].iloc[:k+1]) == 0:
                        bot.send_message(error_tg, f"ver 33 len(df_target['smoth_atr']) == 0 in screen, i={i}, symb={symb}")  ### отладка - поиск min([])   -nk-
                    df.loc[k, 'atr_real_ind'] = (df['atr_real'].iloc[k] - df['atr_real'].iloc[:k+1].min()) / (df['atr_real'].iloc[:k+1].max() - df['atr_real'].iloc[:k+1].min())
            except:
                pass
            
            ind_1_line = ind[0] - 15
            ind_2_line = ind[0] + 120 + 1
            
            line_1 = time_alert - 15 * 60 * 1000 + 3 * 60 * 60 * 1000
            line_2 = time_alert + 120 * 60 * 1000 + 3 * 60 * 60 * 1000
            df_line = pd.DataFrame({'Data': [line_1, line_2]})
            df_line['Data_line'] = pd.to_datetime(df_line['Data'], unit = 'ms')
            
            df_CV = df[(df.index >= ind[0]-1) & (df.index < ind_2_line)]
            df_CV = df_CV.reset_index()
            df_CV['Close'] = round((df_CV['Close'] - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)

            #try:
            
            if 'e' not in channel_cond[symb][i]:
                channel_time[symb][i] = channel_time[symb][i] + [int(time_alert + 120 * 60 * 1000)]
                channel_price[symb][i] = channel_price[symb][i] + [float(df.iloc[ind[0]+120]['Close'])]
                channel_cond[symb][i] = channel_cond[symb][i] + ['e']

            # ver
            pnl_long = []
            pnl_short = []

            

            if channel_cond[symb][i][0] == 'long':
                print('long')
                time_open = int(channel_time[symb][i][0] - (channel_time[symb][i][0] % 60000))
                ind_time_open = df[df['Time'] == time_open].index.values.astype(int)
                df.loc[ind_time_open[0], 'price_open'] = round((float(channel_price[symb][i][0]) - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
                
                df.loc[ind_time_open[0], 'open_cond'] = channel_cond[symb][i][0]
                df_op_cond = df.open_cond.dropna()
                print(df_op_cond)
                start_screen_cond = 'long'

                for k in range(1,len(channel_time[symb][i])):

                    if k == len(channel_time[symb][i]) - 1:
                        if k % 2 == 1:
                            time_open = int(channel_time[symb][i][k] - (channel_time[symb][i][k] % 60000))
                            ind_time_open = df[df['Time'] == time_open].index.values.astype(int)
                            df.loc[ind_time_open[0], 'price_close'] = round((float(channel_price[symb][i][k]) - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
                            
                            df.loc[ind_time_open[0], 'close_cond'] = 'cls_long'
                            end_screen_cond = 'cls_long'
                            df_cl_cond = df.close_cond.dropna()
                            print(df_cl_cond)
                            pnl_long = pnl_long + [round((channel_price[symb][i][k] - channel_price[symb][i][k-1]) / channel_price[symb][i][k-1] * 100, 2)]
                        elif k % 2 == 0:
                            time_open = int(channel_time[symb][i][k] - (channel_time[symb][i][k] % 60000))
                            ind_time_open = df[df['Time'] == time_open].index.values.astype(int)
                            df.loc[ind_time_open[0], 'price_open'] = round((float(channel_price[symb][i][k]) - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
                            
                            df.loc[ind_time_open[0], 'open_cond'] = 'cls_short'
                            end_screen_cond = 'cls_short'
                            df_cl_cond = df.close_cond.dropna()
                            print(df_cl_cond)
                            pnl_short = pnl_short + [round((channel_price[symb][i][k-1] - channel_price[symb][i][k]) / channel_price[symb][i][k-1] * 100, 2)]
                        
                    elif k % 2 == 1:
                        time_open = int(channel_time[symb][i][k] - (channel_time[symb][i][k] % 60000))
                        ind_time_open = df[df['Time'] == time_open].index.values.astype(int)
                        df.loc[ind_time_open[0], 'price_close'] = round((float(channel_price[symb][i][k]) - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
                        
                        df.loc[ind_time_open[0], 'close_cond'] = channel_cond[symb][i][k]
                        df_sw_cond = df.switch_cond.dropna()
                        print(df_sw_cond)
                        pnl_long = pnl_long + [round((channel_price[symb][i][k] - channel_price[symb][i][k-1]) / channel_price[symb][i][k-1] * 100, 2)]

                    elif k % 2 == 0:
                        time_close = int(channel_time[symb][i][k] - (channel_time[symb][i][k] % 60000))
                        ind_time_close = df[df['Time'] == time_close].index.values.astype(int)
                        df.loc[ind_time_close[0], 'price_open'] = round((float(channel_price[symb][i][k]) - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
                        
                        df.loc[ind_time_close[0], 'open_cond'] = channel_cond[symb][i][k]
                        df_sw_cond = df.switch_cond.dropna()
                        print(df_sw_cond)
                        pnl_short = pnl_short + [round((channel_price[symb][i][k-1] - channel_price[symb][i][k]) / channel_price[symb][i][k-1] * 100, 2)]

            elif channel_cond[symb][i][0] == 'short':
                time_open = int(channel_time[symb][i][0] - (channel_time[symb][i][0] % 60000))
                ind_time_open = df[df['Time'] == time_open].index.values.astype(int)
                df.loc[ind_time_open[0], 'price_close'] = round((float(channel_price[symb][i][0]) - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
                
                df.loc[ind_time_open[0], 'close_cond'] = channel_cond[symb][i][0]
                
                start_screen_cond = 'short'

                for k in range(1,len(channel_time[symb][i])):

                    if k == len(channel_time[symb][i]) - 1:
                        if k % 2 == 0:
                            time_open = int(channel_time[symb][i][k] - (channel_time[symb][i][k] % 60000))
                            ind_time_open = df[df['Time'] == time_open].index.values.astype(int)
                            df.loc[ind_time_open[0], 'price_close'] = round((float(channel_price[symb][i][k]) - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
                            
                            df.loc[ind_time_open[0], 'close_cond'] = 'cls_long'
                            end_screen_cond = 'cls_long'
                            
                            pnl_long = pnl_long + [round((channel_price[symb][i][k] - channel_price[symb][i][k-1]) / channel_price[symb][i][k-1] * 100, 2)]
                        elif k % 2 == 1:
                            time_open = int(channel_time[symb][i][k] - (channel_time[symb][i][k] % 60000))
                            ind_time_open = df[df['Time'] == time_open].index.values.astype(int)
                            df.loc[ind_time_open[0], 'price_open'] = round((float(channel_price[symb][i][k]) - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
                            
                            df.loc[ind_time_open[0], 'open_cond'] = 'cls_short'
                            end_screen_cond = 'cls_short'
                            
                            pnl_short = pnl_short + [round((channel_price[symb][i][k-1] - channel_price[symb][i][k]) / channel_price[symb][i][k-1] * 100, 2)]
                        
                    elif k % 2 == 0:
                        time_open = int(channel_time[symb][i][k] - (channel_time[symb][i][k] % 60000))
                        ind_time_open = df[df['Time'] == time_open].index.values.astype(int)
                        df.loc[ind_time_open[0], 'price_close'] = round((float(channel_price[symb][i][k]) - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
                        
                        df.loc[ind_time_open[0], 'close_cond'] = channel_cond[symb][i][k]
                        
                        pnl_long = pnl_long + [round((channel_price[symb][i][k] - channel_price[symb][i][k-1]) / channel_price[symb][i][k-1] * 100, 2)]

                    elif k % 2 == 1:
                        time_close = int(channel_time[symb][i][k] - (channel_time[symb][i][k] % 60000))
                        ind_time_close = df[df['Time'] == time_close].index.values.astype(int)
                        df.loc[ind_time_close[0], 'price_open'] = round((float(channel_price[symb][i][k]) - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
                        
                        df.loc[ind_time_close[0], 'open_cond'] = channel_cond[symb][i][k]
                        
                        pnl_short = pnl_short + [round((channel_price[symb][i][k-1] - channel_price[symb][i][k]) / channel_price[symb][i][k-1] * 100, 2)]

            pnl_total_long = round(sum(pnl_long),2)
            pnl_total_long_clear = round(pnl_total_long - len(pnl_long)*0.1, 2)
            
            pnl_total_short = round(sum(pnl_short),2)
            pnl_total_short_clear = round(pnl_total_short - len(pnl_short)*0.1, 2)
            
            pnl_total_clear = round(pnl_total_long_clear + pnl_total_short_clear, 2)

            df['avg_vol'] = df['Volume']/df['Number of trades']
            index_vol = round(float(df.iloc[ind[0]]['Volume'] / statistics.mean(df['Volume'][ind[0]-5:ind[0]])), 2)
            
            df['typ_price'] = ((df.High + df.Close + df.Low) / 3 ) * df.Volume

            '''df['VWAP'] = None
            for j in range(ind[0], len(df)):
                df.loc[j, 'VWAP'] = round((sum(df['typ_price'][ind[0]:j+1])/ sum(df['Volume'][ind[0]:j+1]) - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
            '''
            df.loc[ind[0], 'signal'] = 0 
            

            

            df['Time'] = df['Time'] + 3 * 60 * 60 * 1000
            df = df.merge(df_vol, on='Time', how='left')
            df = df.merge(df_btc, on='Time', how='left')
            df = df.where(pd.notnull(df), None)
            df['Close_btc'] = df['Close_btc'].astype(float)
            # corr = float(df['Close'].corr(df['Close_btc']))
            # corr_before = float(df['Close'][:ind[0]].corr(df['Close_btc'][:ind[0]])) 
            # corr_before_15 = float(df['Close'][:ind_1_line].corr(df['Close_btc'][:ind_1_line]))

            df.loc[0, 'volatility'] = 0
            df['High'] = df['High'].astype(float)
            df['Low'] = df['Low'].astype(float)
            if len(df['Low']) == 0:
                bot.send_message(error_tg, f"ver 33 len(df['Low']) == 0 in screen, i={i}, symb={symb}")  ### отладка - поиск min([])   -nk-
            if (max(df['High']) - min(df['Low'])) / min(df['Low']) * 100 < 5:
                df.loc[0, 'High'] = statistics.mean([max(df['High']), min(df['Low'])]) * 1.025
                df.loc[0, 'Low'] = statistics.mean([max(df['High']), min(df['Low'])]) * 0.975
                df.loc[0, 'Close'] = statistics.mean([max(df['High']), min(df['Low'])])
                df.loc[0, 'Open'] = statistics.mean([max(df['High']), min(df['Low'])])

            
            df = df.set_index('Time')
            df.index = pd.to_datetime(df.index, unit = 'ms')
            cols = df.columns.to_list()
            cols.remove('open_cond')
            cols.remove('close_cond')
            cols.remove('switch_cond')
            df[cols] = df[cols].astype(float)
            
            if len(df['Low'][(ind[0]+1):ind_2_line]) == 0:
                bot.send_message(error_tg, f"ver 33 len(df['Low'][(ind[0]+1):ind_2_line]) == 0 in screen, i={i}, symb={symb}")  ### отладка - поиск min([])   -nk-
            percent_high = round(((float(max(df['High'][ind[0]:ind_2_line])) - float(price_last_alert_algo_1[i]))/float(price_last_alert_algo_1[i])*100),2)
            percent_low = round(((float(min(df['Low'][(ind[0]+1):ind_2_line])) - float(price_last_alert_algo_1[i]))/float(price_last_alert_algo_1[i])*100),2)
            
            if percent_low >= 0:
                percent_low = 0
            if percent_high == 0:
                percent_high = 1
            df['count'] = df['Close'] 
            df['count'] = df['count'].apply(lambda x: 1 if x >= float(price_last_alert_algo_1[i]) else 0)
            
            count_plus_pnl = int(sum(df['count'][ind[0]:ind_2_line]) / len(df[ind[0]:ind_2_line]) * 100)
            count_minus_pnl = 100 - count_plus_pnl
            
            time_pump = get_formatted_time(int(time_last_alert_algo_1[i] + 3 * 60 * 60 * 1000))
            
            if percent_high >= 30:
                description = сap_name_1h[0]
            elif percent_high >= 20:
                description = сap_name_1h[1]
            elif percent_high >= 16:
                description = сap_name_1h[2]
            elif percent_high >= 12:
                description = сap_name_1h[3]
            elif percent_high >= 6:
                description = сap_name_1h[4]
            elif percent_high >= 3:
                description = сap_name_1h[5]
            elif percent_high >= 1.5:
                description = сap_name_1h[6]
            elif percent_high < 1.5 and percent_low > -1.5:
                description = сap_name_1h[7]
            elif percent_low <= -30:
                description = сap_name_1h[-1]
            elif percent_low <= -20:
                description = сap_name_1h[-2]
            elif percent_low <= -16:
                description = сap_name_1h[-3]
            elif percent_low <= -12:
                description = сap_name_1h[-4]
            elif percent_low <= -6:
                description = сap_name_1h[-5]
            elif percent_low <= -3:
                description = сap_name_1h[-6]
            elif percent_low <= -1.5:
                description = сap_name_1h[-7]
 
            if percent_high >= 100 or percent_low <= -100:
                power_emoji = f'{legendary_100}'
            elif percent_high >= 60 or percent_low <= -60:
                power_emoji = f'{legendary_60}'
            elif percent_high >= 40 or percent_low <= -40:
                power_emoji = f'{legendary_40}'
            elif percent_high >= 30 or percent_low <= -30:
                power_emoji = f'{legendary_30}'
            elif percent_high >= 20 or percent_low <= -20:
                power_emoji = f'{legendary_20}'
            elif percent_high >= 16 or percent_low <= -16:
                power_emoji = f'{legendary_16}'
            elif percent_high >= 12 or percent_low <= -12:
                power_emoji = f'{p_emoji}{p_emoji}{p_emoji}'
            elif percent_high >= 6 or percent_low <= -6:
                power_emoji = f'{p_emoji}{p_emoji}'
            elif percent_high >= 3 or percent_low <= -3:
                power_emoji = f'{p_emoji}'
            else:
                power_emoji = ''

            df['Close'] = round((df['Close'] - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
            df['Open'] = round((df['Open'] - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
            df['High'] = round((df['High'] - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
            df['Low'] = round((df['Low'] - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
            btc_zero_price = df.iloc[ind[0]]['Close_btc']
            delta = df.iloc[0]['Close']
            df['Close_btc'] = round((df['Close_btc'] - float(btc_zero_price)) / float(btc_zero_price) * 100, 2) + delta
            if len(df['Close'][:ind[0]]) == 0:
                bot.send_message(error_tg, f"ver 33 len(df['Close'][:ind[0]]) == 0 in screen, i={i}, symb={symb}")  ### отладка - поиск min([])   -nk-
            min_pcnt_befor = min(df['Close'][:ind[0]])
            ################################ Ценовые каналы ##############################
            ##############################################################################
            df_chanels['Close'] = round((df_chanels['Close'] - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
            df_chanels['Open'] = round((df_chanels['Open'] - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
            df_chanels['High'] = round((df_chanels['High'] - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
            df_chanels['Low'] = round((df_chanels['Low'] - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
            
            def create_dist(df):
                distr = np.linspace(df.Low, df.High, 10)
                return distr
        
            def calculate_chanel(data, candles_num):

                data = data[-candles_num-3:-3]
                chanel_time_end = data[-1:].Time.values[0]
                chanel_time_start = data[:1].Time.values[0]
                data = data.reset_index(drop=True)
                
                data['candle_dist']= data.apply(create_dist, axis = 1)
                data['dateIndex'] = data.index + 1

                data_exp = data.explode('candle_dist')
                X = np.asarray(data_exp.dateIndex)
                y = np.asarray(data_exp.candle_dist)
                
                conc = np.concatenate((X.reshape(-1,1),y.reshape(-1,1)), axis = 1)
                pca = PCA(1)
                pca_tr = pca.fit_transform(conc)
                pca_inv = pca.inverse_transform(pca_tr)
                y_0 = pca_inv[0,1]
                y_1 = pca_inv[-1,1]
                
                y_new = y - pca_inv[:,1]
                chanel_width = y_new.std()*2*2
                return (chanel_width, (chanel_time_start, chanel_time_end), (y_0, y_1))
            
            def chanel_widths(ser: pd.Series, df: pd.DataFrame):
                data = df.loc[ser.index]
                data = data.reset_index(drop=True)
                data['candle_dist']= data.apply(create_dist, axis = 1)
                
                data['dateIndex'] = data.index + 1
                data_exp = data.explode('candle_dist')
                X = np.asarray(data_exp.dateIndex)
                Y = np.asarray(data_exp.candle_dist)
                X = X.reshape(-1,1)
                Y = Y.reshape(-1,1)
                reg = LinearRegression().fit(X, Y)
                y_fit = reg.predict(X)
            
                chanel_width = 2*2*mae(Y, y_fit) #*1.2
                return chanel_width
            
            

            
            
            

            time_alert_msk = time_alert + 3 * 60 * 60 * 1000
            time_alert_msk = time_alert_msk - time_alert_msk%60000
            df_chanels['Time'] = df_chanels['Time'] + 3 * 60 * 60 * 1000 ####
            df_chanels.reset_index(inplace=True)
            ################### Подсчет метрик ширин каналов ##############################################
            def w30_scoring(feature):
                if feature <= w_scores['w30'][6]:
                    return 6
                elif feature <= w_scores['w30'][5]:
                    return 5
                elif feature <= w_scores['w30'][4]:
                    return 4
                elif feature <= w_scores['w30'][3]:
                    return 3
                elif feature <= w_scores['w30'][2]:
                    return 2
                elif feature <= w_scores['w30'][1]:
                    return 1
                else:
                    return 0
                        
            def w5_scoring(feature):
                if feature <= w_scores['w5'][6]:
                    return 6
                elif feature <= w_scores['w5'][5]:
                    return 5
                elif feature <= w_scores['w5'][4]:
                    return 4
                elif feature <= w_scores['w5'][3]:
                    return 3
                elif feature <= w_scores['w5'][2]:
                    return 2
                elif feature <= w_scores['w5'][1]:
                    return 1
                else:
                    return 0

        
            w_scores = {'w30': {6: 0.613, 5: 0.7645, 4: 0.916, 3: 1.0745, 2: 1.233, 1: 1.4}, 
                        'w5' : {6: 0.215, 5: 0.28,   4: 0.346, 3: 0.397,  2: 0.449, 1: 0.5}}
            
            # chanel_width_params = {'w30_med':0.92, 'w5_med':0.35}
            
            df_chanels['w30'] = df_chanels[df_chanels['Time'] <= time_alert_msk -2*60*1000].High.rolling(window = 30).apply(chanel_widths, args=(df_chanels,))
            df_chanels['w5'] = df_chanels[(df_chanels['Time'] >= time_alert_msk - 60*60*1000)&(df_chanels['Time'] <= time_alert_msk -2*60*1000)].High.rolling(window = 5).apply(chanel_widths, args=(df_chanels,))
            
            w30_50a = df_chanels[(df_chanels.w30 > np.percentile(df_chanels.w30.dropna(),50)) & (df_chanels.w30 < np.percentile(df_chanels.w30.dropna(),99))].w30.mean()
            # median_30 = df_chanels.w30.median()
            mean_5 = df_chanels.w5.mean()

            # narrow_30_chanel = int(median_30 <=chanel_width_params['w30_med'])
            # narrow_5_chanel = int(mean_5 <=chanel_width_params['w5_med'])

            w30_score = w30_scoring(w30_50a)
            w5_score = w5_scoring(mean_5)

            ##################################################################################################
            
            window = df_chanels['Time'] < time_alert_msk
            
            data_alert = df_chanels[window]
            data_after = df_chanels[~window]
            data_after = data_after.reset_index(drop = True)
            start_anomaly = data_alert[-2:-1].Low.values[0]
            # start_anomaly_time = data_alert[-2:-1].Time.values[0]
            time_before_alert = [5, 10, 20]
            
            chanels_info = [calculate_chanel(data_alert, candles) for candles in time_before_alert]
            points = []
            widths = np.asarray([i[0] for i in chanels_info])
            # widths_rounded = np.around(widths,2) # Ширины каналов
            
            s0 = np.around(-start_anomaly/widths,2) # -> array - индикаторы в момент алерта  
            mins_indi = [] # индикаторы в моменты 1, 5, 10, 30, 60 минутных свечей после алерта
            times = [1, 5, 10, 30, 60]
        
            for time in times:
                indic = np.around((data_after.loc[time,'High'] - start_anomaly)/widths,2)
                mins_indi.append(indic)
            
            max_indi = np.around((percent_high - start_anomaly)/widths, 2) # индикаторы максимума
            min_indi = np.around((percent_low - start_anomaly)/widths, 2) # индикаторы минимума
            
            colors_ = np.concatenate([([i]*2) for i in ['r','b','g','y']], axis=0).tolist()

            # Точки для отрисовки каналов
            
            for info in chanels_info:
                xx = [get_formatted_time(int(x)) for x in info[1]]
                yy = info[2]
                points_1 = [(i, j - info[0]/2) for (i, j) in zip(xx,yy)]
                points_2 = [(i, j + info[0]/2) for (i, j) in zip(xx,yy)]
                points.append(points_1)
                points.append(points_2)

            text = f'\nalert:{s0}; 1 min:{mins_indi[0]}; 5 min:{mins_indi[1]}\n10 min:{mins_indi[2]}; 30 min:{mins_indi[3]}; 60 min:{mins_indi[4]}\nmax:{max_indi}; min:{min_indi}'
            #######################
            
            
            #corr = corr[0][1]
            #df_btc = df_btc.set_index('Time')
            #df_btc.index = pd.to_datetime(df_btc.index, unit = 'ms')
            #######################
            

            y1values = df['Close'].values
            y2value  = 0

            
            apds = [mpf.make_addplot(df['signal'],type='scatter', color='#2d5ff5',markersize=50, secondary_y=False),
                        mpf.make_addplot(df['psar_high'],type='scatter', color='r',markersize=0.5, secondary_y=False),
                        mpf.make_addplot(df['psar_low'],type='scatter', color='g',markersize=0.5, secondary_y=False),
                        mpf.make_addplot(df['line_alert'],type='scatter', color='g',markersize=0.1, secondary_y=False),
                        mpf.make_addplot(df['price_close'], type='scatter', color='r',markersize=20, marker='v', secondary_y=False),
                        mpf.make_addplot(df['price_open'], type='scatter', color='g',markersize=20, marker='^', secondary_y=False),
                        #mpf.make_addplot(df['price_switch'], type='scatter', color='g',markersize=20, marker='^', secondary_y=False),
                        #mpf.make_addplot(df['price_switch'], type='scatter', color='r',markersize=20, marker='v', secondary_y=False),
                        ]
            
            cap = f'ver33 {description} {symb}\n{power_emoji}\nclear_pnl: {pnl_total_clear}%\ntake_clear_potential: {round(pnl_total_clear/percent_high*100,2)}%'
            
            title_mess = f'\n\n\nver33 {symb}, price: {price_last_alert_algo_1[i]}, time: {time_pump}\nmax={percent_high}%, min={percent_low}%, coef={count_plus_pnl}/{count_minus_pnl}, Ind_Vol= {index_vol}\nlong_pnl: {pnl_total_long_clear}%, short_pnl: {pnl_total_short_clear}%, clear_pnl: {pnl_total_clear}%,  min_pcnt_before: {round(min_pcnt_befor, 2)}' #, PnL% = {percent_order} corr: {round(corr,2)}, corr_before: {round(corr_before,2)}, corr_before_15: {round(corr_before_15,2)}, chanel_30: {narrow_30_chanel}, chanel_5: {narrow_5_chanel},
            ### сохраняем последний трейд для отправки в wtp all
            trade_str = f'ver33: {pnl_total_clear}% / {round(pnl_total_clear/percent_high*100,2)}%'
            
            al = dict(alines=points, colors=colors_, linewidths=2, alpha=0.6)
            vl = dict(vlines=[df_line.iloc[0,1],df_line.iloc[1,1]],linewidths=(1,1))
            buf6 = io.BytesIO()

            
 
            
            up_trand = dict(y1=y1values,y2=y2value,where=df['trend']==1,color="g",alpha=0.1)
            down_trand = dict(y1=y1values,y2=y2value,where=df['trend']==2,color="r",alpha=0.1)
            plot_between = [up_trand, down_trand]

            CV_pnl_long = 0
            CV_pnl_short = 0
            CV_pnl_all = 0
            last_k = 0

            for k in range(1, len(df_CV)):
                
                if df_CV['trend'].iloc[k] == 2 and df_CV['trend'].iloc[k-1] == 1:
                    CV_pnl_long = CV_pnl_long + (df_CV['Close'].iloc[k-1] - df_CV['Close'].iloc[last_k]) - 0.1
                    last_k = k-1

                elif df_CV['trend'].iloc[k] == 1 and df_CV['trend'].iloc[k-1] == 2:
                    CV_pnl_short = CV_pnl_short - (df_CV['Close'].iloc[k-1] - df_CV['Close'].iloc[last_k]) - 0.1
                    last_k = k-1

                
            if df_CV['trend'].iloc[-1] == 1:
                CV_pnl_long = CV_pnl_long + (df_CV['Close'].iloc[k-1] - df_CV['Close'].iloc[last_k]) - 0.1
                last_k = k-1

            elif df_CV['trend'].iloc[1] == 2:
                CV_pnl_short = CV_pnl_short - (df_CV['Close'].iloc[k-1] - df_CV['Close'].iloc[last_k]) - 0.1
                last_k = k-1

            CV_pnl_all = CV_pnl_short + CV_pnl_long
            
                
            
            if percent_high >= 12 or percent_low <= -12:
                title_mess = '\n\n\n' + title_mess + text
                fig, axlist = mpf.plot(df, type='candle', style='yahoo', volume=True, fill_between=plot_between, alines=al, addplot=apds, vlines=vl, title=title_mess, panel_ratios=(4,1), figratio=(30,14), fontscale=0.6,returnfig=True, show_nontrading=True)
                df_op_cond = df.open_cond.dropna()
                for x,t in df_op_cond.items():
                    y = df.loc[x,'price_open']+0.5
                    axlist[0].text(x,y,t,fontstyle='italic')
                df_cl_cond = df.close_cond.dropna()
                for x,t in df_cl_cond.items():
                    y = df.loc[x,'price_close']+0.5
                    axlist[0].text(x,y,t,fontstyle='italic')
                '''df_sw_cond = df.switch_cond.dropna()
                for x,t in df_sw_cond.items():
                    y = df.loc[x,'price_switch']+0.5
                    axlist[0].text(x,y,t,fontstyle='italic')'''

            

                
            else:
                fig, axlist = mpf.plot(df, type='candle', style='yahoo', volume=True, fill_between=plot_between, alines=al, addplot=apds, vlines=vl, title=title_mess, fontscale=0.6, panel_ratios=(4,1), figratio=(30,14),returnfig=True, show_nontrading=True)
                df_op_cond = df.open_cond.dropna()
                
                for x,t in df_op_cond.items():
                    y = df.loc[x,'price_open']+percent_high/2*0.2
                    axlist[0].text(x,y,t,fontstyle='normal',fontsize='x-large')
                df_cl_cond = df.close_cond.dropna()
                
                for x,t in df_cl_cond.items():
                    y = df.loc[x,'price_close']+percent_high/2*0.2
                    axlist[0].text(x,y,t,fontstyle='normal',fontsize='x-large')

                '''df_sw_cond = df.switch_cond.dropna()
                print(df_sw_cond)
                for x,t in df_sw_cond.items():
                    y = df.loc[x,'price_switch']+percent_high/2*0.2
                    axlist[0].text(x,y,t,fontstyle='normal',fontsize='x-large')'''

                
            
            # (строку ниже сдвинул на 1 уровень, чтобы не дублировать блок)
            fig.savefig(fname=buf6, dpi=100, pad_inches=0.25)

            try:
                for ax in axlist:
                        del ax
                plt.cla()
                plt.clf()

                #plt.close(fig)
                plt.close('all')
                del fig, axlist
            except: pass
            '''
            if percent_high >= 12 or percent_low <= -12:
                title_mess = '\n\n\n' + title_mess + text
                
                mpf.plot(df, type='candle', style='yahoo', volume=True, alines=al, addplot=apds, vlines=vl, title=title_mess, panel_ratios=(4,1), figratio=(30,14), fontscale=0.6, closefig=True, savefig=dict(fname=buf6,dpi=100,pad_inches=0.25))
                #fig , axlist = mpf.plot(df, type='candle', style='yahoo', volume=True, alines=al, addplot=apds, vlines=vl, title=title_mess, panel_ratios=(4,1), figratio=(30,14), fontscale=0.6, closefig=True, returnfig=True) #savefig=dict(fname=f'/projects/Ver3/mt_screen/screen{symb}.jpeg',dpi=100,pad_inches=0.25))
            else:
                mpf.plot(df, type='candle', style='yahoo', volume=True, addplot=apds, vlines=vl, title=title_mess, fontscale=0.6, panel_ratios=(4,1), figratio=(30,14), closefig=True, savefig=dict(fname=buf6,dpi=100,pad_inches=0.25))
                #fig , axlist = mpf.plot(df, type='candle', style='yahoo', volume=True, addplot=apds, vlines=vl, title=title_mess, fontscale=0.6, panel_ratios=(4,1), figratio=(30,14), closefig=True, returnfig=True) #savefig=dict(fname=f'/projects/Ver3/mt_screen/screen{symb}.jpeg',dpi=100,pad_inches=0.25))
            
            '''
            buf6.seek(0)
            id_photo = send_photo(chat_id=screen_tg, file=buf6, cap=cap)
        
            f_id = str(id_photo['result']['photo'][-1]['file_id'])
            #id_photo = bot.send_photo(screen_tg, buf6, caption=cap)            
            #f_id = id_photo.photo[-1].file_id
            buf6.close()
            bot.send_photo(screen_v20, f_id, caption=cap)
            #bot.send_message(a1_v31,cap)
            #if percent_high >= 3:
                #bot.send_photo(wtp_screen_tg, open(f'/projects/Ver33/mt_screen/screen{symb}.jpeg','rb'), caption=cap)
                #bot.send_message(wtp_v31,cap)

            '''if MT_pnl_clear >= 8 and round(MT_pnl_clear/percent_high*100,2) <= 40:
                bot.send_photo(max_8_take_40_tg, f_id, caption=cap)
            
            if MT_pnl_clear >= 10:
                bot.send_photo(clear_pnl_10_tg, f_id, caption=cap)

            if round(MT_pnl_clear/percent_high*100,2) >= 80:
                bot.send_photo(take_clear_pnl_80_tg, f_id, caption=cap)'''

            channel_price[symb][i] = [] 
            channel_time[symb][i] = []
            
            print('end send screen')

            
            

            alerts_MT[symb][i] = 0
            
            return f_id, trade_str

        except Exception as e:
            #bot.send_message(screen_tg, f'fail screen {symb}')
            bot.send_message(error_tg, f'ver33 fail screen {symb} i={i}\n\n{e}')
            
            channel_price[symb][i] = []
            channel_time[symb][i] = []
            alerts_MT[symb][i] = 0
            return 0, ''
                        
            



def get_formatted_time(timestamp):
        dt_object = datetime.datetime.fromtimestamp(timestamp / 1000.0)
        time_str = dt_object.strftime("%Y-%m-%d %H:%M:%S")
        return time_str
    
def get_formatted_day(timestamp):
    dt_object = datetime.datetime.fromtimestamp(timestamp / 1000.0)
    time_str = dt_object.strftime("%Y-%m-%d")
    return time_str