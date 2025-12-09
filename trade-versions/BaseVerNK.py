import pandas as pd
import numpy as np
import mplfinance as mpf
from matplotlib import pyplot as plt
import json
import requests
import telebot
import datetime
import statistics
import io
import time
# import copy


COIN_TO_REMOVE = ['XEMUSDT', 'CRVUSDT', 'EOSUSDT', 'NEOUSDT', 'TLMUSDT', 'FILUSDT', 'LUNA2USDT', 'ILVUSDT', 'TRXUSDT', 'ZRXUSDT']
CH_M = 9                          ### было = 10
TMFR = 210

a1_screen_tg = '-###'   
NK_all_scr_tg = '-###'  
TG_Bot_token = "###"   
bot = telebot.TeleBot(TG_Bot_token)

p_emoji = '❗️'
legendary_16 = '❗️❗️❗️❗️'
legendary_20 = '❗️❗️❗️❗️❗️'
legendary_30 = '🤯🤯🤯🤯🤯'
legendary_40 = '☠️☠️☠️☠️☠️'
legendary_60 = '🌋🗽🌋🗽'
legendary_100 = '🩻🤖🩻🤖🩻'


with open('/projects/data/low_acc.txt', 'r') as f:
    last = f.read()
    low_acc = json.loads(last)


symbols = []
for key in low_acc:
    symbols.append(key)


#-----------------------------------------------------------------------------------------------------------------------
# '''
# Словари внутри торговой версии verNK. Содержат информацию о наличии или отсутсвтии открытых сделок:
# channel_price[symbol] = [[], []] словарь с ценой входа и выхода из сделки:
# {'REEFUSDT':[[может быть пусто], ['цена входа в сделку','цена выхода из сделки']]}

# channel_time[symbol] = [[], []] словарь с временем входа и выхода из сделки:
# {'REEFUSDT':[['может быть пусто'],['метка открытия позиции', 'метка закрытия позиции']]}

# alerts_ver_NK[symbol] = [1, 1] словарь состояния в сделке/не в сделке. где:
# 1-не в сделке, 2-в лонговой сделке, 3-не ищем сделку, 6 - в шортовой сделке.
# {'REEFUSDT':[1,1]}

# channel_cond[symbol] = [[], []] - словарь с меткой ДС-а и условием по выходу из сделки. Где:
# {'REEFUSDT':[['всегда пустой'],['NKS','e']]})


# Словари в основном файле для вызова всех функций поиска и торговли, плюс отрисовки и изменения информации:
# time_last_alert_NK[symbol] = [0, 0]  время последнего алерта. Где:
#       0-нет алерта, 175034200000 - есть время, 3000000000000-был алерт, но не подтвердился по цене.          
# price_last_alert_NK[symbol] = [0, 0] цена последнего алерта. Где: 0-нет алерта, 1.836 - есть цена алерта
#       alerts_NK[symbol] = [0, 0] состояние активного алерта. 0-нет алерта,1-лонговый алерт,2-шортовый алерт.
# key_points_sequence_NK = [['loading0', [], []], [], []] - словарь накопляемых данных, очищается после окончания торговли. 
#       {'REEFUSDT':[['loading', ['240 значений close'], ['локал минимум']],['список желтых точек'],['список синих точек']]}
# time_next_NK - технический словарь для основной логики. 
#     ЕГ: хранит начало следующей минуты по конкретной монете чтоб по 10 раз за минуту не запускать код. 
#     Смещение в мс - искусственно раскидывает монеты, чтоб не все одномоментно обсчитывались
# '''
try:
    # Словарь с ценой входа или выхода.
    # Записываю во второй список по ключу из двух. Записываю цену по которой хочу войти в сделку и запишу цену выхода из сделки, какая она получится.
    # channel_price = dict({'REEFUSDT':[['всегда пустой'],['цена входа в сделку','цена выхода из сделки']]})
    with open('/projects/verNK/channel_price.txt', 'r') as f:
        last = f.read()
        channel_price = json.loads(last)

    # Словарь со временем входа или выхода. Первый всегда пустой. первый элемент это время алерта, второй сразу же или через 4 часа время закрытия.
    # channel_time = dict({'REEFUSDT':[['всегда пустой'],['метка открытия позиции', 'метка закрытия позиции']]})
    with open('/projects/verNK/channel_time.txt', 'r') as f:
        last = f.read()
        channel_time = json.loads(last)

    # Словарь состояния в сделке или не в сделке. Где [1,1] - не в сделке, [1,2] - в сделке. Хранит состояние трейда внутри алерта.
    # Нулевая позиция меня не интересует, я ее не меняю, всегда должна стоять 1. Статусом 3 я не пользуюсь.
    # Я должен изменить статус на 2, когда вошел в лонг позицию в трейд версии, 6 - когда вошел в шорт позицию в трейд версии.
    # Я должен присвоить статус 1, когда сделка завершена.
    # alerts_ver_NK = dict({'REEFUSDT':[1,1]})
    # 1 - не в сделке
    # 2 - в сделке лонговой
    # 3 - не ищем сделку (мне не нужен этот статус)
    # 6 - в шортовой сделке
    with open('/projects/verNK/alerts_ver_NK.txt', 'r') as f:
        last = f.read()
        alerts_ver_NK = json.loads(last)
except:
    channel_price = {symbol: [[], []] for symbol in symbols}
    channel_time = {symbol: [[], []] for symbol in symbols}
    alerts_ver_NK = {symbol: [1, 1] for symbol in symbols}

try:
    # Словарь с условием по сделке (по входу или по выходу). Где 'NKS' - метка Шорт, NKL - метка Лонг. 'e' - метка выхода по времени.
    # channel_cond = dict({'REEFUSDT':[['всегда пустой'],['NKS','e']]})    
    with open('/projects/verNK/channel_cond.txt', 'r') as f:
        last = f.read()
        channel_cond = json.loads(last)
except:
    channel_cond = {symbol: [[], []] for symbol in symbols}


symbols_old = []
for key in alerts_ver_NK:            
    symbols_old.append(key)

symbol_new = list(set(symbols) - set(symbols_old))
if len(symbol_new) != 0:
    for symbol in symbol_new:
        channel_price[symbol] = [[], []]
        channel_time[symbol] = [[], []] 
        alerts_ver_NK[symbol] = [1, 1] 
        channel_cond[symbol] = [[], []]

def send_photo(chat_id, file, cap):
        url = f'https://api.telegram.org/bot{TG_Bot_token}/sendPhoto'
        files = {'photo': file}
        data = {'chat_id': chat_id, "caption": cap}
        respoNKe = requests.post(url, files=files, data=data)
        json_respoNKe = respoNKe.json()
        return json_respoNKe

# name_col_a1 = ['symbol', 'time_open', 'time_close', 'open_price', 'close_price', 'pnl',
#                'predict_vol', 'predict_05_vol','long_short', 'w30_score', 'w5_score']
# try:
    
#     a1_data_verNK = pd.read_csv('/projects/verNK/a1_data_verNK.csv', delimiter=',')
#     if len(a1_data_verNK.columns) == 1:
#         a1_data_verNK = pd.read_csv('/projects/verNK/a1_data_verNK.csv', delimiter=';')
#     #print(a1_data)
# except:
#     a1_data_verNK = pd.DataFrame(columns=name_col_a1)

# def trade_stat(symb, i, long_short_real, volume_05_real, volume_real, widths_real): 
#     global a1_data_verNK
#     pnl = round((channel_price[symb][i][-1] - channel_price[symb][i][-2])/channel_price[symb][i][-2] * 100, 2)
#     a1_data_verNK.loc[len(a1_data_verNK.index)] = [symb, channel_time[symb][i][-2], channel_time[symb][i][-1], channel_price[symb][i][-2], channel_price[symb][i][-1], pnl,
#                                                 volume_real[symb][i],volume_05_real[symb][i],long_short_real[symb][i],widths_real[symb][i][0],widths_real[symb][i][1]]


def trade_version_NK(last_kline_close, symb, time_tick, price_last_alert_NK, time_last_alert_NK, key_points_sequence, alerts_NK):
    '''
    3-я функция конвейера Никиты поиска алертов и торговли.
    Функция является торговой версией. Принимает алерт (алерт Никиты). Через 10 минут решает входить ли в позицию,
    в зависимости от типа алерта. В течении торговой сессии проверяет условия стоп-лосс. Закрывает позицию через 4 часа.

    Функция вызывается в A1_base (2647строка) только при условии получения статуса long/short:
    ((key_points_sequence_NK[symb][0][0] == 'long') or (key_points_sequence_NK[symb][0][0] == 'short'))

    Функция принимает на вход каждую минуту:
    last_kline_close - текущая цена закрытия минутной свечи
    time_tick - время текущей свечи
    symb - имя валютной пары
    price_last_alert_NK - словарь с ценой последнего алерта
    time_last_alert_NK  - словарь с временем последнего алерта
    key_points_sequence - словарь который хранит ключевые точки для получения алерта:
                            0                               1                         2
    {'symb':[ [short,[240минут],[локал минимум] ], [желтые точки для лонга], [синие точки для шорта] ]}

    Глобальные константы:
    CH_M - check minutes (количество минут) через которое проверяем условие на вход в позицию после получения алерта
    TMFR - timeframe - тайм -фрейм который торгуем при условии что позиция находится в правильном тренде.

    Перезаписываем только в случае наличия сделки:
    channel_time: dict - словарь со временем входа и выхода из позиции. {'symb': [] , [время входа, время выхода]}
    channel_price:dict - cловарь с ценой входа и выхода из позиции.     {'symb': [] , [цена входа, цена выхода]}
    channel_cond: dict - словарь с условием по сделке. {'symb': [] , [NKS/NKL-метка ДС-а, метка условия по выходу]}
    alerts_ver_NK: dict - состояние в сделке не в сделке внутри версии. 1-не в сделке.2-лонг,6-шорт.{'symb':[1,1]}

    return:
    key_points_sequence[symb]
    time_last_alert_NK[symb]
    price_last_alert_NK[symb]
    '''
    global channel_price, channel_time, alerts_ver_NK, channel_cond

    try:
        # Я получил время алерта, цену алерта, надо через 10 минут решить согласно типу алерта (шорт или лонг)
        # Торговать его или нет

        # Если тип алерта шорт:                              # 1-й паттерн это шортовый паттерн
        if (alerts_NK[symb][1] == 2) or (key_points_sequence[symb][0][0] == 'short'):
            # print(".", end="")                  ### метка в лог, чтобы видеть как много шортовых пре-алёртов   -nk-
            # если полученная свеча является десятой после алерта, и цена полученной свечи меньше чем цена алерта':}
            # if 'время текущей новой свечи минус время алерта >= 10 минут (милисек)' and 'цена текущей меньше чем цена алерта':
            if ((alerts_ver_NK[symb][1] == 1) and (time_tick - time_last_alert_NK[symb][1] >= CH_M*60*1000)):     # Если вдруг в версию будет добавлено ещё другое условие на вход - это убрать в конец, чтоб двойтой if не заблочил всё    -nk-
                if (last_kline_close < price_last_alert_NK[symb][1]) and (last_kline_close >= price_last_alert_NK[symb][1]*0.965):          
                    print("-SHORT- ", end="")                       # Это открытие шорт позиции:
                    # rewrite(symb, last_kline_close, time_tick)    ### смещаем словари с предыдущей сделкой   -nk-
                    # В данном случае список с ценой, временем и метками пуст. По этому мы не добавляем на позицию, а приклеиваем.
                    channel_price[symb][1] = channel_price[symb][1] + [last_kline_close]
                    channel_time[symb][1] = channel_time[symb][1] + [time_tick]
                    alerts_ver_NK[symb][1] = 6                                 # указатель открытия шорт позиции
                    channel_cond[symb][1] = channel_cond[symb][1] + ['NKS']    # указатель DS-a, указатель типа сделки
                    bot.send_message(a1_screen_tg, f'verNK short opened. {symb} {str(get_formatted_time(time_tick + 3*60*60000))[5:-3]} {last_kline_close}')
                    time.sleep(1)
                else:              # Если 10+ свеча больше чем алерт, и мы не в позиции, то выходим отсюда.
                    print("- ", end="")                         ### метка в лог - отмены алёрта на 10 минуте   -nk-
                    alerts_NK[symb][1] = 0                      # алёрт НЕ торгуется и НЕ рисуется, обнуляю    -nk-
                    key_points_sequence[symb][0][0] = 'done'    # - нет алертаs
                    # 'мы должны вернуться в функцию key-points() и продолжить искать ключевые точки'
                    bot.send_message(a1_screen_tg, f'verNK short aborted. {symb} {get_formatted_time(time_tick + 3*60*60000)}')
                    time.sleep(1)

            # Выход по времени через 4 часа после начала торговли
            elif ((alerts_ver_NK[symb][1] == 6) and (time_tick - channel_time[symb][1][-1] >= TMFR*60*1000)):
                print("e", end="")                                       ###    метка в лог - выход по времени  -nk-
                channel_price[symb][1] = channel_price[symb][1] + [last_kline_close]
                channel_time[symb][1] = channel_time[symb][1] + [time_tick]
                alerts_ver_NK[symb][1] = 1                               # указатель, что мы не в сделке
                channel_cond[symb][1] = channel_cond[symb][1] + ['e']    # указатель выхода по времени
                bot.send_message(a1_screen_tg, f'verNK short closed "e". {symb} {str(get_formatted_time(time_tick + 3*60*60000))[5:-3]} {0.9984 - float(last_kline_close) / float(channel_price[symb][1][0]):.2%}')
                time.sleep(1)

                # Здесь - почистить словарь с ключевыми точками, чтобы заново начать с самой первой функции start_minimum()
                # Изменим статус на loading, очистим список первых 4 часов, локальный минимум, синие и желтые точки очистим.
                key_points_sequence[symb] = [['loading', [], [], time_tick], [], []]   # обнуляем всё за эти 4 часа, сохраняем время начала накопления
                # Обнулить словари с активным алертом нужно будет там, где мы запишем скрин, то есть уже не в этой функции

            # stop-loss 3%
            # Если текущая цена выше чем цена алёрта на 1% и более and шорт позиция открыта то выйдем из позиции   (было выше чем цена входа в позицию на 3% и более)
            elif ((alerts_ver_NK[symb][1] == 6) and (last_kline_close >= price_last_alert_NK[symb][1] * 1.012)):   ### -nk-
                print("sl ", end="")                  ###    метка в лог, выход по стоплоссу                   -nk-
                channel_price[symb][1] = channel_price[symb][1] + [last_kline_close]
                channel_time[symb][1] = channel_time[symb][1] + [time_tick]
                alerts_ver_NK[symb][1] = 1                                # указатель, что мы не в сделке
                channel_cond[symb][1] = channel_cond[symb][1] + ['sl']    # указатель выхода по времени

                # Здесь - почистить словарь с ключевыми точками, чтобы заново начать с самой первой функции start_minimum()
                # Изменим статус на loading, очистим список первых 4 часов, локальный минимум, синие и желтые точки очистим.
                key_points_sequence[symb] = [['loading', [], [], time_tick], [], []]   # обнуляем всё за эти 4 часа, сохраняем время начала накопления
                bot.send_message(a1_screen_tg, f'verNK short closed "sl". {symb} {str(get_formatted_time(time_tick + 3*60*60000))[5:-3]} {0.9984 - float(last_kline_close) / float(channel_price[symb][1][0]):.2%}')
                time.sleep(1)
                # Обнулить словари с активным алертом нужно будет там, где мы запишем скрин, то есть уже не в этой функции

            # take-profit 4.5%
            # Если текущая цена ниже, чем цена входа в позицию на 5% и более and шорт позиция открыта то выйдем из позиции
            elif ((alerts_ver_NK[symb][1] == 6) and (last_kline_close <= channel_price[symb][1][-1] * 0.955)):  ### -NK-
                print(" tp ", end="")  ###    метка в лог, выход по take профиту                 -NK-
                channel_price[symb][1] = channel_price[symb][1] + [last_kline_close]
                channel_time[symb][1] = channel_time[symb][1] + [time_tick]
                alerts_ver_NK[symb][1] = 1  # указатель, что мы не в сделке
                channel_cond[symb][1] = channel_cond[symb][1] + ['tp']  # указатель выхода по достигнутой прибыли

                # Здесь - почистить словарь с ключевыми точками, чтобы заново начать с самой первой функции start_minimum()
                # Изменим статус на loading, очистим список первых 4 часов, локальный минимум, синие и желтые точки очистим.
                key_points_sequence[symb] = [['loading', [], [], time_tick], [], []]   # обнуляем всё за эти 4 часа, сохраняем время начала накопления
                bot.send_message(a1_screen_tg, f'verNK short closed "tp". {symb} {str(get_formatted_time(time_tick + 3 * 60 * 60000))[5:-3]} {0.9984 - float(last_kline_close) / float(channel_price[symb][1][0]):.2%}')
                time.sleep(1)
                # Обнулить словари с активным алертом нужно будет там, где мы запишем скрин, то есть уже не в этой функции



            elif (alerts_ver_NK[symb][1] not in (1, 2, 3, 6)):
                # при ошибке в словаре alerts_ver_NK - обнуляемся и выходим  -nk-
                print(f"alerts_ver_NK[{symb}]=", alerts_ver_NK[symb], end="   ")
                alerts_NK[symb][1] = 0                                          # алёрт НЕ торгуется и НЕ рисуется, обнуляю    -nk-
                key_points_sequence[symb][0][0] = 'done'                        # - нет алерта
                alerts_ver_NK[symb][1] = 1
            else:       # Это случай когда у нас есть алерт шортовый, и это еще не 10 свеча и это не стоп лосс и это не 240 свеча, то есть мы не вышли по времени
                pass    # ЗНачит это либо до 10 свечи, когда нам пока не важно, либо это все свечи внутри 4 часовой позиции, мы их просто пропускаем.
            return key_points_sequence[symb][0][0], alerts_NK[symb]   ### чтоб не попасть на if "всё проспали"  -nk-

        # 2-й паттерн лонговой модели

        if (alerts_NK[symb][1] == 1) or (key_points_sequence[symb][0][0] == 'long'):
            # print("'", end="")         ###    метка в лог, чтобы видеть как много лонговых пре-алёртов         -nk-
            # если полученная свеча является десятой после алерта, and цена через 10 минут превышает цену алерта не более чем на 2.8%:
            # if 'через 10 минут цена больше чем цена алерта' and 'цена через 10 минут превышает цену алерта не более чем на 2.8%':
            if ((alerts_ver_NK[symb][1] == 1) and (time_tick - time_last_alert_NK[symb][1] >= CH_M*60*1000)):         # Если вдруг в версию будет добавлено ещё другое условие на вход - это убрать в конец, чтоб двойтой if не заблочил всё    -nk-
                if ((price_last_alert_NK[symb][1] < last_kline_close) and (last_kline_close <= price_last_alert_NK[symb][1]*1.028)):                
                    print("+LONG+ ", end="")                                   # Это открытие лонг позиции:
                    # rewrite(symb, last_kline_close, time_tick)
                    channel_price[symb][1] = channel_price[symb][1] + [last_kline_close]
                    channel_time[symb][1] = channel_time[symb][1] + [time_tick]
                    alerts_ver_NK[symb][1] = 2                                 # указатель открытия лонг позиции
                    channel_cond[symb][1] = channel_cond[symb][1] + ['NKL']    # указатель DS-a, указатель типа сделки.
                    bot.send_message(a1_screen_tg, f'verNK long opened. {symb} {str(get_formatted_time(time_tick + 3*60*60000))[5:-3]} {last_kline_close}')
                    time.sleep(1)
                    return key_points_sequence[symb][0][0], alerts_NK[symb]
                    # return key_points_sequence[symb], time_last_alert_NK[symb], price_last_alert_NK[symb]
                else:              # Если 10+ свеча больше чем алерт, и мы не в позиции, то выходим отсюда.
                    print("- ", end="")                                        ### метка в лог - отмена алёрта на 10 минуте   -nk-
                    alerts_NK[symb][1] = 0                                     # алёрт НЕ торгуется и НЕ рисуется, обнуляю    -nk-
                    key_points_sequence[symb][0][0] = 'done'                   # - нет алерта
                    # 'мы должны вернуться в функцию key-points() и продолжить искать ключевые точки'
                    bot.send_message(a1_screen_tg, f'verNK long aborted. {symb} {get_formatted_time(time_tick + 3*60*60000)}')
                    time.sleep(1)

            # Выход по времени через 4 часа после начала торговли
            elif ((alerts_ver_NK[symb][1] == 2) and (time_tick - channel_time[symb][1][-1] >= TMFR*60*1000)):
                print("e ", end="")
                channel_price[symb][1] = channel_price[symb][1] + [last_kline_close]
                channel_time[symb][1] = channel_time[symb][1] + [time_tick]
                alerts_ver_NK[symb][1] = 1                                     # указатель, что мы не в сделке
                channel_cond[symb][1] = channel_cond[symb][1] + ['e']          # указатель выхода по времени
                bot.send_message(a1_screen_tg, f'verNK long closed "e". {symb} {str(get_formatted_time(time_tick + 3*60*60000))[5:-3]} {float(last_kline_close) / float(channel_price[symb][1][0]) - 1.0016:.2%}')
                time.sleep(1)

                # Здесь я должен почистить свой словарь с ключевыми точками, чтобы заново начать с самой первой функции start_minimum()
                # Изменим статус на loading, очистим список первых 4 часов, локальный минимум, синие и желтые точки очистим.
                key_points_sequence[symb] = [['loading', [], [], time_tick], [], []]   # обнуляем всё за эти 4 часа, сохраняем время начала накопления
                # Обнулить словари с активным алертом нужно будет там, где мы запишем скрин, то есть уже не в этой функции

            # stop-loss 3%
            # Если текущая цена ниже чем цена алёрта на 1% и более and лонг позиция открыта, то выйдем из позиции  (было ниже чем цена входа в позицию на 3% и более)
            elif ((alerts_ver_NK[symb][1] == 2) and (last_kline_close <= price_last_alert_NK[symb][1] * 0.988)):   ### -nk-
                print("sl ", end="")
                channel_price[symb][1] = channel_price[symb][1] + [last_kline_close]
                channel_time[symb][1] = channel_time[symb][1] + [time_tick]
                alerts_ver_NK[symb][1] = 1                                     # указатель, что мы не в сделке
                channel_cond[symb][1] = channel_cond[symb][1] + ['sl']         # указатель выхода по времени
                bot.send_message(a1_screen_tg, f'verNK long closed "sl". {symb} {str(get_formatted_time(time_tick + 3*60*60000))[5:-3]} {float(last_kline_close) / float(channel_price[symb][1][0]) - 1.0016:.1%}')
                time.sleep(1)
                
                # Здесь - почистить словарь с ключевыми точками, чтобы заново начать с самой первой функции start_minimum()
                # Изменим статус на loading, очистим список первых 4 часов, локальный минимум, синие и желтые точки очистим.
                key_points_sequence[symb] = [['loading', [], [], time_tick], [], []]   # обнуляем всё за эти 4 часа, сохраняем время начала накопления
                # Обнулить словари с активным алертом нужно будет там, где мы запишем скрин, то есть уже не в этой функции

            # take-profit 10%
            # Если в лонге цена поднялась выше чем 10% от цены входа в сделку - то можно выходить.
            # Если текущая цена выше, чем цена входа в позицию на 10% и более and лонг позиция открыта, то выйдем из позиции
            elif ((alerts_ver_NK[symb][1] == 2) and (last_kline_close >= channel_price[symb][1][-1] * 1.05)):  ### NK
                print("tp ", end="")
                channel_price[symb][1] = channel_price[symb][1] + [last_kline_close]
                channel_time[symb][1] = channel_time[symb][1] + [time_tick]
                alerts_ver_NK[symb][1] = 1  # указатель, что мы не в сделке
                channel_cond[symb][1] = channel_cond[symb][1] + ['tp']  # указатель выхода по stop profit
                bot.send_message(a1_screen_tg, f'verNK long closed "tp". {symb} {str(get_formatted_time(time_tick + 3 * 60 * 60000))[5:-3]} {float(last_kline_close) / float(channel_price[symb][1][0]) - 1.0016:.1%}')
                time.sleep(1)

                # Здесь - почистить словарь с ключевыми точками, чтобы заново начать с самой первой функции start_minimum()
                # Изменим статус на loading, очистим список первых 4 часов, локальный минимум, синие и желтые точки очистим.
                key_points_sequence[symb] = [['loading', [], [], time_tick], [], []]   # обнуляем всё за эти 4 часа, сохраняем время начала накопления

            elif (alerts_ver_NK[symb][1] not in (1, 2, 3, 6)):
                # при ошибке в словаре alerts_ver_NK - обнуляемся и выходим  -nk-
                print(f"alerts_ver_NK[{symb}]=", alerts_ver_NK[symb], end="   ")
                alerts_NK[symb][1] = 0                                          # алёрт НЕ торгуется и НЕ рисуется, обнуляю    -nk-
                key_points_sequence[symb][0][0] = 'done'                        # - нет алерта
                alerts_ver_NK[symb][1] = 1
            else:       # Это случай когда у нас есть алерт лонговый, и это еще не 10 свеча и это не стоп лосс и это не 240 свеча, то есть мы не вышли по времени
                pass    # Значит это либо до 10 свечи, когда нам пока не важно, либо это все свечи внутри 4 часовой позиции, мы их просто пропускаем.
            return key_points_sequence[symb][0][0], alerts_NK[symb]                 ### чтоб не попасть на if "всё проспали"       -nk-

        if (((alerts_ver_NK[symb][1] == 1) and (time_tick - time_last_alert_NK[symb][1] >= (CH_M+5)*60*1000)) or 
            (time_last_alert_NK[symb][1] == 3000000000000) or (alerts_ver_NK[symb][1] not in (1, 2, 3, 6))):
                # "всё проспали" - сюда не должны попадать, но если неверно загрузились словари или по другой причине мы здесь - обнуляемся и выходим  -nk-
                print("-проспали- ", end="")
                alerts_NK[symb][1] = 0                                          # алёрт НЕ торгуется и НЕ рисуется, обнуляю    -nk-
                key_points_sequence[symb][0][0] = 'done'                        # - нет алерта
                alerts_ver_NK[symb][1] = 1
                # 'мы должны вернуться в функцию key-points() и продолжить искать ключевые точки'
                bot.send_message(a1_screen_tg, f'verNK aborted >=15 min. {symb} {get_formatted_time(time_tick + 3*60*60000)}')
                time.sleep(1)
        return key_points_sequence[symb][0][0], alerts_NK[symb]
    except Exception as e:
        bot.send_message(a1_screen_tg, f'verNK ({symb}) trade_version_NK failed\n{e}\n')
        time.sleep(1)
        return key_points_sequence[symb][0][0], alerts_NK[symb]


def rewrite(symb, price, time):
    try:
        if symb not in channel_price:
            channel_price[symb] = [[], []]
        if symb not in channel_time:
            channel_time[symb] = [[], []] 
        if symb not in alerts_ver_NK:
            alerts_ver_NK[symb] = [1, 1]

        channel_price[symb][0] = channel_price[symb][1]
        channel_time[symb][0] = channel_time[symb][1]
        channel_price[symb][1] = []
        channel_time[symb][1] = []

        alerts_ver_NK[symb][0] = alerts_ver_NK[symb][1]
        alerts_ver_NK[symb][1] = 1

        channel_cond[symb][0] = channel_cond[symb][1]
        channel_cond[symb][1] = []
    except Exception as e:
        bot.send_message(a1_screen_tg, f'verNK rewrite fail\n\n{e}')
        time.sleep(1)


def save():
    try:
        with open('/projects/verNK/channel_price.txt', 'w') as file:
            file.write(json.dumps(channel_price))
        
        with open('/projects/verNK/channel_time.txt', 'w') as file:
            file.write(json.dumps(channel_time))

        with open('/projects/verNK/alerts_ver_NK.txt', 'w') as file:
            file.write(json.dumps(alerts_ver_NK)) 

        with open('/projects/verNK/channel_cond.txt', 'w') as file:
            file.write(json.dumps(channel_cond))   

        # a1_data_verNK.to_csv('/projects/verNK/a1_data_verNK.csv', index=False) 

    except Exception as e:
        bot.send_message(a1_screen_tg, f'verNK save fail\n\n{e}')
        time.sleep(1)


def screen(symb, i, df, time_last_alert, price_last_alert, df_btc, alert_type):
        try:
            global channel_cond, channel_price, channel_time
            global p_emoji, legendary_16, legendary_20, legendary_30, legendary_40, legendary_60, legendary_100
            try:
                print('start send screen verNK', symb, end="\t") 

                if len(channel_price[symb][i]) == 0:
                    bot.send_message(a1_screen_tg, f'verNK screen empty {symb} i={i}, {get_formatted_time(time_last_alert[i])}, p={price_last_alert[i]}')
                    time.sleep(1)
                    return  0, 0, 0, 0.000001, 0, 0, 0
            
                time_last_alert_scr = time_last_alert[i]             ### сохраняю локально содержимое глобальных словарей
                price_last_alert_scr = price_last_alert[i]           ### на случай смещения при параллельном асинхронном 
                channel_cond_scr = channel_cond[symb][i].copy()  ### получении другого алёрта / входа в сделку  -nk-
                channel_price_scr = channel_price[symb][i].copy()
                channel_time_scr = channel_time[symb][i].copy()

                channel_price[symb][i] = []                          ### сразу очищаю глобальные словари
                channel_time[symb][i] = []                           ### на случай смещения при параллельном асинхронном 
                channel_cond[symb][i] = []                           ### получении другого алёрта / входа в сделку
                alerts_ver_NK[symb][i] = 1                           ### чтоб не затереть другой алёрт              -nk-

                time.sleep(0.01)
                bot.send_message(a1_screen_tg, f'start send screen verNK {symb}, alert_type={alert_type}, time_last_alert_NK[{i}]={time_last_alert_scr} \t')
                df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume']
                time_alert = int(time_last_alert_scr - (time_last_alert_scr % 60000))

                df['Time_alert'] = time_alert
                df['Price_alert'] = price_last_alert_scr
                ###############
                df['Close'] = df['Close'].astype(float)
                df['High'] = df['High'].astype(float)
                df['Low'] = df['Low'].astype(float)
                df['Open'] = df['Open'].astype(float)
                df['Time'] = df['Time'].astype(np.int64)
                df['Number of trades'] = df['Number of trades'].astype(int)
                df['Volume'] = df['Volume'].astype(float)
                df['Taker buy base asset volume'] = df['Taker buy base asset volume'].astype(float)

            except Exception as e:
                bot.send_message(a1_screen_tg, f'verNK  screen failed-1 {symb} i={i}\n\n{e}')
                time.sleep(1)
            try:    
                df['signal'] = None
                df['line_alert'] = 0
                df['price_open'] = None
                df['price_close'] = None
                df['open_cond'] = None
                df['close_cond'] = None 
                df['pnl_description'] = None 

                ind = df[df['Time'] >= time_alert].index.values.astype(int)[:1]
                # ind_1_line = ind[0] - 15
                ind_2_line = ind[0] + 250 + 1
                
                line_1 = time_alert - 10 * 60 * 1000 + 3 * 60 * 60 * 1000
                line_2 = time_alert + 250 * 60 * 1000 + 3 * 60 * 60 * 1000
                df_line = pd.DataFrame({'Data': [line_1, line_2]})
                df_line['Data_line'] = pd.to_datetime(df_line['Data'], unit = 'ms')

                if len(channel_time_scr) % 2 == 1:
                    channel_time_scr = channel_time_scr + [int(time_alert + 299 * 60 * 1000)]
                    channel_price_scr = channel_price_scr + [float(df.iloc[ind[0] + 299]['Close'])]
                    channel_cond_scr = channel_cond_scr + ['e']

                NK_pnl = []
                for k in range(len(channel_time_scr)):
                    if k % 2 == 0:
                        time_open = int(channel_time_scr[k] - (channel_time_scr[k] % 60000))
                        ind_time_open = df[df['Time'] == time_open].index.values.astype(int)
                        df.loc[ind_time_open[0], 'price_open'] = round((float(channel_price_scr[k]) - float(price_last_alert_scr)) / float(price_last_alert_scr) * 100, 2)
                        try:
                            df.loc[ind_time_open[0], 'open_cond'] = channel_cond_scr[k]
                        except: pass

                    if k % 2 == 1:
                        time_close = int(channel_time_scr[k] - (channel_time_scr[k] % 60000))
                        ind_time_close = df[df['Time'] == time_close].index.values.astype(int)
                        df.loc[ind_time_close[0], 'price_close'] = round((float(channel_price_scr[k]) - float(price_last_alert_scr)) / float(price_last_alert_scr) * 100, 2)
                        try:
                            df.loc[ind_time_close[0], 'close_cond'] = channel_cond_scr[k]
                        except: pass
                        if alert_type in (1, 'long', 'loading2'):              ### оставить только 1   -nk-
                            NK_pnl = NK_pnl + [round((channel_price_scr[k] - channel_price_scr[k-1]) / channel_price_scr[k-1] * 100, 2)]
                        elif alert_type in (2, 'short', 'loading6'):           ### оставить только 2   -nk-
                            NK_pnl = NK_pnl + [-round((channel_price_scr[k] - channel_price_scr[k-1]) / channel_price_scr[k-1] * 100, 2)]
                        else:    
                            NK_pnl = NK_pnl + [0.16]

                NK_pnl_total = round(sum(NK_pnl), 2)
                NK_pnl_clear = round(NK_pnl_total - len(NK_pnl) * 0.16, 2)     ### комисс + сквиз
                df.loc[ind_2_line + 2, 'pnl_description'] = NK_pnl_clear / 2
                # df['avg_vol'] = df['Volume'] / df['Number of trades']
                index_vol = round(float(df.iloc[ind[0]]['Volume'] / df['Volume'][ind[0]-5: ind[0]].mean()), 2)
                
                # df['typ_price'] = ((df.High + df.Close + df.Low) / 3 ) * df.Volume
                df.loc[ind[0], 'signal'] = 0 

            except Exception as e:
                bot.send_message(a1_screen_tg, f'verNK  screen failed-2 {symb} i={i}\n\n{e}')
                time.sleep(1)
            try:                
                df['Time'] = df['Time'] + 3 * 60 * 60 * 1000
                # df = df.merge(df_vol, on='Time', how='left')
                df = df.merge(df_btc, on='Time', how='left')
                df = df.where(pd.notnull(df), None)
                df['Close_btc'] = df['Close_btc'].astype(float)
                df['High'] = df['High'].astype(float)
                df['Low'] = df['Low'].astype(float)

            except Exception as e:
                bot.send_message(a1_screen_tg, f'verNK  screen failed-3 {symb} i={i}\n\n{e}')
                time.sleep(1)
            try:                
                if len(df['Low']) == 0:
                    bot.send_message(a1_screen_tg, f"verNK len(df['Low']) == 0 in screen, i={i}, symb={symb}")  ### отладка - поиск min([])   -nk-
                    time.sleep(1)

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
                df[cols] = df[cols].astype(float)
                
                percent_high = round(((float(max(df['High'][ind[0]:ind_2_line])) - float(price_last_alert_scr))/float(price_last_alert_scr)*100),2)
                
                if len(df['Low'][(ind[0]+1):ind_2_line]) == 0:
                    bot.send_message(a1_screen_tg, f"verNK bag min([]): len(df['Low'][(ind[0]+1):ind_2_line]) == 0 in screen, i={i}, symb={symb}")  ### отладка - поиск min([])   -nk-
                    time.sleep(1)

                percent_low = round(((float(min(df['Low'][(ind[0]+1):ind_2_line])) - float(price_last_alert_scr))/float(price_last_alert_scr)*100),2)
                
                if percent_low >= 0:
                    percent_low = -0.000001                ###  исправвил -nk-
                if percent_high <= 0:
                    percent_high = 0.000001                ###  исправвил -nk-
                df['count'] = df['Close'] 
                df['count'] = df['count'].apply(lambda x: 1 if x >= float(price_last_alert_scr) else 0)
                
                count_plus_pnl = int(sum(df['count'][ind[0]:ind_2_line]) / len(df[ind[0]:ind_2_line]) * 100)
                count_minus_pnl = 100 - count_plus_pnl
                
                time_pump = get_formatted_time(int(time_last_alert_scr + 3 * 60 * 60 * 1000))

            except Exception as e:
                bot.send_message(a1_screen_tg, f'verNK  screen failed-4 {symb} i={i}\n\n{e}')
                time.sleep(1)
            try:
                сap_name_1h = ['P!!!!!+', 'P!!!!!', 'P!!!!', 'P!!!', 'P!!', 'P!', 'P', 'N', 'D', 'D!', 'D!!', 'D!!!', 'D!!!!', 'D!!!!!', 'D!!!!!+'] 
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

                df['Close'] = round((df['Close'] - float(price_last_alert_scr)) / float(price_last_alert_scr) * 100, 2)
                df['Open'] = round((df['Open'] - float(price_last_alert_scr)) / float(price_last_alert_scr) * 100, 2)
                df['High'] = round((df['High'] - float(price_last_alert_scr)) / float(price_last_alert_scr) * 100, 2)
                df['Low'] = round((df['Low'] - float(price_last_alert_scr)) / float(price_last_alert_scr) * 100, 2)
                btc_zero_price = df.iloc[ind[0]]['Close_btc']
                delta = df.iloc[0]['Close']
                df['Close_btc'] = round((df['Close_btc'] - float(btc_zero_price)) / float(btc_zero_price) * 100, 2) + delta

                if len(df['Close'][:ind[0]]) == 0:
                    bot.send_message(a1_screen_tg, f"verNK len(df['Close'][:ind[0]]) == 0 in screen, i={i}, symb={symb}")  ### отладка - поиск min([])   -nk-
                    time.sleep(1)
                    return 0, 0, 0, 0.000001, 0, 0, 0

            except Exception as e:
                bot.send_message(a1_screen_tg, f'verNK  screen failed-5 {symb} i={i}\n\n{e}')
                time.sleep(1)
            try:
                # if len(channel_price_scr) == 0:
                #     df['pnl_line'] = 0
                # else:
                #     df['pnl_line'] = NK_pnl_clear
                
                apds = [mpf.make_addplot(df['signal'],type='scatter', color='#2d5ff5',markersize=50, secondary_y=False),
                        # mpf.make_addplot(df['pnl_line'],type='scatter', color='purple', alpha = 0.6, markersize=0.1, secondary_y=False),
                        mpf.make_addplot(df['line_alert'],type='scatter', color='g',markersize=0.1, secondary_y=False),
                        mpf.make_addplot(df['price_close'], type='scatter', color='r',markersize=20, marker='v', secondary_y=False),
                        mpf.make_addplot(df['price_open'], type='scatter', color='g',markersize=20, marker='^', secondary_y=False),
                        mpf.make_addplot(df['Close_btc'], color='y', alpha = 0.3, secondary_y=False),
                        ]
            except Exception as e:
                bot.send_message(a1_screen_tg, f'verNK  screen failed-6 {symb} i={i}\n\n{e}')
                time.sleep(1)
            try:
                cap = f'verNK {"LONG" if alert_type != 2 else "SHORT"} {description} {symb}\n{power_emoji}\nclear_pnl: {NK_pnl_clear}%\ntake_clear_potential: {round(NK_pnl_clear/(percent_high if alert_type != 2 else -percent_low)*100, 2)}%'
                
                title_mess = f'\n\n\nverNK {"LONG" if alert_type != 2 else "SHORT"} {symb}, price: {price_last_alert_scr}, time: {time_pump}\nmax={percent_high}%, min={percent_low}%, coef={count_plus_pnl}/{count_minus_pnl}, Ind_Vol= {index_vol}\ntotal_pnl: {NK_pnl_total}%, clear_pnl: {NK_pnl_clear}%, count_trades: {len(NK_pnl)}, comm+sq: {round(len(NK_pnl) * 0.16, 2)}%, take_potential: {round(NK_pnl_total/percent_high*100,2)}%,take_clear_potential: {round(NK_pnl_clear/(percent_high if alert_type != 2 else -percent_low)*100,2)}%,\npnl_trades: {NK_pnl}' 

                ### сохраняем последний трейд для отправки в wtp all
                # trade_str = f'verNK: {NK_pnl_clear}% / {round(NK_pnl_clear/percent_high*100,2)}%'
                
                vl = dict(vlines=[df_line.iloc[0,1],df_line.iloc[1,1]], linewidths=(1,1), 
                          colors="darkred" if alert_type == 2 else "blue")
                buf6 = io.BytesIO()

                # df['where'] = (df['Close'] == df['Close'].iloc[ind_2_line + 2]) & (df['Open'] == df['Open'].iloc[ind_2_line + 2]).values
            except Exception as e:
                title_mess = ''
                bot.send_message(a1_screen_tg, f'verNK  screen failed-7 {symb} i={i}\n\n{e}')
                time.sleep(1)
            try:
                fig, axlist = mpf.plot(df, type='candle', style='yahoo', volume=True, addplot=apds, vlines=vl,
                                       title=title_mess, fontscale=0.6, panel_ratios=(4,1), figratio=(30,14), 
                                       returnfig=True, show_nontrading=True)
                axlist[0].set_xticks(np.arange((min(df.index.to_list()) + datetime.timedelta(1/24/4)).round('30 min'), max(df.index.to_list()), 1800000000))
                axlist[0].set_ylim(-20, 15)
                # axlist[0].text(df.index[0], df.High.max() * 0.9 + df.Low.min() * 0.1, "LONG" if alert_type == 1 else "SHORT",
                axlist[0].text(df.index[0], 10, "LONG" if alert_type == 1 else "SHORT",
                               color= "lime" if alert_type == 1 else "magenta", fontstyle='normal', fontsize=24)                    
                df_op_cond = df.open_cond.dropna()
                for x,t in df_op_cond.items():
                    y = df.loc[x,'price_open']+percent_high/2*0.2
                    axlist[0].text(x,y,t,fontstyle='normal', fontsize='x-large')
                df_cl_cond = df.close_cond.dropna()
                for x,t in df_cl_cond.items():
                    y = df.loc[x,'price_close']+percent_high/2*0.2
                    axlist[0].text(x,y,t,fontstyle='normal', fontsize='x-large')
                df_pnl_description = df.pnl_description.dropna()
                for x,t in df_pnl_description.items():
                    y = df.loc[x,'pnl_description']
                    t = t * 2
                    axlist[0].text(x,y,t,fontstyle='italic', fontsize='x-large')
            except Exception as e:
                bot.send_message(a1_screen_tg, f"verNK  screen failed-8 {symb} i={i}\n\n{e}\n\nI'll try 1 more time")
                time.sleep(1)
                try:
                    fig, axlist = mpf.plot(df, type='candle', style='yahoo', volume=True, addplot=apds, vlines=vl, 
                                           title=title_mess, fontscale=0.6, panel_ratios=(4,1), figratio=(30,14), 
                                           returnfig=True, show_nontrading=True)
                    axlist[0].set_xticks(np.arange((min(df.index.to_list()) + datetime.timedelta(1/24/4)).round('30 min'), max(df.index.to_list()), 1800000000))
                    axlist[0].set_ylim(-20, 15)
                    axlist[0].text(df.index[0], df.High.max() * 0.9 + df.Low.min() * 0.1, "LONG" if alert_type == 1 else "SHORT",
                                    color= "lime" if alert_type == 1 else "magenta", fontstyle='normal', fontsize=36)                       
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
                except Exception as e:
                    bot.send_message(a1_screen_tg, f'verNK  screen failed-8 & lost (2 attempt) {symb} i={i}\n\n{e}')
                    time.sleep(1)
                    return 0, 0, 0, 0.000001, 0, 0, 0
            try:
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
                f_id = 0
            # except Exception as e:
            #     bot.send_message(a1_screen_tg, f'verNK  screen failed-8.1 {symb} i={i}\n\n{e}')
            # try:
                buf6.seek(0)
                # f_id = send_photo(chat_id=a1_screen_tg, file=buf6, cap=cap)
                f_id = send_photo(chat_id=NK_all_scr_tg, file=buf6, cap=cap)
                print(f"verNK  screen f_id = {f_id}")
            # except Exception as e:
            #     bot.send_message(a1_screen_tg, f'verNK  screen failed-8.2 {symb} i={i}\n\n{e}')
            # try:                
                # f_id = f_id
            # except Exception as e:
            #     bot.send_message(a1_screen_tg, f'verNK  screen failed-8.4 {symb} i={i}\n\n{e}')
            # try:                
                # print("f_id=", f_id)
                try:
                    f_id = str(f_id['result']['message_id'])
                except Exception as e:
                    print("\nverNK  screen f_id =", f_id, "\n", e)
                    bot.send_message(a1_screen_tg, f'verNK  screen f_id = {f_id}')
                    time.sleep(1)
                #f_id = bot.send_photo(screen_tg, buf6, caption=cap)            
                #f_id = f_id.photo[-1].file_id
                buf6.close()
                # bot.send_photo(a1_screen_tg, f_id, caption=cap)
                #bot.send_message(a1_v31,cap)
                #if percent_high >= 3:
                    #bot.send_photo(wtp_screen_tg, open(f'/projects/verNK/mt_screen/screen{symb}.jpeg','rb'), caption=cap)
                    #bot.send_message(wtp_v31,cap)
            except Exception as e:
                bot.send_message(a1_screen_tg, f'verNK  screen failed-9 {symb} i={i}\n\n{e}')
                time.sleep(1)
            try:
                if len(channel_time_scr) == 0:
                    return_first_time_trade = 0
                else:
                    return_first_time_trade = channel_time_scr[0]

                print('end send screen NK')            

                # check_ztpk = 0
                # if len(channel_cond[symb][i]) != 0 and 'ztpk' in channel_cond[symb][i]:
                #     check_ztpk = 1

                alert_type = "long" if alert_type == 1 else "short" if alert_type == 2 else 0
                return (percent_high, description, f_id, NK_pnl_clear, percent_low, return_first_time_trade, alert_type)
                    
            except Exception as e:
                bot.send_message(a1_screen_tg, f'verNK  screen failed-10 {symb} i={i}\n\n{e}')
                time.sleep(1)
                return  0, 0, 0, 0.000001, 0, 0, 0

        except Exception as e:
                bot.send_message(a1_screen_tg, f'verNK fail screen {symb} i={i}\n\n{e}')
                time.sleep(1)
                return  0, 0, 0, 0.000001, 0, 0, 0
                      

def get_formatted_time(timestamp):
        dt_object = datetime.datetime.fromtimestamp(timestamp / 1000.0)
        time_str = dt_object.strftime("%Y-%m-%d %H:%M:%S")
        return time_str
    
# def get_formatted_day(timestamp):
#     dt_object = datetime.datetime.fromtimestamp(timestamp / 1000.0)
#     time_str = dt_object.strftime("%Y-%m-%d")
#     return time_str
