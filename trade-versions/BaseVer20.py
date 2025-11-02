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
from datetime import datetime as dt
import statistics
import asyncio
import requests
import mplfinance as mpf
import csv
import joblib
import openpyxl
import xlsxwriter
import io
from matplotlib import pyplot as plt
from memory_profiler import profile
from scipy.signal import argrelextrema
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error as mae # для подсчета ширины канала
import matplotlib 
matplotlib.use("agg")

key = '###'


stat_tg = '-###'  
screen_tg = '-###' 
screen_v20 = '-###'
max_8_take_40_tg = '-###'
clear_pnl_10_tg = '-###'
take_clear_pnl_80_tg = '-###'
error_tg = '-###'   
stat_tg = '-###'
TG_Bot_token = "###"  
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

with open('/projects/data/price_acc.txt', 'r') as f:
    last = f.read()
    price_acc = json.loads(last)


symbols = []
for key in price_acc:
    symbols.append(key)

try:
    with open('/projects/Ver20/stats/alerts_stat.txt', 'r') as f:
        last = f.read()
        alerts_stat = json.loads(last)
except:
    alerts_stat = {
        'all_clear': float(0.0),
        'all_potential': float(0.0),
        'all_count_per_day': int(0),
        'wtp_potential': float(0.0),
        'wtp_clear': float(0.0),
        'wtp_count': int(0),
        'commission': float(0.0),
        'commission_wtp': float(0.0)
    }

try:
    with open('/projects/Ver20/stats/day_check.txt', 'r') as f:
        last = f.read()
        day_check = json.loads(last)
except:
    day_check = 0


try:
    with open('/projects/Ver20/stats_4h/alerts_stat_4h.txt', 'r') as f:
        last = f.read()
        alerts_stat_4h = json.loads(last)
except:
    alerts_stat_4h = {
        'clear': float(0.0),
        'potential': float(0.0),
        'wtp_clear': int(0),
        'wtp_potential': float(0.0)
    }

try:
    with open('/projects/Ver20/stats_4h/alerts_stat_1h.txt', 'r') as f:
        last = f.read()
        alerts_stat_1h = json.loads(last)
except:
    alerts_stat_1h = {
        'plus_30': [0, 0, 0],
        'plus_20': [0, 0, 0],
        'plus_16': [0, 0, 0],
        'plus_12': [0, 0, 0],
        'plus_6': [0, 0, 0],
        'plus_3': [0, 0, 0],
        'plus_1.5': [0, 0, 0],
        'noise': [0, 0, 0],
        'minus_1.5': [0, 0, 0],
        'minus_3': [0, 0, 0],
        'minus_6': [0, 0, 0],
        'minus_12': [0, 0, 0],
        'minus_16': [0, 0, 0],
        'minus_20': [0, 0, 0],
        'minus_30': [0, 0, 0]
    }

сap_name_1h = ['P!!!!!+', 'P!!!!!', 'P!!!!', 'P!!!', 'P!!', 'P!', 'P', 'N', 'D', 'D!', 'D!!', 'D!!!', 'D!!!!', 'D!!!!!', 'D!!!!!+'] 


try:
    with open('/projects/Ver20/stats_4h/hour_check_1h.txt', 'r') as f:
        last = f.read()
        hour_check_1h = json.loads(last)
except:
    hour_check_1h = 0


try:
    with open('/projects/Ver20/channel_price.txt', 'r') as f:
        last = f.read()
        channel_price = json.loads(last)
    
    with open('/projects/Ver20/channel_time.txt', 'r') as f:
        last = f.read()
        channel_time = json.loads(last)
    
    with open('/projects/Ver20/alerts_MT.txt', 'r') as f:
        last = f.read()
        alerts_MT = json.loads(last)

except:
    channel_price = {symbol: [[], []] for symbol in symbols}
    channel_time = {symbol: [[], []] for symbol in symbols}
    alerts_MT = {symbol: [1, 1] for symbol in symbols}


try:
    with open('/projects/Ver20/channel_cond.txt', 'r') as f:
        last = f.read()
        channel_cond = json.loads(last)
except:
    channel_cond = {symbol: [[], []] for symbol in symbols}


try:
    with open('/projects/Ver20/count_trades.txt', 'r') as f:
        last = f.read()
        count_trades = json.loads(last)
except:
    count_trades = 0

####################
try:
    with open('/projects/Ver20/high_ser.txt', 'r') as f:
        last = f.read()
        high_ser = json.loads(last)
    
    for i in high_ser:
        high_ser[i] = pd.Series(high_ser[i])

    with open('/projects/Ver20/low_ser.txt', 'r') as f:
        last = f.read()
        low_ser = json.loads(last)
    
    for i in low_ser:
        low_ser[i] = pd.Series(low_ser[i])

    with open('/projects/Ver20/close_ser.txt', 'r') as f:
        last = f.read()
        close_ser = json.loads(last)
    
    for i in close_ser:
        close_ser[i] = pd.Series(close_ser[i])

    with open('/projects/Ver20/lim_amp.txt', 'r') as f:
        last = f.read()
        lim_amp = json.loads(last)

    with open('/projects/Ver20/lim_atr.txt', 'r') as f:
        last = f.read()
        lim_atr = json.loads(last)

    # with open('/projects/Ver20/f1.txt', 'r') as f:
    #     last = f.read()
    #     f1 = json.loads(last)

    # with open('/projects/Ver20/f2.txt', 'r') as f:
    #     last = f.read()
    #     f2 = json.loads(last)

    with open('/projects/Ver20/current_minute_prices.txt', 'r') as f:
        last = f.read()
        current_minute_prices = json.loads(last)

    with open('/projects/Ver20/current_minute_start.txt', 'r') as f:
        last = f.read()
        current_minute_start = json.loads(last)

except:
    high_ser = {symb: pd.Series([None]) for symb in symbols}
    low_ser = {symb: pd.Series([None]) for symb in symbols}
    close_ser = {symb: pd.Series([None]) for symb in symbols}
    lim_amp = {symb: 0 for symb in symbols}
    lim_atr = {symb: 0 for symb in symbols}


    

    current_minute_prices = {symb: [] for symb in symbols}
    current_minute_start = {symb: 0 for symb in symbols}
############

try:
    with open('/projects/Ver20/max_average_bar_price.txt', 'r') as f:
        last = f.read()
        max_average_bar_price = json.loads(last)
except:
    max_average_bar_price = {symb: [0, 0] for symb in symbols}





def send_photo(chat_id, file, cap):
        url = f'https://api.telegram.org/bot{TG_Bot_token}/sendPhoto'
        files = {'photo': file}
        data = {'chat_id': chat_id, "caption": cap}
        response = requests.post(url, files=files, data=data)
        json_response = response.json()
        return json_response

############## EG #############

# Гиперпараметры фильтра, объявляем как константу
try:
    with open('/projects/Ver20/time_last_kline.txt', 'r') as f:
        last = f.read()
        time_last_kline = json.loads(last)
except:
    time_last_kline = {symb: 0 for symb in symbols}


# хранят значения стопов и последний посчитанный ATR
# try:
#     f = open('/projects/Ver20/red_stop.txt', 'r')
#     last = f.read()
#     red_stop = json.loads(last)
#     f.close()
# except:
#     red_stop = {symb: [None, None] for symb in symbols}
try:
    with open('/projects/Ver20/orange_stop.txt', 'r') as f:
        last = f.read()
        orange_stop = json.loads(last)
except:
    orange_stop = {symb: [None, None] for symb in symbols}
try:
    with open('/projects/Ver20/yellow_stop.txt', 'r') as f:
        last = f.read()
        yellow_stop = json.loads(last)
except:
    yellow_stop = {symb: [None, None] for symb in symbols}

try:
    with open('/projects/Ver20/last_atr.txt', 'r') as f:
        last = f.read()
        last_atr = json.loads(last)
except:
    last_atr = {symb: None for symb in symbols}


try:
    with open('/projects/Ver20/orange_ten_min_start.txt', 'r') as f:
        last = f.read()
        orange_ten_min_start = json.loads(last)
except:
    orange_ten_min_start = {symb: [0, 0] for symb in symbols}


# try:
#     f = open('/projects/Ver20/ten_min_start.txt', 'r')
#     last = f.read()
#     ten_min_start = json.loads(last)
#     f.close()
# except:   
#     ten_min_start = {symb: [0, 0] for symb in symbols}
try:
    with open('/projects/Ver20/sl_time.txt', 'r') as f:
        last = f.read()
        sl_time = json.loads(last)
except:
    sl_time = {symb: [None, None] for symb in symbols}



PARAMS = {"n": 3, "limit": 1.5, "long_base": 20, "alg": "3_SL",
          "atr_limit": 0.46, "length": 14, "block_min": 5, 
          "down_rsl": 1.0, "step_rsl": 0.5, "sl_time": 4,
          "down_osl": 1.4, "step_osl": 0.5, "down_ysl": 2.4}

f1, f2 = {symb: [] for symb in symbols}, {symb: [] for symb in symbols}




def calc_prev_min_chandles(channel_data_price: dict[list[float]], symb: str, 
                           i: int):
    """Собирает нужное число (39) предыдущих минутных свечей"""
    global PARAMS
    
    
    idxs = range(-(PARAMS["long_base"] + PARAMS["length"] + 5) * 60 -1, -1, 60)
    prices = channel_data_price[symb]
    try:
        high_ser_loc = pd.Series((max(prices[j: j + 60]) for j in idxs))
        low_ser_loc = pd.Series((min(prices[j: j + 60]) for j in idxs))
    except Exception as er:
        bot.send_message(error_tg, f"ver 20 fail calc_prev_min_chandles, min([]), i={i}, symb={symb}, er={er}")  ### отладка - поиск min([])   -eg-
        high_ser_loc = pd.Series(((prices[j]) for j in idxs))
        low_ser_loc = pd.Series(((prices[j]) for j in idxs))
    close_ser_loc = pd.Series((prices[j] for j in (*idxs, -1)))
    return high_ser_loc, low_ser_loc, close_ser_loc

 
def cummul_chandle_calc(time_tick: int, price: float, symb: str, i: int, 
                        s_len = PARAMS["length"] + 12) -> None:  ### удлинил серию (+12)
    """Накопительно считает минутные свечи"""
    
    global high_ser, low_ser, close_ser, current_minute_start, current_minute_prices
    
    current_minute_prices[symb] = current_minute_prices[symb] + [price]
    if time_tick >= current_minute_start[symb] + 60 * 1000:        
        
        high_ser[symb] = high_ser[symb][-s_len:].reset_index(drop=True)
        high_ser[symb].loc[s_len] = max(current_minute_prices[symb])
        
        low_ser[symb] = low_ser[symb][-s_len:].reset_index(drop=True)
        low_ser[symb].loc[s_len] = min(current_minute_prices[symb])
        
        close_ser[symb] = close_ser[symb][-s_len:].reset_index(drop=True)
        close_ser[symb].loc[s_len] = price
        
        current_minute_prices[symb] = []
        #current_minute_start[symb] = current_minute_start[symb] + 60 * 1000


last_trade_ignore_bar_number = 6  # бар входа в сделку + 5 баров, которые мы не отслеживаем
last_trade_check_bar_number = 11  # бар входа в сделку + 10 баров, которые мы отслеживаем
last_trade_price_border_percent = 4  # процент, на который цена входа в сделку должна быть > цены алерта
last_trade_valid_pnl = 2  # минимальный процент pnl, который должен быть взять на предыдущей закрытой сделке
check_wtp = {symbol: [0,0] for symbol in symbols}

symbols_old = []
for key in alerts_MT:            
    symbols_old.append(key)


####### пороги, веса и проходной балл от 05.06 специально под фичу 0.5 и индикатор для 20 версии
WEIGHTS_2 = {"vol_lim": 0, "v05_lim": 0, "real_lim": 1, "w30_lim": 0, "w5_lim": 0,
             "V": 1, "05": 6, "R": 3, "W": 1, "w": 1, "Total": 56}

####### volume classifier ############
LIMITS_VOL_2 = {"label": ['v1/avg', 'v2/avg', 'v2/v1'],
                0:       [2,         0.0001,   0.0001],
                1:       [3.15,      0.5,      0.0001],
                2:       [4.3,       0.8,      0.0001],
                3:       [5.0,       1.1,      0.0001],
                4:       [5.7,       1.8,      0.0001],
                5:       [6.4,       2.5,      0.06  ],
                "comment": ['во сколько раз объёмы 1 свечи выше средних ДО A1', 
                            'во сколько раз объёмы 2 свечи выше средних ДО A1', 
                            'во сколько раз объёмы 1 свечи выше чем на 2 свече']}
# pd.DataFrame(LIMITS_VOL_2)  # отображает красиво табличку порогов с комментариями

def max_vol(x, max_v):
    if x >= max_v:
        return x/5
    else:
        return x

def vol_features_calc_2(data_in, alert_time=None):
    data = data_in.reset_index(drop=True).copy()      # без copy() меняем значение в базе, особенно важно при повторных запусках!
    if "Time_alert" in data.columns:
        alert_time = data.loc[data.index[0], 'Time_alert'] // 60000 * 60000  ### перестраховка, чтобы не было ошибок с timestamp
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

def vol_marc_detect_2(features_tpl, LIMITS_VOL_2):
    """Даёт оценку в баллах фиче антифрода - снижает баллы, если превышен порог этого балла по одному из показателей"""
    for mrk in (0, 1, 2, 3, 4, 5):
        iterator = zip(LIMITS_VOL_2[mrk], features_tpl, LIMITS_VOL_2["label"])
        labels = [f"{lab} < {lim}" for lim, val, lab in iterator if abs(val) < lim]
        if len(labels) > 0:
            return mrk, "\n    ".join(labels)
    return 6, ""           ############## 6 хорошо

# словарь порогов для объемов с 0.5 от 0506
LIMITS_V05_2 = {
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
# pd.DataFrame(LIMITS_V05_2)  # отображает красиво табличку порогов с комментариями

def get_05_time(data_in, alert_time=None, alert_price=None):
    """ эта и следущая - вспомогательные функции для определения времени 0.5
        по идее, если время задаётся, они не нужны.
        Но если   first_time_trade  не будет определяться, v05_calc() будет обращаться к ним"""
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
    return int(dt.strptime(dt_str, '%Y-%m-%d %H:%M:%S.%z').timestamp()) * 1000    

def vol_05_calc_2(data_in, alert_time=None, first_time_trade=None):
    """Считатет 7 параметров объёмов в конкретную минуту, изначально - при цене +0.5%"""
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

def vol_05_marc_detect_2(features_tpl, LIMITS_V05_2=LIMITS_V05_2):
    for mrk in range(6):
        iterator = zip(LIMITS_V05_2[mrk], features_tpl[:7], LIMITS_V05_2["label"])
        labels = [f"{lab} < {lim}" for lim, val, lab in iterator if abs(val) < lim]
        if len(labels) > 0:
            return mrk, "\n    ".join(labels)
    for mrk in range(12, 6, -2):
        iterator = zip(LIMITS_V05_2[mrk], features_tpl[:7], LIMITS_V05_2["label"])
        labels = [f"{lab} > {lim}" for lim, val, lab in iterator if abs(val) > lim]
        if len(labels) > 0:
            return mrk, "\n    ".join(labels)
    return 6, ""
####### volume classifier - конец вставки ############


############### long/short classifier ############
# словарь порогов для антифрода по лонг-шорт реализации
LIMITS_SHL_2 = {
    "label": ['total_real', 'total_33', 'short_real', 'long_real', 'short2_real', 'short2_time'], 
    0:       [12.1,          10.1,       8.0,          9.7,         8.4,           100         ],
    1:       [11.15,         8.4,        6.25,         7.9,         6.3,           100         ],
    2:       [10.2,          6.7,        4.5,          6.1,         4.2,           100         ],
    3:       [9.55,          5.9,        4.4,          4.5,         3.85,          100         ],
    4:       [8.9,           5.1,        4.3,          2.9,         3.5,           60.0        ],
    5:       [8.0,           4.3,        3.5,          2.5,         3.15,          36.0        ],
    "comment": ['суммарный % шорт-лонг реализации ДО A1', 'лонг-реализация 100% + шорт-реализация 33%',
                'абсолюное занчение 1й шорт-реализации в %', 'абсолюное занчение лонг-реализации в %',
                'абсолюное занчение 2й шорт-реализации в %', 'долгая 2я шорт-реал. (разница с лонг в мин.)']
}
# pd.DataFrame(LIMITS_SHL_2)  # отображает красиво табличку порогов с комментариями

def realis_calc_2(hi, lo, alert_price):
    """Считает числовые параметры шорт/лонг реализации по спискам Hi и Low за 90 минут до А1"""
    if lo[2:-2] == []:
        bot.send_message(error_tg, f"ver 20 lo[2:-2] == [] in realis_calc")  ### отладка - поиск min([])   -eg-    
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

def af_realis_detect_2(features_tpl, LIMITS_SHL_2):
    """Даёт оценку в баллах фиче антифрода - снижает баллы, если превышен порог этого балла по одному из показателей"""
    for mrk in (0, 1, 2, 3, 4, 5):
        iterator = zip(LIMITS_SHL_2[mrk], features_tpl, LIMITS_SHL_2["label"])
        labs = [f"{lab} > {lim}" for lim, val, lab in iterator if abs(val) > lim]
        if len(labs) > 0:
            return mrk, "\n    ".join(labs)
    return 6, ""           ############## 6 - если всё хорошо
############### long/short classifier - конец вставки ############


symbol_new=list(set(symbols)-set(symbols_old))
if len(symbol_new) != 0:
    for symbol in symbol_new:
        channel_price[symbol] = [[],[]]
        channel_time[symbol] = [[],[]] 
        alerts_MT[symbol] = [1,1] 
        channel_cond[symbol] = [[],[]]
        high_ser[symbol] = pd.Series([None])
        low_ser[symbol] = pd.Series([None])
        close_ser[symbol] = pd.Series([None])
        current_minute_prices[symbol] = []
        current_minute_start[symbol] = 0
        max_average_bar_price[symbol] = [0,0]
        # red_stop[symbol] = [None, None]
        orange_stop[symbol] = [None, None]
        yellow_stop[symbol] = [None, None]
        last_atr[symbol] = None
        orange_ten_min_start[symbol] = [0, 0]
        # ten_min_start[symbol] = [0, 0]
        sl_time[symbol] = [None, None]

name_col_a1 = ['symbol', 'time_open', 'time_close', 'open_price', 'close_price', 'pnl',
               'predict_vol', 'predict_05_vol','long_short', 'w30_score', 'w5_score']
try:
    
    a1_data_ver20 = pd.read_csv('/projects/Ver20/a1_data_ver20.csv', delimiter=',')
    if len(a1_data_ver20.columns) == 1:
        a1_data_ver20 = pd.read_csv('/projects/Ver20/a1_data_ver20.csv', delimiter=';')
    #print(a1_data)
except:
    a1_data_ver20 = pd.DataFrame(np.array([[0 for _ in range(len(name_col_a1))]]), columns=name_col_a1)

def trade_stat(symb, i, long_short_real, volume_05_real, volume_real, widths_real): 
    global a1_data_ver20
    pnl = round((channel_price[symb][i][-1] - channel_price[symb][i][-2])/channel_price[symb][i][-2] * 100, 2)
    a1_data_ver20.loc[len(a1_data_ver20.index)] = [symb, channel_time[symb][i][-2], channel_time[symb][i][-1], channel_price[symb][i][-2], channel_price[symb][i][-1], pnl,
                                                volume_real[symb][i],volume_05_real[symb][i],long_short_real[symb][i],widths_real[symb][i][0],widths_real[symb][i][1]]
    
def ver_trade(channel_data_price, symb, price_last_alert_algo_1, time_last_alert_algo_1, time_tick, price, alerts,
                channel_data_cline_10m,channel_data_cline_7m,channel_data_width_7m,channel_data_cline_4m,
                channel_data_width_3m, channel_data_cline_3m, channel_data_cline_2m, channel_data_cline_30s, koef, koef_base, last_psar_01,check_pump, last_psar_01_old,
                green_psar, k0, k1, price_acc, price_last_dinamic_sl, time_check_sl, last_10_avg_vol, zatupok,
                long_short_real, volume_05_real, volume_real, widths_real): 

        
        def kline_MT(i,k, average_bar_price):   
            
            if check_wtp[symb][i] == 0:
                if price_acc[symb] == []:
                    bot.send_message(error_tg, f'ver 20 price_acc[{symb}] == [] in kline_MT_9({i}, {k})')  ### отладка - поиск min([])   -eg-
                min3 = min(price_acc[symb][-3:])
                if (price - min3) / min3 * 100  >= 3: #and (price - price_last_alert_algo_1[symb][i] * 1.03) / price_last_alert_algo_1[symb][i] * 100  >= 3:
                    check_wtp[symb][i] = 1
               

            # открытие сделки на резком взлете на первой минуте
            if alerts_MT[symb][i] == 1 and\
                time_tick < time_last_alert_algo_1[symb][i] + 1 * 60 * 1000 and price > price_last_alert_algo_1[symb][i] * 1.005: # вход
                channel_price[symb][i] = channel_price[symb][i] + [price]
                channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                alerts_MT[symb][i] = 2
                channel_cond[symb][i] = channel_cond[symb][i] + ['on']

                try:
                    last_atr[symb] = ta.atr(high_ser[symb], low_ser[symb], 
                                            close_ser[symb][-len(high_ser[symb]):],    ### срез для выравнивания длины серий
                                            length=PARAMS["length"]).tolist()[-1]
#                         print(last_atr[symb])
                    if not last_atr[symb]:  # чтобы nan не кидало при коротких сериях
                        last_atr[symb] = ta.atr(high_ser[symb], low_ser[symb], 
                                                close_ser[symb][-len(high_ser[symb]):],  ### срез для выравнивания длины серий
                                                length=PARAMS["length"] // 3).tolist()[-1]
                except: pass  

                orange_stop[symb][i] = price * 0.998 - PARAMS["down_osl"] * float(last_atr[symb])  # -1,8*ATR
                yellow_stop[symb][i] = price * 0.998 - PARAMS["down_ysl"] * float(last_atr[symb])  # -3*ATR
                orange_ten_min_start[symb][i] = time_tick // 60000 * 60000  # начало отсчёта лесенки 

            # открытие первой сделки (не on)
            elif alerts_MT[symb][i] == 1 and len(channel_price[symb][i]) == 0 and price >= price_last_alert_algo_1[symb][i] * 1.005:
                channel_price[symb][i] = channel_price[symb][i] + [price]
                channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                alerts_MT[symb][i] = 2
                channel_cond[symb][i] = channel_cond[symb][i] + ['op05']
                sl_time[symb][i] = None
                
                # 1 раз при каждом входе в лонг
                if alerts_MT[symb][i] == 2 and orange_stop[symb][i] == None:
                    try:    
                        last_atr[symb] = ta.atr(high_ser[symb], low_ser[symb], 
                                                close_ser[symb][-len(high_ser[symb]):],    ### срез для выравнивания длины серий
                                                length=PARAMS["length"]).tolist()[-1]
                        if not last_atr[symb]:  # чтобы nan не кидало при коротких сериях
                            last_atr[symb] = ta.atr(high_ser[symb], low_ser[symb], 
                                                    close_ser[symb][-len(high_ser[symb]):],  ### срез для выравнивания длины серий
                                                    length=PARAMS["length"] // 3).tolist()[-1]
                    except: pass  

                    orange_stop[symb][i] = price * 0.998 - PARAMS["down_osl"] * float(last_atr[symb])  # -1,8*ATR
                    yellow_stop[symb][i] = price * 0.998 - PARAMS["down_ysl"] * float(last_atr[symb])  # -3*ATR
                    orange_ten_min_start[symb][i] = time_tick // 60000 * 60000  # начало отсчёта лесенки 

            # открытие сделки 
            
            elif (((channel_data_cline_3m[symb][i][-1] > 1.6 * k[15]) & (all(elem > 1.6 * k[16] for elem in channel_data_cline_3m[symb][i][-1 - 60:-1])) and len(channel_time[symb][i]) > 0) or (price > price_last_alert_algo_1[symb][i] * 1.005 and len(channel_time[symb][i]) == 0)) and\
                    (alerts_MT[symb][i] == 1 or (alerts_MT[symb][i] == 4 and time_tick >= channel_time[symb][i][-1] + 4 * 60 * 1000) or (alerts_MT[symb][i] == 5 and time_tick >= channel_time[symb][i][-1] + 1.5 * 60 * 1000)) and\
                    ((len(channel_time[symb][i]) > 0 and time_tick >= channel_time[symb][i][-1] + 90 * 1000) or (len(channel_time[symb][i]) == 0 and time_tick >= time_last_alert_algo_1[symb][i] + 90 * 1000)) and\
                    ((time_tick < time_last_alert_algo_1[symb][i] + 40 * 60 * 1000) or (time_tick >= time_last_alert_algo_1[symb][i] + 40 * 60 * 1000 and check_pump[symb][i])) and\
                    time_tick < time_last_alert_algo_1[symb][i] + 2 * 60 * 60 * 1000 and price > price_last_alert_algo_1[symb][i] * 1.005 and\
                    (len(channel_price[symb][i]) == 0 or (len(channel_price[symb][i]) >= 2 and price > max(channel_price[symb][i]) * 1.005)): # вход
                    channel_price[symb][i] = channel_price[symb][i] + [price]
                    channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                    alerts_MT[symb][i] = 2
                    channel_cond[symb][i] = channel_cond[symb][i] + ['ops']
                    # 1 раз при каждом входе в лонг
                    if alerts_MT[symb][i] == 2 and orange_stop[symb][i] == None:
                        try:
                            last_atr[symb] = ta.atr(high_ser[symb], low_ser[symb], 
                                                close_ser[symb], 
                                                length=PARAMS["length"]).tolist()[-1]
                        except:
                            if not last_atr[symb]:  # чтобы nan не кидало при коротких сериях
                                last_atr[symb] = ta.atr(high_ser[symb], low_ser[symb], 
                                                        close_ser[symb], 
                                                        length=PARAMS["length"] // 3).tolist()[-1]
                        orange_stop[symb][i] = price * 0.998 - PARAMS["down_osl"] * float(last_atr[symb])  # -1,8*ATR
                        yellow_stop[symb][i] = price * 0.998 - PARAMS["down_ysl"] * float(last_atr[symb])  # -3*ATR
                        orange_ten_min_start[symb][i] = time_tick // 60000 * 60000  # начало отсчёта лесенки
            

            elif (alerts_MT[symb][i] == 2 and time_tick >= channel_time[symb][i][-1] + 2 * 60 * 1000 and\
                    ((time_tick < time_last_alert_algo_1[symb][i] + 40 * 60 * 1000) or (time_tick >= time_last_alert_algo_1[symb][i] + 40 * 60 * 1000 and check_pump[symb][i])) and\
                    ((abs(channel_data_cline_4m[symb][i][-1] - channel_data_cline_7m[symb][i][-1]) < k[0]) & ((channel_data_cline_4m[symb][i][-1 - 10] - channel_data_cline_4m[symb][i][-1]) > k[1]) & (channel_data_cline_4m[symb][i][-1] > k[2]) & (channel_data_width_7m[symb][i][-1] < k[3]) & (channel_data_width_3m[symb][i][-1] > k[4]))): # 1 возможность перегиба
                        channel_price[symb][i] = channel_price[symb][i] + [price]
                        channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                        alerts_MT[symb][i] = 1
                        channel_cond[symb][i] = channel_cond[symb][i] + ['c1']
                        orange_stop[symb][i] = None
                        trade_stat(symb, i, long_short_real, volume_05_real, volume_real, widths_real)
                
            elif ((alerts_MT[symb][i] == 2 and time_tick >= channel_time[symb][i][-1] + 2 * 60 * 1000) and\
                    ((time_tick < time_last_alert_algo_1[symb][i] + 40 * 60 * 1000) or (time_tick >= time_last_alert_algo_1[symb][i] + 40 * 60 * 1000 and check_pump[symb][i])) and\
                    ((abs(channel_data_cline_4m[symb][i][-1] - channel_data_cline_7m[symb][i][-1]) < 1.5 * k[9]) & ((channel_data_cline_4m[symb][i][-1 - 10] - channel_data_cline_4m[symb][i][-1]) > 1.5 * k[10]) & (channel_data_cline_4m[symb][i][-1] > 1.5 * k[11]) & (channel_data_width_7m[symb][i][-1] < 0.5 * k[12]) & ((channel_data_cline_2m[symb][i][-1] - channel_data_cline_2m[symb][i][-1 - 10]) > 0.5 * k[13]) & (channel_data_cline_2m[symb][i][-1] < k[14]))): # 2 возможность перегиба
                        channel_price[symb][i] = channel_price[symb][i] + [price]
                        channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                        alerts_MT[symb][i] = 1
                        channel_cond[symb][i] = channel_cond[symb][i] + ['c2']
                        orange_stop[symb][i] = None
                        trade_stat(symb, i, long_short_real, volume_05_real, volume_real, widths_real)
            
            # ver4 
            elif (((alerts_MT[symb][i] == 0 and time_tick >= time_last_alert_algo_1[symb][i] + 2 * 60 * 1000) or (alerts_MT[symb][i] == 2 and time_tick >= channel_time[symb][i][-1] + 1 * 60 * 1000)) and\
                ((time_tick < time_last_alert_algo_1[symb][i] + 40 * 60 * 1000) or (time_tick >= time_last_alert_algo_1[symb][i] + 40 * 60 * 1000 and check_pump[symb][i])) and\
                price >= price_last_alert_algo_1[symb][i] * 1.03 and\
                ((abs(channel_data_cline_4m[symb][i][-1] - channel_data_cline_7m[symb][i][-1])< 0.0005) and\
                (channel_data_cline_4m[symb][i][-1-10] - channel_data_cline_4m[symb][i][-1]> 0.0009) and\
                (channel_data_cline_4m[symb][i][-1] > 0.006) and\
                (channel_data_width_7m[symb][i][-1] < 0.85) and\
                (channel_data_width_3m[symb][i][-1] > 0.3))): # 1 возможность перегиба
                    channel_price[symb][i] = channel_price[symb][i] + [price]
                    channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                    alerts_MT[symb][i] = 1
                    channel_cond[symb][i] = channel_cond[symb][i] + ['c4']
                    orange_stop[symb][i] = None
                    trade_stat(symb, i, long_short_real, volume_05_real, volume_real, widths_real)

            # DE
            elif (alerts_MT[symb][i] == 2 and time_tick >= channel_time[symb][i][-1] + 2 * 60 * 1000) and\
                ((time_tick < time_last_alert_algo_1[symb][i] + 40 * 60 * 1000) or (time_tick >= time_last_alert_algo_1[symb][i] + 40 * 60 * 1000 and check_pump[symb][i])) and\
                ((max(price_acc[symb][-3:]) - price) / max(price_acc[symb][-3:]) * 100  >  1) and check_wtp[symb][i]:
                    channel_price[symb][i] = channel_price[symb][i] + [price]
                    channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                    alerts_MT[symb][i] = 1
                    check_wtp[symb][i] = 0
                    channel_cond[symb][i] = channel_cond[symb][i] + ['cDE']
                    orange_stop[symb][i] = None
                    trade_stat(symb, i, long_short_real, volume_05_real, volume_real, widths_real)

             
                    
            
            #green_psar_1
            elif (alerts_MT[symb][i] == 2 and time_tick >= channel_time[symb][i][-1] + 2 * 60 * 1000) and\
                (time_tick < time_last_alert_algo_1[symb][i] + 50 * 60 * 1000) and green_psar[symb][1] <= 5 and\
                price >= price_last_alert_algo_1[symb][i] * 1.015 and last_psar_01[symb][0] > price:
                    channel_price[symb][i] = channel_price[symb][i] + [price]
                    channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                    alerts_MT[symb][i] = 1
                    channel_cond[symb][i] = channel_cond[symb][i] + ['cps1']
                    orange_stop[symb][i] = None
                    trade_stat(symb, i, long_short_real, volume_05_real, volume_real, widths_real)

            #green_psar_2
            elif (alerts_MT[symb][i] == 2 and time_tick >= channel_time[symb][i][-1] + 2 * 60 * 1000) and\
                (time_tick >= time_last_alert_algo_1[symb][i] + 50 * 60 * 1000) and green_psar[symb][0] >= 49 and\
                price >= price_last_alert_algo_1[symb][i] * 1.025 and last_psar_01[symb][0] > price and\
                green_psar[symb][1] <= 5:
                    channel_price[symb][i] = channel_price[symb][i] + [price]
                    channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                    alerts_MT[symb][i] = 3
                    channel_cond[symb][i] = channel_cond[symb][i] + ['cps2']
                    orange_stop[symb][i] = None
                    trade_stat(symb, i, long_short_real, volume_05_real, volume_real, widths_real)

            # zatupok

            elif (alerts_MT[symb][i] == 2 and time_tick >= channel_time[symb][i][-1] + 10 * 60 * 1000 and time_tick >= channel_time[symb][i][-1] + 17 * 60 * 1000) and\
                last_10_avg_vol[symb] <= zatupok[symb][i] * 0.65 and price <= channel_price[symb][i][-1] * 1.007 and\
                len(channel_price[symb][i]) == 1 and\
                ((price_acc[symb][-1] < price_acc[symb][-2] and price_acc[symb][-2] < price_acc[symb][-3] and price_acc[symb][-1] > min(price_acc[symb][-10:]) * 1.003) or (price >= channel_price[symb][i][-1] * 1.004)):
                    channel_price[symb][i] = channel_price[symb][i] + [price]
                    channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                    alerts_MT[symb][i] = 1
                    check_wtp[symb][i] = 0
                    channel_cond[symb][i] = channel_cond[symb][i] + ['ztpk']
                    orange_stop[symb][i] = None
                    check_wtp[symb][i] = 0
                    trade_stat(symb, i, long_short_real, volume_05_real, volume_real, widths_real)

            # stoploss 1%

            elif (alerts_MT[symb][i] == 2 and time_tick >= channel_time[symb][i][-1] + 1 * 60 * 1000) and\
                price <= price_last_alert_algo_1[symb][i] * 0.995:
                    channel_price[symb][i] = channel_price[symb][i] + [price]
                    channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                    alerts_MT[symb][i] = 1
                    check_wtp[symb][i] = 0
                    channel_cond[symb][i] = channel_cond[symb][i] + ['sl1%']
                    orange_stop[symb][i] = None
                    check_wtp[symb][i] = 0
                    trade_stat(symb, i, long_short_real, volume_05_real, volume_real, widths_real)

            # экстренное закрытие сделки после резкого взлета на первой минуте
            elif alerts_MT[symb][i] == 2 and len(channel_price[symb][i]) == 1 and\
                time_tick < time_last_alert_algo_1[symb][i] + 1 * 60 * 1000 and price <= channel_price[symb][i][-1] * 0.995: # вход
                channel_price[symb][i] = channel_price[symb][i] + [price]
                channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                alerts_MT[symb][i] = 5
                channel_cond[symb][i] = channel_cond[symb][i] + ['off'] 
                orange_stop[symb][i] = None
                trade_stat(symb, i, long_short_real, volume_05_real, volume_real, widths_real)

########################################################### Вставка 3 SL                    
            # red SL =-0.7% от алерта, затем через 30 мин +0.5% каждые 10 мин.  
            # orange SL =-1.5*ATR от входа в лонг, затем через 20 мин +0.5% каждые 10 мин.  
            # elif alerts_MT[symb][i] == 2 and red_stop[symb][i] != None and price < red_stop[symb][i]:
            #         channel_price[symb][i] = channel_price[symb][i] + [price]
            #         channel_time[symb][i] = channel_time[symb][i] + [time_tick]
            #         alerts_MT[symb][i] = 1
            #         channel_cond[symb][i] = channel_cond[symb][i] + ['R'] 
            #         orange_stop[symb][i] = None 
                    
            # orange SL =-1.5*ATR от входа в лонг, затем через 20 мин +0.5% каждые 10 мин.  
            elif not sl_time[symb][i] and alerts_MT[symb][i] == 2 and orange_stop[symb][i] != None and price < orange_stop[symb][i]:
                    sl_time[symb][i] = time_tick   ### вместо выхода запускается отсчёт времени (1,5 мин до выхода)

            # yellow SL =-2.4*ATR от входа в лонг, затем =-2.4*ATR от максимума цены
            # (растёт с ростом цены каждую минуту)
            elif not sl_time[symb][i] and alerts_MT[symb][i] == 2 and yellow_stop[symb][i] != None and price < yellow_stop[symb][i]:
                    sl_time[symb][i] = time_tick   ### вместо выхода запускается отсчёт времени (3 мин до выхода)
            
            # Проверка временем стопов (3 мин. для O, 90 сек. для Y, 45 сек. для O+Y)
            elif alerts_MT[symb][i] == 2 and sl_time[symb][i] and yellow_stop[symb][i] != None and orange_stop[symb][i] != None and price > orange_stop[symb][i] and price > yellow_stop[symb][i]:
                    sl_time[symb][i] = None        ### сброс времени при возврате цены выше стопов
            elif alerts_MT[symb][i] == 2 and sl_time[symb][i] and yellow_stop[symb][i] != None and orange_stop[symb][i] != None and time_tick > sl_time[symb][i] + PARAMS["sl_time"] * 60 * 1000:  ### 3 минуты
                    channel_price[symb][i] = channel_price[symb][i] + [price]
                    channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                    alerts_MT[symb][i] = 1
                    # пометка на скрине заистит от сработавших стопов на момент выхода
                    if price <= yellow_stop[symb][i] and price <= orange_stop[symb][i]:
                        channel_cond[symb][i] = channel_cond[symb][i] + ['YO']
                    elif price <= yellow_stop[symb][i]:
                        channel_cond[symb][i] = channel_cond[symb][i] + ['Y']
                    elif price <= orange_stop[symb][i]:
                        channel_cond[symb][i] = channel_cond[symb][i] + ['O']
                    else:
                        channel_cond[symb][i] = channel_cond[symb][i] + ['?']  ### не должны сюда попасть, но мало ли
                    sl_time[symb][i] = None       ### сброс времени после срабатывания
                    orange_stop[symb][i] = None
                    trade_stat(symb, i, long_short_real, volume_05_real, volume_real, widths_real)
                # Если оба стопа активны, за 1 сек. смещаем время проверки на 4 секунды (-3)
            elif alerts_MT[symb][i] == 2 and sl_time[symb][i] and yellow_stop[symb][i] != None and orange_stop[symb][i] != None and price < orange_stop[symb][i] and price < yellow_stop[symb][i]:
                    sl_time[symb][i] = sl_time[symb][i] - 3 * 1000
                # Если только Y-стоп, за 1 сек. смещаем время проверки на 2 секунды (-1)
            elif alerts_MT[symb][i] == 2 and sl_time[symb][i] and yellow_stop[symb][i] != None and orange_stop[symb][i] != None and price < yellow_stop[symb][i]:
                    sl_time[symb][i] = sl_time[symb][i] - 1 * 1000  
##################################################### Конец вставки 3 SL


            # закрытие по last trade
            elif (alerts_MT[symb][i] == 2) and len(channel_price[symb][i]) >=2 and\
                channel_price[symb][i][-1] > channel_price[symb][i][-2] and time_tick >= channel_time[symb][i][-1] + last_trade_ignore_bar_number * 60 * 1000 and time_tick < channel_time[symb][i][-1] + last_trade_check_bar_number * 60 * 1000 and\
                (channel_price[symb][i][-1] - channel_price[symb][i][-2] > last_trade_valid_pnl or price > price_last_alert_algo_1[symb][i] * 1.04) and\
                price < channel_price[symb][i][-1]:
                    channel_price[symb][i] = channel_price[symb][i] + [price]
                    channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                    alerts_MT[symb][i] = 1
                    channel_cond[symb][i] = channel_cond[symb][i] + ['LT']
                    orange_stop[symb][i] = None
                    trade_stat(symb, i, long_short_real, volume_05_real, volume_real, widths_real)
                    


            # закрытие по закруглениям DE
            elif (alerts_MT[symb][i] == 2) and len(channel_price[symb][i]) != 0 and max_average_bar_price[symb][i] != 0 and\
                time_tick >= channel_time[symb][i][-1] + 5 * 60 * 1000 and\
                ((average_bar_price / max_average_bar_price[symb][i]) - 1) * 100 <= -0.5:
                    channel_price[symb][i] = channel_price[symb][i] + [price]
                    channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                    alerts_MT[symb][i] = 1
                    channel_cond[symb][i] = channel_cond[symb][i] + ['cCV']
                    orange_stop[symb][i] = None
                    trade_stat(symb, i, long_short_real, volume_05_real, volume_real, widths_real)

            elif (alerts_MT[symb][i] == 2) and time_tick > time_last_alert_algo_1[symb][i] + 2 * 60 * 60 * 1000:
                    alerts_MT[symb][i] = 3
                    channel_price[symb][i] = channel_price[symb][i] + [price]
                    channel_time[symb][i] = channel_time[symb][i] + [time_tick]
                    channel_cond[symb][i] = channel_cond[symb][i] + ['e']
                    # red_stop[symb][i] = None
                    orange_stop[symb][i] = None
                    trade_stat(symb, i, long_short_real, volume_05_real, volume_real, widths_real)

        if alerts[symb][0] >= 1 and time_tick < time_last_alert_algo_1[symb][0] + 2.1 * 60 * 60 * 1000:
            try:
                #pr_k = (price-price_last_alert_algo_1[symb][0])/price_last_alert_algo_1[symb][0]*100
                #if pr_k < 3:
                #    pr_k = 3
                #elif pr_k > 11:
                #    pr_k = 10
                #k = [k * pr_k / (koef_base - 1/pr_k) for k in koef]
                #cline_width(0)
                average_bar_price = (price_acc[symb][-1] + price_acc[symb][-2]) / 2
                if time_tick >= current_minute_start[symb] + 60 * 1000:  ### фильтр входа на хаях
                    
                    # # Движение красного стопа:
                    # if time_tick >= ten_min_start[symb][0] + 10 * 60 * 1000:
                    #     if time_tick >= time_last_alert_algo_1[symb][0] + 29 * 60 * 1000 and red_stop[symb][0] != None:
                    #         red_stop[symb][0] = red_stop[symb][0] + price_last_alert_algo_1[symb][0] * PARAMS["step_rsl"] * 0.01           # =0.5
                    #     ten_min_start[symb][0] = ten_min_start[symb][0] + 10 * 60 * 1000

                    # Движение оранжевого стопа:
                    if time_tick >= orange_ten_min_start[symb][0] + 10 * 60 * 1000:  ### Потом можно убрать, когда сделаем:
                        orange_ten_min_start[symb][0] = orange_ten_min_start[symb][0] + 10 * 60 * 1000              ### (ten_min_start = orange_ten_min_start)
                        if (orange_stop[symb][0] != None and len(channel_time[symb][0]) != 0 and time_tick >= channel_time[symb][0][-1] + 14 * 60 * 1000):
                            orange_stop[symb][0] = orange_stop[symb][0] + price * 0.01 * PARAMS["step_osl"]  #* atr[i_n]  ### можно привязать к ATR

                    # Движение жёлтого стопа:
                    if (orange_stop[symb][0] != None and\
                        time_tick >= current_minute_start[symb] + 59 * 1000 and\
                        (price > high_ser[symb].iloc[-1] or high_ser[symb].iloc[-1] > high_ser[symb].iloc[-2])):
                            yellow_stop[symb][0] =  0.998 * max(price, high_ser[symb].iloc[-1]) - PARAMS["down_ysl"] * last_atr[symb]

                    

                    ##### закругления ДЕ #####
                    

                    # условия для начала отслеживания средних значений тела бара
                    if len(channel_price[symb][0]) != 0: 
                        general_conditions = [
                            time_tick - channel_time[symb][0][-1] > 5 * 60 * 1000,
                            average_bar_price > channel_price[symb][0][-1],
                        ]

                        if max_average_bar_price[symb][0] == 0 and all(general_conditions):
                            max_average_bar_price[symb][0] = average_bar_price
                        
                        elif max_average_bar_price[symb][0] != 0 and average_bar_price >= max_average_bar_price[symb][0]:
                            max_average_bar_price[symb][0] = average_bar_price

                    else:
                        max_average_bar_price[symb][0] = 0

                kline_MT(0,k0, average_bar_price)
            except Exception as e:
                # pass
                bot.send_message(error_tg, f'ver 20 kline_MT(0,k) fail {symb}\n\n{e}')

        if alerts[symb][1] >= 1 and time_tick < time_last_alert_algo_1[symb][1] + 2.1 * 60 * 60 * 1000:
            #try:
                #pr_k = (price-price_last_alert_algo_1[symb][1])/price_last_alert_algo_1[symb][1]*100
                #if pr_k < 3:
                #    pr_k = 3
                #elif pr_k > 11:
                #    pr_k = 10
                #k = [k * pr_k / (koef_base - 1/pr_k) for k in koef]
                #cline_width(1)
                
                    
                average_bar_price = (price_acc[symb][-1] + price_acc[symb][-2]) / 2
                if time_tick >= current_minute_start[symb] + 60 * 1000:  ### каждую минуту
                    # # Движение красного стопа:
                    # if time_tick >= ten_min_start[symb][1] + 10 * 60 * 1000:
                    #     if time_tick >= time_last_alert_algo_1[symb][1] + 29 * 60 * 1000 and red_stop[symb][1] != None:
                    #         red_stop[symb][1] += price_last_alert_algo_1[symb][1] * PARAMS["step_rsl"] * 0.01           # =0.5
                    #     ten_min_start[symb][1] += 10 * 60 * 1000

                    # Движение оранжевого стопа:
                    if time_tick >= orange_ten_min_start[symb][1] + 10 * 60 * 1000:  ### Потом можно убрать, когда сделаем:
                        orange_ten_min_start[symb][1] += 10 * 60 * 1000              ### (ten_min_start = orange_ten_min_start)
                        if (orange_stop[symb][1] != None and len(channel_time[symb][0]) != 0 and time_tick >= channel_time[symb][1][-1] + 14 * 60 * 1000):
                            orange_stop[symb][1] += price * 0.01 * PARAMS["step_osl"]  #* atr[i_n]  ### можно привязать к ATR

                    # Движение жёлтого стопа:
                    if (orange_stop[symb][1] != None and\
                        time_tick >= current_minute_start[symb] + 59 * 1000 and\
                        (price > high_ser[symb].iloc[-1] or high_ser[symb].iloc[-1] > high_ser[symb].iloc[-2])):
                            yellow_stop[symb][1] =  0.998 * max(price, high_ser[symb].iloc[-1]) - PARAMS["down_ysl"] * last_atr[symb]


                    ##### закругления ДЕ #####
                    

                    # условия для начала отслеживания средних значений тела бара
                    if len(channel_price[symb][1]) != 0:
                        general_conditions = [
                            time_tick - channel_time[symb][1][-1] > 5 * 60 * 1000,
                            average_bar_price > channel_price[symb][1][-1],
                        ]

                        if max_average_bar_price[symb][1] == 0 and all(general_conditions):
                            max_average_bar_price[symb][1] = average_bar_price
                        
                        elif max_average_bar_price[symb][1] != 0 and average_bar_price >= max_average_bar_price[symb][1]:
                            max_average_bar_price[symb][1] = average_bar_price

                    else:
                        max_average_bar_price[symb][1] = 0

                    cummul_chandle_calc(time_tick=time_tick, price=price, symb=symb, i=1,
                                        s_len = PARAMS["length"] + 12)  ### здесь +12 прописал, можно в функции не править

                    ##### закругления ДЕ #####

                    current_minute_start[symb] = current_minute_start[symb] + 60 * 1000

                kline_MT(1,k1, average_bar_price)
            #except Exception as e:
                # pass
            #    bot.send_message(error_tg, f'ver 20 kline_MT(1,k) fail {symb}\n\n{e}')


def rewrite(symb, price, time, channel_data_price, price_acc, high_acc, low_acc):
    
    try:

        if symb not in channel_price:
            channel_price[symb] = [[],[]]
        if symb not in channel_time:
            channel_time[symb] = [[],[]] 
        if symb not in alerts_MT:
            alerts_MT[symb] = [1,1] 
        if symb not in channel_cond:   
            channel_cond[symb] = [[],[]]
        if symb not in high_ser:   
            high_ser[symb] = pd.Series([None])
        if symb not in low_ser:  
            low_ser[symb] = pd.Series([None])
        if symb not in close_ser:
            close_ser[symb] = pd.Series([None])
        if symb not in current_minute_prices:
            current_minute_prices[symb] = []
        if symb not in current_minute_start:
            current_minute_start[symb] = 0
        if symb not in max_average_bar_price:
            max_average_bar_price[symb] = [0,0]
        # if symb not in red_stop:
        #     red_stop[symb] = [None, None]
        if symb not in orange_stop:
            orange_stop[symb] = [None, None]
        if symb not in yellow_stop:
            yellow_stop[symb] = [None, None]
        if symb not in last_atr:
            last_atr[symb] = None
        if symb not in orange_ten_min_start:
            orange_ten_min_start[symb] = [0, 0]
        # if symb not in ten_min_start:
        #     ten_min_start[symb] = [0, 0]
        if symb not in sl_time:
            sl_time[symb] = [None, None]
        if symb not in check_wtp:
            check_wtp[symb] = [0, 0]
        if symb not in max_average_bar_price:
            max_average_bar_price[symb] = [0, 0]

        channel_price[symb][0] = channel_price[symb][1]
        channel_time[symb][0] = channel_time[symb][1]

        sl_time[symb][0] = sl_time[symb][1]
        sl_time[symb][1] = None

        channel_price[symb][1] = []
        channel_time[symb][1] = []
        alerts_MT[symb][0] = alerts_MT[symb][1]
        alerts_MT[symb][1] = 1 

        channel_cond[symb][0] = channel_cond[symb][1]
        channel_cond[symb][1] = []

        check_wtp[symb][0] = check_wtp[symb][1]
        check_wtp[symb][1] = 0

        max_average_bar_price[symb][0] = max_average_bar_price[symb][1]
        max_average_bar_price[symb][1] = 0

        
        #high_ser[symb], low_ser[symb], close_ser[symb] = calc_prev_min_chandles(channel_data_price, symb, 1)
        high_ser[symb], low_ser[symb], close_ser[symb] = pd.Series(high_acc[symb][-49:]), pd.Series(low_acc[symb][-49:]), pd.Series(price_acc[symb][-49:])
        
        current_minute_start[symb] = time // 60000 * 60000
        current_minute_prices[symb] = []

        

        # red_stop[symb][0] = red_stop[symb][1]
        # ten_min_start[symb][0] = ten_min_start[symb][1]
        orange_stop[symb][0] = orange_stop[symb][1]
        yellow_stop[symb][0] = yellow_stop[symb][1]
        orange_ten_min_start[symb][0] = orange_ten_min_start[symb][1]
        orange_stop[symb][1] = None
        yellow_stop[symb][1] = None
        # red_stop[symb][1] = None
        orange_ten_min_start[symb][1] = 0
        # if red_stop[symb][1] is None:  
        #     red_stop[symb][1] = (price * (1 - PARAMS["down_rsl"] * 0.01))             # =0.7  
        # ten_min_start[symb][1] = time // 60000 * 60000      ### условие выполняется только 1 раз при получении алерта
    
    except Exception as e:
        bot.send_message(error_tg, f'rewrite 20\n\n{e}')
    


def save():

    global a1_data_ver20

    try:
        with open('/projects/Ver20/channel_price.txt', 'w') as file:
            file.write(json.dumps(channel_price))
                
        with open('/projects/Ver20/channel_time.txt', 'w') as file:
            file.write(json.dumps(channel_time))

        with open('/projects/Ver20/alerts_MT.txt', 'w') as file:
            file.write(json.dumps(alerts_MT)) 

        with open('/projects/Ver20/channel_cond.txt', 'w') as file:
            file.write(json.dumps(channel_cond))   

        with open(f'/projects/Ver20/stats/{str(day_check)}_stat.txt', 'w') as file:
            file.write(json.dumps(alerts_stat))

        with open('/projects/Ver20/stats/alerts_stat.txt', 'w') as file:
            file.write(json.dumps(alerts_stat))
            
        with open('/projects/Ver20/stats/day_check.txt', 'w') as file:
            file.write(json.dumps(day_check))

        with open('/projects/Ver20/stats_4h/alerts_stat.txt', 'w') as file:
            file.write(json.dumps(alerts_stat_4h))

        with open('/projects/Ver20/stats_4h/alerts_stat_1h.txt', 'w') as file:
            file.write(json.dumps(alerts_stat_1h))
            
        with open('/projects/Ver20/stats_4h/hour_check_1h.txt', 'w') as file:
            file.write(json.dumps(hour_check_1h))
        
        with open('/projects/Ver20/sl_time.txt', 'w') as file:
            file.write(json.dumps(sl_time))

        a1_data_ver20.to_csv('/projects/Ver20/a1_data_ver20.csv', index=False)

        high_ser_dict = {}
        for i in high_ser:
            high_ser_dict[i] = high_ser[i].to_list()

        with open('/projects/Ver20/high_ser.txt', 'w') as file:
            file.write(json.dumps(high_ser_dict)) 
        del high_ser_dict

        low_ser_dict = {}
        for i in low_ser:
            low_ser_dict[i] = low_ser[i].to_list()
        with open('/projects/Ver20/low_ser.txt', 'w') as file:
            file.write(json.dumps(low_ser_dict)) 
        del low_ser_dict
        
        close_ser_dict = {}
        for i in close_ser:
            close_ser_dict[i] = close_ser[i].to_list()
        with open('/projects/Ver20/close_ser.txt', 'w') as file:
            file.write(json.dumps(close_ser_dict))
        del close_ser_dict 

        with open('/projects/Ver20/current_minute_start.txt', 'w') as file:
            file.write(json.dumps(current_minute_start))

        with open('/projects/Ver20/current_minute_prices.txt', 'w') as file:
            file.write(json.dumps(current_minute_prices))

        with open('/projects/Ver20/count_trades.txt', 'w') as file:
            file.write(json.dumps(count_trades))

        with open('/projects/Ver20/time_last_kline.txt', 'w') as file:
            file.write(json.dumps(time_last_kline))

        # with open('/projects/Ver20/red_stop.txt', 'w') as file:
        #     file.write(json.dumps(red_stop))

        with open('/projects/Ver20/orange_stop.txt', 'w') as file:
            file.write(json.dumps(orange_stop))
        
        with open('/projects/Ver20/yellow_stop.txt', 'w') as file:
            file.write(json.dumps(yellow_stop))

        with open('/projects/Ver20/last_atr.txt', 'w') as file:
            file.write(json.dumps(last_atr))

        with open('/projects/Ver20/orange_ten_min_start.txt', 'w') as file:
            file.write(json.dumps(orange_ten_min_start))

        # with open('/projects/Ver20/ten_min_start.txt', 'w') as file:
        #     file.write(json.dumps(ten_min_start))

        with open('/projects/Ver20/max_average_bar_price.txt', 'w') as file:
            file.write(json.dumps(max_average_bar_price))


    except:
        pass


def screen(symb, i, df, time_last_alert_algo_1, price_last_alert_algo_1):
        global day_check, hour_check_1h, count_trades
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
            df['Number of trades'] = df['Number of trades'].astype(int)
            df['Volume'] = df['Volume'].astype(float)
            df['Taker buy base asset volume'] = df['Taker buy base asset volume'].astype(float)


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
            df['open_cond'] = None
            df['close_cond'] = None 
            df['pnl_description'] = None
            ######################################### Для отрисовки стоп-лоссов - EG
            df["atr"] = ta.atr(df.High, df.Low, df.Close, length=PARAMS["length"], offset = 1, 
                            drift=1) / price_last_alert_algo_1[i] * 100
        ######################### Конец вставки "Для отрисовки стоп-лоссов" - EG 

            ind = df[df['Time'] >= time_alert].index.values.astype(int)[:1]
            
            ind_1_line = ind[0] - 15
            ind_2_line = ind[0] + 120 + 1
            
            line_1 = time_alert - 15 * 60 * 1000 + 3 * 60 * 60 * 1000
            line_2 = time_alert + 120 * 60 * 1000 + 3 * 60 * 60 * 1000
            df_line = pd.DataFrame({'Data': [line_1, line_2]})
            df_line['Data_line'] = pd.to_datetime(df_line['Data'], unit = 'ms')
            
            #try:
            
            if len(channel_time[symb][i]) % 2 == 1:
                channel_time[symb][i] = channel_time[symb][i] + [int(time_alert + 120 * 60 * 1000)]
                channel_price[symb][i] = channel_price[symb][i] + [float(df.iloc[ind[0]+120]['Close'])]
                channel_cond[symb][i] = channel_cond[symb][i] + ['e']

            # ver
            MT_pnl = []
            for k in range(len(channel_time[symb][i])):
                if k % 2 == 0:
                    time_open = int(channel_time[symb][i][k] - (channel_time[symb][i][k] % 60000))
                    ind_time_open = df[df['Time'] == time_open].index.values.astype(int)
                    df.loc[ind_time_open[0], 'price_open'] = round((float(channel_price[symb][i][k]) - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
                    try:
                        df.loc[ind_time_open[0], 'open_cond'] = channel_cond[symb][i][k]
                    except: pass

                if k % 2 == 1:
                    time_close = int(channel_time[symb][i][k] - (channel_time[symb][i][k] % 60000))
                    ind_time_close = df[df['Time'] == time_close].index.values.astype(int)
                    df.loc[ind_time_close[0], 'price_close'] = round((float(channel_price[symb][i][k]) - float(price_last_alert_algo_1[i])) / float(price_last_alert_algo_1[i]) * 100, 2)
                    try:
                        df.loc[ind_time_close[0], 'close_cond'] = channel_cond[symb][i][k]
                    except: pass
                    MT_pnl = MT_pnl + [round((channel_price[symb][i][k] - channel_price[symb][i][k-1]) / channel_price[symb][i][k-1] * 100, 2)]

            MT_pnl_total = round(sum(MT_pnl),2)
            MT_pnl_clear = round(MT_pnl_total - len(MT_pnl)*0.16, 2)
            count_trades = count_trades + len(MT_pnl)
            df.loc[ind_2_line+2, 'pnl_description'] = MT_pnl_clear/2
            df['avg_vol'] = df['Volume']/df['Number of trades']
            index_vol = round(float(df.iloc[ind[0]]['Volume'] / statistics.mean(df['Volume'][ind[0]-5:ind[0]])), 2)
            

            df.loc[ind[0], 'signal'] = 0 


            ############################################# фичи антифрода - работают на абсолютной цене
            time_ser = df["Time"].copy()              ### для индикатора
            hi = df[df['Time'] < time_alert].High.tolist()          
            lo = df[df['Time'] < time_alert].Low.tolist()        
            pts, (tot_r, t33_r, sh_r, low_r, sh2_r, s2l) = realis_calc_2(hi=hi, lo=lo, alert_price=price_last_alert_algo_1[i])
            af_mark, af_comment = af_realis_detect_2((tot_r, t33_r, sh_r, low_r, sh2_r, s2l), LIMITS_SHL_2)
            sh2_r = sh2_r if sh2_r else ""
            g_string = f"Sh/Lng  {sh_r}  {low_r:+.1f}  {sh2_r} =>  {tot_r}  ({t33_r})"
            
            avg1, avg2, v2_v1 = vol_features_calc_2(df, time_alert)
            vol_mark, vol_comment = vol_marc_detect_2((avg1, avg2, v2_v1), LIMITS_VOL_2)
            v_string = f"Vol1/avg={avg1}, vol2/avg={avg2}, vol2/vol1={v2_v1}"
            
            first_time_trade = channel_time[symb][i][0] if len(channel_time[symb][i]) else 0
            features05_tpl = vol_05_calc_2(df, time_alert, first_time_trade)         ### добавил блок объёмов с 0.5
            v05_mark, v05_comment = vol_05_marc_detect_2(features05_tpl, LIMITS_V05_2)
            v05_string = "\n".join(map(lambda x: f"{x:.2f}", features05_tpl))
            if sum(features05_tpl[:7]) <= 0.008:
                v05_comment, v05_string = "нет 0.5", "нет 0.5"
            ind05 = int(features05_tpl[-1])
            ############################################# конец первой вставки - фичи антифрода


            df['Time'] = df['Time'] + 3 * 60 * 60 * 1000

            df['High'] = df['High'].astype(float)
            df['Low'] = df['Low'].astype(float)
            if len(df['Low']) == 0:
                bot.send_message(error_tg, f'ver 20 len(df["Low"]) == 0 in screen({symb}, {i})')  ### отладка - поиск min([])   -eg-
            if (max(df['High']) - min(df['Low'])) / min(df['Low']) * 100 < 5:
                df.loc[0, 'High'] = statistics.mean([max(df['High']), min(df['Low'])]) * 1.025
                df.loc[0, 'Low'] = statistics.mean([max(df['High']), min(df['Low'])]) * 0.975
                df.loc[0, 'Close'] = statistics.mean([max(df['High']), min(df['Low'])])
                df.loc[0, 'Open'] = statistics.mean([max(df['High']), min(df['Low'])])

            df['Time_for_sl'] = df['Time']
            df = df.set_index('Time')
            df.index = pd.to_datetime(df.index, unit = 'ms')
            cols = df.columns.to_list()
            cols.remove('open_cond')
            cols.remove('close_cond')
            df[cols] = df[cols].astype(float) 
            
            percent_high = round(((float(max(df['High'][ind[0]:ind_2_line])) - float(price_last_alert_algo_1[i]))/float(price_last_alert_algo_1[i])*100),2)
            if len(df['Low'][(ind[0]+1):ind_2_line]) == 0:
                bot.send_message(error_tg, f'ver 20 len(df["Low"][(ind[0]+1):ind_2_line]) == 0 in screen({symb}, {i})')  ### отладка - поиск min([])   -eg-                
            
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
            window = df_chanels['Time'] < time_alert_msk
            
            data_alert = df_chanels[window]
            data_after = df_chanels[~window]
            data_after = data_after.reset_index(drop = True)
            start_anomaly = data_alert[-2:-1].Low.values[0]
            start_anomaly_time = data_alert[-2:-1].Time.values[0]
            time_before_alert = [5, 10, 20]
            
            chanels_info = [calculate_chanel(data_alert, candles) for candles in time_before_alert]
            points = []
            widths = np.asarray([i[0] for i in chanels_info])
            widths_rounded = np.around(widths,2) # Ширины каналов
            
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
            #######################
            if len(channel_price[symb][i]) == 0:
                df['pnl_line'] = 0
            else:
                df['pnl_line'] = MT_pnl_clear

            
            apds = [mpf.make_addplot(df['signal'],type='scatter', color='#2d5ff5',markersize=50, secondary_y=False),
                    mpf.make_addplot(df['psar_high'],type='scatter', color='r',markersize=0.5, secondary_y=False),
                    mpf.make_addplot(df['psar_low'],type='scatter', color='g',markersize=0.5, secondary_y=False),
                    mpf.make_addplot(df['pnl_line'],type='scatter', color='purple', alpha = 0.6, markersize=0.1, secondary_y=False),
                    mpf.make_addplot(df['line_alert'],type='scatter', color='g',markersize=0.1, secondary_y=False),
                    mpf.make_addplot(df['price_close'], type='scatter', color='r',markersize=20, marker='v', secondary_y=False),
                    mpf.make_addplot(df['price_open'], type='scatter', color='g',markersize=20, marker='^', secondary_y=False)]
            
            cap = f'ver20 {description} {symb}\n{power_emoji}\nclear_pnl: {MT_pnl_clear}%\ntake_clear_potential: {round(MT_pnl_clear/percent_high*100,2)}%'
            
            title_mess = f'\n\n\nver20 {symb}, price: {price_last_alert_algo_1[i]}, time: {time_pump}\nmax={percent_high}%, min={percent_low}%, coef={count_plus_pnl}/{count_minus_pnl}, Ind_Vol= {index_vol}, {v_string}\ntotal_pnl: {MT_pnl_total}%, clear_pnl: {MT_pnl_clear}%, count_trades: {len(MT_pnl)}, comm+sq: {round(len(MT_pnl)*0.16, 2)}%, take_potential: {round(MT_pnl_total/percent_high*100,2)}%,take_clear_potential: {round(MT_pnl_clear/percent_high*100,2)}%,\npnl_trades: {MT_pnl}' #, PnL% = {percent_order}
            ### сохраняем последний трейд для отправки в wtp all
            trade_str = f'ver20: {MT_pnl_clear}% / {round(MT_pnl_clear/percent_high*100,2)}%'

############################# Вставка "Oтрисовка стоп-лоссов" - EG 
            osl_ser = pd.Series(None, index=df.index, dtype=float)
            ysl_ser = pd.Series(None, index=df.index, dtype=float)
            # строю фрагмент линии для каждого трейда
            for _, (t, p, cur_atr) in df[df.price_open > -100][["Time_for_sl", "price_open", "atr"]].iterrows():
                t2 = df[(df.Time_for_sl >= t) & (df.price_close > -100)].Time_for_sl.values[0]  # время закрытия трейда

                # добавляю вылет за пределы трейда на 3 свечи для удобства восприятия
                mask = (df.Time_for_sl >= t - 1 * 60000) & (df.Time_for_sl < t2 + 1 * 60000)
                osl_ser[mask] = p - 0.2 - PARAMS["down_osl"] * cur_atr
                mask = (df.Time_for_sl >= t + 20 * 60000) & (df.Time_for_sl < t2 + 1 * 60000)  # лесенка с 20-й минуты
                osl_ser[mask] = p - 0.2 - PARAMS["down_osl"] * cur_atr + PARAMS["step_osl"] * ((df.Time_for_sl - t) // (10 * 60 * 1000) - 1)
                osl_ser[osl_ser > df.High.max()] = None


                tmp_ser = df.High.copy()    # Чтобы не затереть
                tmp_ser[df.Time_for_sl <= t] = p   # Чтобы убрать максимуиы цены до входа в лонг
                mask = (df.Time_for_sl >= t - 1 * 60000) & (df.Time_for_sl <= t2 + 1 * 60000)  # +1 минута за пределами трейда
                ysl_ser[mask] = (tmp_ser - 0.2 - PARAMS["down_ysl"] * cur_atr).rolling(int((t2 - t) / 60000) + 2).max()
                ysl_ser[ysl_ser > df.High.max()] = None
                # = максимум цены от начала трейда минус 3*ATR

            # формирую доп.линии для графика mpf
            osl_apd = mpf.make_addplot(osl_ser, secondary_y=False, color="darkorange", linestyle="--", alpha=.5)
            ysl_apd = mpf.make_addplot(ysl_ser.shift(), secondary_y=False, color="y", alpha=.5)
            apds.extend([osl_apd, ysl_apd])
############################# Конец вставки "Oтрисовка стоп-лоссов" - EG 

            al = dict(alines=points, colors=colors_, linewidths=2, alpha=0.6)
            vl = dict(vlines=[df_line.iloc[0,1],df_line.iloc[1,1]],linewidths=(1,1))
            buf20 = io.BytesIO()

            ################# шорт-лонг реализация - косые линии ###############
            pts = list(map(lambda x: list(map(lambda y: (df.index[y[0]], y[1]), x)), pts))  # переводит координаты в timestamp
            ind05 = df.index[ind[0] + ind05]  ### Изменил блок косых линий - добавил указатель на 0.5%
            if len(pts) == 2:
                pts.append([(ind05, 0), (ind05, 0)])
            if len(df.Low) == 0:
                bot.send_message(error_tg, f"ver 20 len(df.Low) == 0 in screen, i={i}, symb={symb}")  ### отладка - поиск min([])   -eg-
            al2 = dict(alines=pts + [[(ind05, df.Low.min()), (ind05, df.loc[ind05, "Low"])]], colors=["darkred", "darkgreen", "darkred", "darkorange"], linewidths=[7] * 3 + [0.2], alpha=[0.15] * 3 + [0.5])        
            al = dict(alines = points + al2["alines"], colors = colors_[:len(points)] + al2["colors"], linewidths = [2] * len(points) + al2["linewidths"], alpha = [0.6] * len(points) + al2["alpha"])
            ################# Конец 2 вставки шорт-лонг реализация ###############      
   
            ################# Вставка индюк ###############
            w_scores_new = {'w30': {6: 0.613, 5: 0.910, 4: 1.225, 3: 1.500, 2: 2.173, 1: 2.546},
                            'w5' : {6: 0.215, 5: 0.307, 4: 0.419, 3: 0.500, 2: 0.600, 1: 0.894}}

            def w30_scoring(feature):
                for mrk in range(6, 0, -1):
                    if feature <= w_scores_new['w30'][mrk]:
                        return mrk
                return 0
                        
            def w5_scoring(feature):
                for mrk in range(6, 0, -1):
                    if feature <= w_scores_new['w5'][mrk]:
                        return mrk
                return 0
            
            df_chanels['w30'] = df_chanels[df_chanels['Time'] <= time_alert_msk -2*60*1000].High.rolling(window = 30).apply(chanel_widths, args=(df_chanels,))
            df_chanels['w5'] = df_chanels[(df_chanels['Time'] >= time_alert_msk - 60*60*1000)&(df_chanels['Time'] <= time_alert_msk -2*60*1000)].High.rolling(window = 5).apply(chanel_widths, args=(df_chanels,))
            
            w30_50a = df_chanels[(df_chanels.w30 > np.percentile(df_chanels.w30.dropna(),50)) & (df_chanels.w30 < np.percentile(df_chanels.w30.dropna(),99))].w30.mean()
            mean_5 = df_chanels.w5.mean()

            w30_score = w30_scoring(w30_50a)
            w5_score = w5_scoring(mean_5)
            
            total_score = (vol_mark * WEIGHTS_2["V"] + v05_mark * WEIGHTS_2["05"] + af_mark * WEIGHTS_2["R"] + w30_score * WEIGHTS_2["W"] + w5_score * WEIGHTS_2["w"])
        
            induk_ser = pd.Series(None, index=df.index, dtype=float)
            ind_limit_ser = pd.Series(WEIGHTS_2["Total"] - 6 * WEIGHTS_2["V"], index=df.index)
            
            ind_short_limit_ser = pd.Series(6, index=df.index)
            ind_05_ser = pd.Series(df.Low.min(), index=df.index)
            ind_05_ser[(df.index > ind05) | (df.index < df.index[ind[0]])] = None
            
            ind_shl_ser = pd.Series(None, index=df.index, dtype=float)            
            const_score = af_mark * WEIGHTS_2["R"] + w30_score * WEIGHTS_2["W"] + w5_score * WEIGHTS_2["w"]
            
            if ind05 >= df.index[ind[0]]:
                df["Time"] = time_ser.values                
                induk_ser[(df.index >= df.index[ind[0] - 1]) & (df.index < ind05)] = const_score + vol_mark * WEIGHTS_2["05"]
                for j in range(ind[0], ind[0] + 120):  #                      = 0
                    features05_tpl_cur = vol_05_calc_2(df, time_alert, df.loc[df.index[j], "Time"])  ### динамичные объёмы аля с 0.5
                    v05_current_mark, _ = vol_05_marc_detect_2(features05_tpl_cur, LIMITS_V05_2)                    
                    induk_ser[df.index[j]] = const_score + v05_current_mark * WEIGHTS_2["05"]

            ind_ampl = (df.High.max() - df.Low.min()) / max(induk_ser.max(), WEIGHTS_2["Total"]) / 5  # 5 - какую часть графика занять
            induk_ser = df.Low.min() + induk_ser * ind_ampl
            ind_limit_ser = df.Low.min() + ind_limit_ser * ind_ampl
            ind_short_limit_ser = df.Low.min() + ind_short_limit_ser * ind_ampl
                       
            ind_shl_ser[(df.index >= df.index[0]) & (df.index < df.index[20])] = (vol_mark - WEIGHTS_2["vol_lim"]) * 2
            ind_shl_ser[(df.index >= df.index[10]) & (df.index < df.index[20])] = (v05_mark - WEIGHTS_2["v05_lim"]) * 2
            ind_shl_ser[(df.index >= df.index[20]) & (df.index < df.index[30])] = (af_mark - WEIGHTS_2["real_lim"]) * 2
            ind_shl_ser[(df.index >= df.index[30]) & (df.index < df.index[40])] = (w30_score - WEIGHTS_2["w30_lim"]) * 2
            ind_shl_ser[(df.index >= df.index[40]) & (df.index < df.index[50])] = (w5_score - WEIGHTS_2["w5_lim"]) * 2
            ind_shl_ser[df.index < df.index[50]] = (ind_shl_ser[df.index < df.index[50]] + max(induk_ser.max(), WEIGHTS_2["Total"] - 6 * WEIGHTS_2["V"] + 2))
            ind_shl_ser = df.Low.min() + ind_shl_ser * ind_ampl

            apds.extend([mpf.make_addplot(induk_ser, secondary_y=False, color="b", linestyle="-", linewidths=0.03, alpha=0.7),
                         mpf.make_addplot(ind_limit_ser, secondary_y=False, color="b", linestyle="--", alpha=.3),
                         mpf.make_addplot(ind_short_limit_ser, secondary_y=False, color="b", linestyle="--", alpha=.3),
                         mpf.make_addplot(ind_05_ser, secondary_y=False, color="darkorange", linestyle="-", alpha=.3),
                         mpf.make_addplot(ind_shl_ser, secondary_y=False, color="r", linestyle="-", linewidths=3, alpha=.7),
                        ])
            ################# Конец вставки индюк ###############            

  
            df['where'] = (df['Close'] == df['Close'].iloc[ind_2_line + 2]) & (df['Open'] == df['Open'].iloc[ind_2_line + 2]).values
            if percent_high >= 12 or percent_low <= -12:
                title_mess = '\n\n\n' + title_mess + text
                fig, axlist = mpf.plot(df, type='candle', style='yahoo', volume=True, fill_between=dict(y1=0,y2=MT_pnl_clear,where=df['where'],alpha=0.6,color='purple'), alines=al, addplot=apds, vlines=vl, title=title_mess, panel_ratios=(4, 1), figratio=(30, 14), fontscale=0.6, returnfig=True, show_nontrading=True)
                df_op_cond = df.open_cond.dropna()
                for x,t in df_op_cond.items():
                    y = df.loc[x,'price_open']+0.5
                    axlist[0].text(x,y,t,fontstyle='italic')
                df_cl_cond = df.close_cond.dropna()
                for x,t in df_cl_cond.items():
                    y = df.loc[x,'price_close']+0.5
                    axlist[0].text(x,y,t,fontstyle='italic')

                df_pnl_description = df.pnl_description.dropna()
                for x,t in df_pnl_description.items():
                    y = df.loc[x,'pnl_description']
                    axlist[0].text(x,y,t,fontstyle='italic')
                    t = t * 2
                # fig.savefig(fname=buf20,dpi=100,pad_inches=0.25) 
                #fig , axlist = mpf.plot(df, type='candle', style='yahoo', volume=True, alines=al, addplot=apds, vlines=vl, title=title_mess, panel_ratios=(4,1), figratio=(30,14), fontscale=0.6, closefig=True, returnfig=True) #savefig=dict(fname=f'/projects/Ver3/mt_screen/screen{symb}.jpeg',dpi=100,pad_inches=0.25))
            else:
                fig, axlist = mpf.plot(df, type='candle', style='yahoo', volume=True,  fill_between=dict(y1=0,y2=MT_pnl_clear,where=df['where'],alpha=0.6,color='purple'), addplot=apds, vlines=vl, title=title_mess, fontscale=0.6, panel_ratios=(4, 1), figratio=(30, 14), returnfig=True, show_nontrading=True)
                df_op_cond = df.open_cond.dropna()
                for x,t in df_op_cond.items():
                    y = df.loc[x,'price_open']+percent_high/2*0.2
                    axlist[0].text(x,y,t,fontstyle='normal',fontsize='x-large')
                df_cl_cond = df.close_cond.dropna()
                for x,t in df_cl_cond.items():
                    y = df.loc[x,'price_close']+percent_high/2*0.2
                    axlist[0].text(x,y,t,fontstyle='normal',fontsize='x-large')
                
                df_pnl_description = df.pnl_description.dropna()
                for x,t in df_pnl_description.items():
                    y = df.loc[x,'pnl_description']
                    t = t * 2
                    axlist[0].text(x,y,t,fontstyle='italic',fontsize='x-large')


            ####################### шорт-лонг реализация + каналы + объёмы на графике       
            axlist[0].text(df.index[0], df.High.max() - (df.High.max() - df.Low.min()) * 0.1, g_string, fontstyle='normal', color="darkgreen", fontsize=9)
            axlist[0].text(df.index[0], df.High.max() - (df.High.max() - df.Low.min()) * 0.15, v05_string, fontstyle='normal', color="darkblue", fontsize=9, va="top")
            combo_formula_string = f'{WEIGHTS_2["vol_lim"]}{WEIGHTS_2["v05_lim"]}{WEIGHTS_2["real_lim"]}{WEIGHTS_2["w30_lim"]}{WEIGHTS_2["w5_lim"]}  {WEIGHTS_2["V"]} {WEIGHTS_2["05"]} {WEIGHTS_2["R"]} {WEIGHTS_2["W"]} {WEIGHTS_2["w"]}  ({WEIGHTS_2["Total"]} Б)'
            axlist[0].text(df.index[0], df.High.max(), combo_formula_string, fontstyle='normal', color="darkblue", fontsize=9)   ### текущее комбо

            ch30_comment = "channel 30 min " if w30_score < 6 else ""
            ch5_comment = "channel 5 min " if w5_score < 6 else ""
            iterator = zip((vol_mark, v05_mark, af_mark, w30_score, w5_score), (vol_comment, v05_comment, af_comment, ch30_comment, ch5_comment))
            text_in_box = "\n\n".join((f"{mrk}   {comm}" for mrk, comm in iterator))
            axlist[0].text(df.index[230], df.High.max() - 0.2, text_in_box, fontstyle='normal', color="b", fontsize=9, bbox=dict(boxstyle="square", fill=False, lw=0), va="top")

            text_in_box = (f'max={percent_high}%   v1=x{round(avg1, 1)}\npnl={MT_pnl_total:+.2f}({MT_pnl_clear:+.2f})%\nV{vol_mark} + v{v05_mark} + R{af_mark} + W{w30_score} + w{w5_score} = {total_score}')
            axlist[0].text(df.index[254], df.Low.min(), text_in_box, fontstyle='normal', color="b", fontsize=11, bbox=dict(boxstyle="round", ec="b", fill=False, ls="-", lw=.5, pad=0.2), ha="center")
            
            if (total_score > WEIGHTS_2["Total"] and vol_mark >= WEIGHTS_2["vol_lim"] and \
                v05_mark >= WEIGHTS_2["v05_lim"] and af_mark >= WEIGHTS_2["real_lim"] and \
                w30_score >= WEIGHTS_2["w30_lim"] and w5_score >= WEIGHTS_2["w5_lim"]):
                color, back_color, text_in_box = "g", "lime", "YYY"
            else:
                color, back_color, text_in_box = "darkred", "violet", "NNN"
            axlist[0].text(df.index[254], df.Low.min() + (df.High.max() - df.Low.min()) * 0.2, text_in_box, fontstyle='normal', color=color, fontsize=36, ha="center", bbox=dict(boxstyle="round", ec=color, fc=back_color, ls="-", lw=.5, pad=0.2, alpha=0.1))
            ################# Конец 3 вставки шорт-лонг реализация  и объёмы


            fig.savefig(fname=buf20,dpi=100,pad_inches=0.25)

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
                
                mpf.plot(df, type='candle', style='yahoo', volume=True, alines=al, addplot=apds, vlines=vl, title=title_mess, panel_ratios=(4,1), figratio=(30,14), fontscale=0.6, closefig=True, savefig=dict(fname=buf20,dpi=100,pad_inches=0.25))
                #fig , axlist = mpf.plot(df, type='candle', style='yahoo', volume=True, alines=al, addplot=apds, vlines=vl, title=title_mess, panel_ratios=(4,1), figratio=(30,14), fontscale=0.6, closefig=True, returnfig=True) #savefig=dict(fname=f'/projects/Ver3/mt_screen/screen{symb}.jpeg',dpi=100,pad_inches=0.25))
            else:
                mpf.plot(df, type='candle', style='yahoo', volume=True, addplot=apds, vlines=vl, title=title_mess, fontscale=0.6, panel_ratios=(4,1), figratio=(30,14), closefig=True, savefig=dict(fname=buf20,dpi=100,pad_inches=0.25))
                #fig , axlist = mpf.plot(df, type='candle', style='yahoo', volume=True, addplot=apds, vlines=vl, title=title_mess, fontscale=0.6, panel_ratios=(4,1), figratio=(30,14), closefig=True, returnfig=True) #savefig=dict(fname=f'/projects/Ver3/mt_screen/screen{symb}.jpeg',dpi=100,pad_inches=0.25))
            
            '''
            buf20.seek(0)
            try:
                id_photo = send_photo(chat_id=screen_tg, file=buf20, cap=cap)
            
                f_id = str(id_photo['result']['photo'][-1]['file_id'])
            except:
                bot.send_message(error_tg, f'v20 rusult\n{id_photo}')
                id_photo = send_photo(chat_id=screen_tg, file=buf20, cap=cap)
            
                f_id = str(id_photo['result']['photo'][-1]['file_id'])

            #id_photo = bot.send_photo(screen_tg, buf20, caption=cap)            
            #f_id = id_photo.photo[-1].file_id
            buf20.close()
            
            #bot.send_message(a1_v31,cap)
            #if percent_high >= 3:
                #bot.send_photo(wtp_screen_tg, open(f'/projects/Ver20/mt_screen/screen{symb}.jpeg','rb'), caption=cap)
                #bot.send_message(wtp_v31,cap)
            '''if len(MT_pnl) > 0:
                bot.send_photo(screen_v20, f_id, caption=cap)
            if MT_pnl_clear >= 8 and round(MT_pnl_clear/percent_high*100,2) <= 40:
                bot.send_photo(max_8_take_40_tg, f_id, caption=cap)
            
            if MT_pnl_clear >= 10:
                bot.send_photo(clear_pnl_10_tg, f_id, caption=cap)

            if round(MT_pnl_clear/percent_high*100,2) >= 80:
                bot.send_photo(take_clear_pnl_80_tg, f_id, caption=cap)
            '''
            channel_price[symb][i] = []
            channel_time[symb][i] = []
            
            print('end send screen')

            
            
            alerts_MT[symb][i] = 0
            
            return f_id, trade_str
            

        except Exception as e:
                #bot.send_message(screen_tg, f'fail screen {symb}')
                bot.send_message(error_tg, f'a1_v20 fail screen {symb} i={i}\n\n{e}')
                
                channel_price[symb][i] = []
                channel_time[symb][i] = []
                alerts_MT[symb][i] = 0
                return '', ''
                    
                




def get_formatted_time(timestamp):
        dt_object = datetime.datetime.fromtimestamp(timestamp / 1000.0)
        time_str = dt_object.strftime("%Y-%m-%d %H:%M:%S")
        return time_str
    
def get_formatted_day(timestamp):
    dt_object = datetime.datetime.fromtimestamp(timestamp / 1000.0)
    time_str = dt_object.strftime("%Y-%m-%d")
    return time_str