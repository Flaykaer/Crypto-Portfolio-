from binance.um_futures import UMFutures
import pandas as pd
import numpy as np
import time
import json
import requests
import telebot
import datetime
import mplfinance as mpf
# import os
import matplotlib
from matplotlib import pyplot as plt
import statistics
import io
import psutil                                       ### для логов контроля оперативной памяти    -nk-
# from copy import deepcopy
matplotlib.use("agg")


print('all libs imported', f"Память: {psutil.Process().memory_info().rss / 1024 ** 2:.2f} МБ")  ### Отладка -nk-



ERROR_TG = '-### '     ###    -nk-
LOGS_TG =  '-### '     ###   -nk-
# STAT_TG =  '-### '     ### пока в логи
VJ_A1_SCR_TG = "-### "  ##   -nk-
VJ_TRADES_TG = "-### "  ##  -nk-
STAT_TG = '-### '
# TG_BOT_TOKEN = "### :### "   ### 
TG_BOT_TOKEN = "### :### "   ###   
bot = telebot.TeleBot(TG_BOT_TOKEN)

client_0 = UMFutures()                                                      ### только для сбора данных, без торговли -nk-
# key = "### "       # 400
# secret = "### "
client400 = UMFutures(key, secret)
# key = "### "       # 402
# secret = "### ### ### "
client402 = UMFutures(key, secret)
# key =  "### "      # 399
# secret = "### "
client = UMFutures(key, secret)
my_acc = []
acc400 = []
acc402 = []

NAME_COL_A1 = ["symbol", "alert_time", "link", "vol", "cond", "clear_pnl_x_vol", "time_open", "time_open_serv", 
               "time_close", "time_close_serv", "open_price", "close_price", "pnl", "clear_pnl", "quantity", "trade_no", "alert_price"]
PERIOD = 1                      ### периодичность в минутах проверок на отрисовку 


e_str = "error unnown"


def send_photo(chat_id, file, cap):
        url = f'https://api.telegram.org/bot{TG_BOT_TOKEN}/sendPhoto'
        files = {'photo': file}
        data = {'chat_id': chat_id, "caption": cap}
        response = requests.post(url, files=files, data=data)
        json_response = response.json()
        return json_response


def dt2ts(dtime: str) -> int:
    """Переврдит строку дату-время МОСКОВСКОЕ в метку времени"""
    dt_str = str(dtime).partition(".")[0].replace("T", " ").partition("+")[0]
    dt_str = f'{dt_str}.+0300'
    return int(datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S.%z').timestamp()) * 1000    


for delay in range(10):
    try:
        with open('/projects/short_VJ/time_last_check.txt', 'r') as f:
            time_last_check, time_last_drawn, hour_check_1h_vj, check_day_vj  = json.loads(f.read())
        print(f'load time_last_check')
        break
    except Exception as e:
        time.sleep(0.5 + 0.5 * delay)
        # print(f' load fail. {e}', end="")
        e_str = f"{e.args}, {e.__class__}, {e.__doc__}"
        hour_check_1h_vj = 0
        check_day_vj = (datetime.datetime.now() + datetime.timedelta(hours= 3)).day
else:
        print(f'Drawer: initial load fail.\n{e_str}')
        bot.send_message(ERROR_TG, f'Drawer: initial load  fail.\n{e_str}')
        time.sleep(1)
        time_last_check = time.time()
        time_last_drawn = time_last_check - 15 * 60 * 60
time_last_drawn = max(time_last_drawn, time_last_check - 15 * 60 * 60)

for delay in range(10):
    try:
        with open('/projects/short_VJ/account_screener.txt', 'r') as f:
            account_screener = json.loads(f.read())
        break
    except Exception as e:
        time.sleep(0.5 + 0.5 * delay)
        e_str = f"{e.args}, {e.__class__}, {e.__doc__}"
else:
        account_screener = [[[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], 0]]
        print(f'Drawer: account_screener load fail.\n{e_str}')
        bot.send_message(ERROR_TG, f'Drawer: account_screener load  fail.\n{e_str}')


for delay in range(10):
    try:
        short_data_ver = pd.read_csv('/projects/short_VJ/short_data_ver.csv', delimiter=',')
        if len(short_data_ver.columns) == 1:
            short_data_ver = pd.read_csv('/projects/short_VJ/short_data_ver.csv', delimiter=';')
        break
    except Exception as e:
        time.sleep(0.5 + 0.5 * delay)
        # print(f' short_data_ver load fail. {e}', end="")
        e_str = f"{e.args}, {e.__class__}, {e.__doc__}"
else:
        print(f'Drawer: short_data_ver load fail.\n{e_str}')
        bot.send_message(ERROR_TG, f'Drawer: short_data_ver load  fail.\n{e_str}')
        time.sleep(1)
        short_data_ver = pd.DataFrame(columns=NAME_COL_A1)  ### создаём пустую стату, только если 10 раз не смогли открыть csv

# short_data_ver = short_data_ver[short_data_ver.alert_time.astype(str).map(lambda x: x[:4]!="2024")]
short_data_ver["link"] = short_data_ver["link"].map(lambda x: x if str(x)[0] != "0" else "")
price_acc = {s: 0.0 for s in short_data_ver.symbol}

for delay in range(5):
    try:
        VJ_data = pd.read_csv('/projects/short_VJ/VJ_data.csv', delimiter=',')
        if len(VJ_data.columns) == 1:
            VJ_data = pd.read_csv('/projects/short_VJ/VJ_data.csv', delimiter=';')
        break
    except Exception as e:
        time.sleep(0.02 + 0.02 * delay)
        e_str = f"{e.args}, {e.__class__}, {e.__doc__}"
else:
        print(f'Drawer: VJ_data load fail.\n{e_str}')
        bot.send_message(ERROR_TG, f'Drawer: VJ_data load  fail.\n{e_str}')
        time.sleep(1)
        VJ_data = short_data_ver.copy()  ### делаем копию статы без ссылок, только если 5 раз не смогли открыть csv      
# VJ_data["link"] = VJ_data["link"].map(lambda x: x if (x == "" or str(x)[0] != "0") else "")
# VJ_data = VJ_data[VJ_data.symbol.astype(str) != "0"]

for delay in range(10):
    try:
        with open('/projects/short_VJ/vj_links.txt', 'r') as f:
            vj_links = json.loads(f.read())
        break
    except Exception as e:
        time.sleep(0.5 + 0.5 * delay)
        e_str = f"{e.args}, {e.__class__}, {e.__doc__}, delay={delay}"
else:
    try:
        vj_links = {f"{row.symbol}_{int(row.alert_time)}": row.link for _, row in VJ_data.iterrows()}
        print(f'Drawer: vj_links created from VJ_data')
        time.sleep(1)
    except Exception as e:
        print(f"Drawer: vj_links load  fail.\n{e}\n\ne_str= {e_str}") 
        bot.send_message(ERROR_TG, f'Drawer: vj_links load  fail.\n{e}\n\ne_str= {e_str}')
        vj_links = {}

vj_links = {k: ("" if (len(str(v)) < 4 or str(v).endswith("//")) else (f'https://t.me/{v}' if (len(str(v)) < 10) else v)) for k, v in vj_links.items()}

def try_to_draw():
    """Проверяет текущую стату и рисует скрин при готовности по вермени"""
    global time_last_check, time_last_drawn, short_data_ver, PERIOD, ERROR_TG, e_str, hour_check_1h_vj, VJ_data, vj_links, price_acc

    # print(".", end="")
    if time.time() < time_last_check:
        print(",", end="")
        time.sleep(20)                                 ### если не прошла минута с прошлого рисования, ждём неск.секунд, и проверяем снова
        return
    print("t=", get_formatted_time(time_last_check*1000 + 3*60*60*1000)[5:], end=" \t")
    
    time_last_check = time_last_check + PERIOD * 60     ### отмечаем, когда искать следующий скрин для отрисовки
    try:
        with open('/projects/short_VJ/time_last_check.txt', 'w') as f:
            f.write(json.dumps([time_last_check, time_last_drawn, hour_check_1h_vj, check_day_vj]))
    except Exception as e:
        print(f'time_last_check save fail. {e}')
        bot.send_message(ERROR_TG, f'!!! Drawer: time_last_check save fail !!!\n{e}')
        time.sleep(1)

    try:
        with open('/projects/short_VJ/account_screener.txt', 'w') as f:
            f.write(json.dumps(account_screener[-14400*5:]))              ### пишу 10*5 дней, до этого - затираю  
    except Exception as e:
        print(f'account_screener save fail. {e}')
        bot.send_message(ERROR_TG, f'!!! Drawer: account_screener save fail !!!\n{e}')
        time.sleep(1)

    for delay in range(5):
        try:
            short_data_ver = pd.read_csv('/projects/short_VJ/short_data_ver.csv', delimiter=',')
            if len(short_data_ver.columns) == 1:
                short_data_ver = pd.read_csv('/projects/short_VJ/short_data_ver.csv', delimiter=';')
            print("+", end="")
            break                                       ### обновляем, ордербук, он же стата, он же лог действий
            #print(a1_data)
        except Exception as e:
            time.sleep(0.1 + 0.1 * delay)               ### пробуем 5 раз с нарастающей задержкой
            e_str = f"{e.args}, {e.__class__}, {e.__doc__}"
    else:
        bot.send_message(ERROR_TG, f'!!! Drawer: short_data_ver reading failed !!!\n{e_str}')  ### если не удалось, работаем со старой статой
        time.sleep(1)
    short_data_ver = short_data_ver[short_data_ver.alert_time.astype(str).map(lambda x: x[:4]!="2024")]
    short_data_ver["link"] = short_data_ver["link"].map(lambda x: x if str(x)[0] != "0" else "")


    ############################ проверка остатка ########################################
    try:
        VJ_data["pos"] = (VJ_data["open_price"] * VJ_data["quantity"] * VJ_data["vol"])

        try:
            acc400 = client400.account(recvWindow=5000000)
            print("400+", end="")
        except Exception as e:
            bot.send_message(ERROR_TG, f'!!! Drawer: client400.account(recvWindow=5000000) failed !!! I try again\n{e}')  ### 
            time.sleep(5)
            try:
                acc400 = client400.account(recvWindow=5000000)
            except Exception as e:
                bot.send_message(ERROR_TG, f'!!! Drawer: client400.account(recvWindow=5000000) failed 2nd time !!!\n{e}')  ### 
                time.sleep(5)
        unrealizedProfit400 = round(sum((float(dct['unrealizedProfit']) for dct in acc400['positions'])), 2)
        open_pos400 = -sum((float(dct['notional']) for dct in acc400['positions']))
        bal400 = float(acc400['availableBalance'])

        try:
            acc402 = client402.account(recvWindow=5000000)
            print("402+", end="")
        except Exception as e:
            bot.send_message(ERROR_TG, f'!!! Drawer: client400.account(recvWindow=5000000) failed !!! I try again\n{e}')  ### 
            time.sleep(5)
            try:
                acc402 = client402.account(recvWindow=5000000)
            except Exception as e:
                bot.send_message(ERROR_TG, f'!!! Drawer: client400.account(recvWindow=5000000) failed 2nd time !!!\n{e}')  ### 
                time.sleep(5)
        unrealizedProfit402 = round(sum((float(dct['unrealizedProfit']) for dct in acc402['positions'])), 2)
        open_pos402 = -sum((float(dct['notional']) for dct in acc402['positions']))
        bal402 = float(acc402['availableBalance'])

        try:
            my_acc = client.account(recvWindow=5000000)
            print("399+", end="")
        except Exception as e:
            bot.send_message(ERROR_TG, f'!!! Drawer: client.account(recvWindow=5000000) failed !!! I try again\n{e}')  ### 
            time.sleep(5)
            try:
                my_acc = client.account(recvWindow=5000000)
            except Exception as e:
                bot.send_message(ERROR_TG, f'!!! Drawer: client.account(recvWindow=5000000) failed 2nd time !!!\n{e}')  ### 
                time.sleep(5)                                

        # print("^1", end="")
        my_unrealizedProfit = round(sum((float(dct['unrealizedProfit']) for dct in my_acc['positions'])), 2)
        # print("^2", end="")
        open_pos = VJ_data[VJ_data.cond == "enter"].groupby("symbol")["pos"].sum().round().astype(int).sort_values(ascending=False)
        # open_pos = -sum((float(dct['notional']) for dct in my_acc['positions']))
        # print("^3", end="")
        next_pos = (VJ_data[VJ_data.cond == "enter"].groupby("symbol")["pos"].max().round().astype(int).astype(int) + 6).sort_values(ascending=False).head(5)
        open_pos_str = " + ".join([f"{i[:-4]}={v}" for i, v in open_pos.items()])
        next_pos_str = " ".join([f"{i[:-4]}={v}," for i, v in next_pos.items()])
        bal = float(my_acc['availableBalance'])

        account_screener.append([[bal, float(my_acc['totalWalletBalance']), my_unrealizedProfit, -sum((float(dct['notional']) for dct in my_acc['positions'])), float(next_pos.sum()), int(my_acc["assets"][4]["updateTime"])], 
                                 [bal400, float(acc400['totalWalletBalance']), unrealizedProfit400, open_pos400, 0, int(acc400["assets"][4]["updateTime"])],
                                 [bal402, float(acc402['totalWalletBalance']), unrealizedProfit402, open_pos402, 0, int(acc402["assets"][4]["updateTime"])], float(time.time())])
        
        if int(bal * 5) < next_pos.sum():
            print("!!!                                         Мало денег                                !!!")
        # print(bal * 5, next_pos.sum())
            print(f"💥💥💥  свободно {int(bal)} из {int(float(my_acc['totalWalletBalance']))}, c плечом={int(bal * 5)}, ждём: {next_pos_str} (открыты на {open_pos.sum()}: {open_pos_str}) 💥💥💥 ")
        print("pr=", my_unrealizedProfit, "|", unrealizedProfit400, "|", unrealizedProfit402, end=".")
    except Exception as e:
        bot.send_message(ERROR_TG, f'!!! Drawer: balance check failed !!!\n{e}')  ### 
    ############################ конец проверки остатка ########################################


    # if short_data_ver.alert_time.min()
    # data_to_draw = short_data_ver[(short_data_ver.alert_time > time_last_drawn * 1000) & (short_data_ver.alert_time < time_last_check - 13*60*60*1000)].copy()
    print("not_drawn=", sum(short_data_ver.alert_time.astype(float) > float(time_last_drawn) * 1000), end=" \t")
    print("13h_passed=", sum(short_data_ver.alert_time.astype(float) < float(time_last_check) * 1000 - 13*60*60*1000), end=" \t")
    to_draw = sum((short_data_ver.alert_time.astype(float) > float(time_last_drawn) * 1000) & (short_data_ver.alert_time.astype(float) < float(time_last_check) * 1000 - 13*60*60*1000))
    print("to_draw=", to_draw)

    if to_draw == 0 and (psutil.Process().memory_info().rss / 1024 ** 2 > 600):
        print('memory > 600 Mb', f"Память: {psutil.Process().memory_info().rss / 1024 ** 2:.2f} МБ")  ### Отладка -nk-
        bot.send_message(ERROR_TG, f'Drawer memory > 600 Mb, restart')  ### перезапуск
        exit()


    send_stats_links()


    if not any((short_data_ver.alert_time > time_last_drawn * 1000) & (short_data_ver.alert_time < float(time_last_check) * 1000 - 13*60*60*1000)):
        time.sleep(20)                                 ### если все, алёрты, пришедшие более 13 часов назад отрисованы, просто ждём полминуты, и проверяем снова
        return
    try:
        alert_time_to_draw = short_data_ver.loc[(short_data_ver.alert_time > time_last_drawn * 1000), "alert_time"].min()
        ### получаем время самого старого неотрисованного алёрта, реже - нескольких при точном совпадении времени
    except Exception as e:
        bot.send_message(ERROR_TG, f'Drawer: try_to_draw fail. ??? min([]).\n{e}')
        time.sleep(1)

    for _, row in short_data_ver[short_data_ver.alert_time == alert_time_to_draw].drop_duplicates(subset="symbol").iterrows():
        ### скользим по самым старым неотрисованным алёртам со всеми монетами (обычно только 1)
        if float(row.open_price) > 0:
            # bot.send_message(ERROR_TG, f'Drawer: want to draw {row.symbol}')
            time.sleep(1)
            send_screen(row.symbol, int(row.alert_time), float(row.alert_price), short_data_ver)
        else:
            # bot.send_message(ERROR_TG, f'Drawer: want to draw {row.symbol} empty')
            time.sleep(1)
            send_screen(row.symbol, int(row.alert_time), float(row.alert_price), short_data_ver)

    time_last_drawn = alert_time_to_draw / 1000  ### омечаем, что все алёрты до этого и этот отрисованы
    


def send_stats_links():
        try:
            global hour_check_1h_vj, check_day_vj, time_last_check, time_last_drawn, VJ_data, short_data_ver, price_acc
            hour_now = datetime.datetime.now() + datetime.timedelta(hours=3)
            day = hour_now.day
            hour_now = hour_now.hour

            if hour_now != hour_check_1h_vj:
                
                now = datetime.datetime.now() + datetime.timedelta(hours= 3) 
                before = datetime.datetime.now() - datetime.timedelta(hours= 1) + datetime.timedelta(hours= 3)
                now_hour = now.strftime("%H")
                before_hour = before.strftime("%H")
                date = before.strftime("%Y-%m-%d")
                try:
                    with open('/projects/data/price_acc.txt', 'r') as f:
                        price_acc = json.loads(f.read())
                except Exception:
                    time.sleep(5)
                    try:
                        with open('/projects/data/price_acc.txt', 'r') as f:
                            price_acc = json.loads(f.read())
                    except Exception:
                        pass

                try:
                    VJ_data = short_data_ver.drop(columns=["link"]).copy()
                    # tmp_ser = short_data_ver[["symbol", "alert_time"]].apply(lambda x: vj_links.setdefault(f"{x["symbol"]}_{int(x["alert_time"])}", ""), axis=1).map(lambda x: x if (x == "" or str(x)[-1] not in ("//", r"/")) else " ").copy()
                    tmp_ser = short_data_ver[["symbol", "alert_time"]].apply(lambda x: vj_links.setdefault(f'{x["symbol"]}_{int(x["alert_time"])}', ""), axis=1).map(lambda x: x if (x == "" or str(x)[-1] not in ("//", r"/")) else " ")
                    VJ_data.insert(2, "link", tmp_ser)

                    tmp_ser = VJ_data["alert_time"].astype(np.int64)
                    VJ_data.drop(columns=["alert_time"], inplace=True)
                    VJ_data.insert(1, "alert_time", tmp_ser)

                    with pd.ExcelWriter(f"/projects/short_VJ/excel/vj_to_hour_{now_hour}.xlsx") as writer:
                        data_to_excel = VJ_data[VJ_data.alert_time > time.time()*1000//86400000*86400000-16*60*60*1000].copy()
                        print(" 1$ ", end="")
                        tmp_ser = data_to_excel["alert_time"].map(lambda x: get_formatted_time(x + 3*60*60*1000) if len(str(x))!=19 else x)
                        print(" 1.2$ ", end="")
                        data_to_excel.drop(columns=["alert_time"], inplace=True)
                        print(" 1.5$ ", end="")
                        data_to_excel.insert(1, "alert_time", tmp_ser)
                        print(" 2$ ", end="")
                        data_to_excel["alert_time"].fillna(0, inplace=True)
                        data_to_excel.fillna("", inplace=True)   ### заполнение условного закрытия на момент отправки статы
                        print(" 3$ ", end="")
                        if not all(data_to_excel.open_price.apply(lambda x: isinstance(x, float))):
                            print("------               open_price                -------")
                            tmp_ser = data_to_excel.open_price.fillna(0).apply(lambda x: 0 if x=="" else x)
                            data_to_excel.drop(columns=["open_price"], inplace=True)
                            data_to_excel.insert(10, "open_price", tmp_ser)
                        else:
                            print(" 3.1$ ", end="")
                        if not all(data_to_excel.close_price.apply(lambda x: isinstance(x, float))):
                            print("------               close_price                -------")
                            tmp_ser = data_to_excel.close_price.fillna(0).apply(lambda x: 0 if x=="" else x)
                            data_to_excel.drop(columns=["close_price"], inplace=True)
                            data_to_excel.insert(10, "close_price", tmp_ser)
                        else:
                            print(" 3.2$ ", end="")                            

                        not_closed_ser = (data_to_excel.time_close.astype(str).apply(len) < 5) & (data_to_excel.open_price.astype(float) > 0.000000001)

                        print(" 3.5$ ", end="")
                        data_to_excel.loc[not_closed_ser, ["time_close", "time_close_serv"]] = get_formatted_time(time.time()*1000 + 3*60*60*1000)
                        print(" 4$ ", end="")
                        data_to_excel.loc[not_closed_ser, "close_price"] = data_to_excel.symbol.map(lambda x: float(price_acc[x][-1]))
                        print(" 5$ ", end="")
                        data_to_excel.loc[not_closed_ser, "pnl"] = round((1 - data_to_excel.close_price.astype(float) / data_to_excel.open_price.astype(float)) * 100, 2)
                        print(" 6$ ", end="")
                        data_to_excel.loc[not_closed_ser, "clear_pnl"] = data_to_excel["pnl"] - 0.16
                        print(" 7$ ", end="")
                        data_to_excel.loc[not_closed_ser, "clear_pnl_x_vol"] = data_to_excel.clear_pnl * data_to_excel["vol"]
                        print(" 8$ ", end="")
                        data_to_excel = data_to_excel[data_to_excel.symbol.astype(str) != "0"].copy()
                        print(" 8.5$ ", end="")

                        data_to_excel.to_excel(writer, index=False, sheet_name='Sheet_name_4')
                        print(" 9$ ", end="")
                    time.sleep(1)
                    print(" 10$ ")
                    with open(f'/projects/short_VJ/excel/vj_to_hour_{now_hour}.xlsx', 'rb') as f:
                        bot.send_document(chat_id= VJ_A1_SCR_TG, document=f, caption=f'A1_VJ to_hour {now_hour} {date}')                        
                except Exception as e:
                    bot.send_message(ERROR_TG, f'A1_VJ 1st send VJ_data fail\n\n{e}')
                    try:
                        time.sleep(5)
                        VJ_data = VJ_data[NAME_COL_A1].copy()
                        VJ_data = VJ_data[VJ_data.symbol.astype(str) != "0"]
                        with pd.ExcelWriter(f"/projects/short_VJ/excel/vj_to_hour_{now_hour}.xlsx") as writer:  
                            data_to_excel = VJ_data[(VJ_data.alert_time.astype(str) > str(int(time.time()*1000//86400000*86400000)-16*60*60*1000))].copy()
                            if not all(data_to_excel.open_price.apply(lambda x: isinstance(x, float))):
                                tmp_ser = data_to_excel.open_price.fillna(0).apply(lambda x: 0 if x=="" else x)
                                data_to_excel.drop(columns=["open_price"], inplace=True)
                                data_to_excel.insert(10, "open_price", tmp_ser)
                            if not all(data_to_excel.close_price.apply(lambda x: isinstance(x, float))):
                                tmp_ser = data_to_excel.close_price.fillna(0).apply(lambda x: 0 if x=="" else x)
                                data_to_excel.drop(columns=["close_price"], inplace=True)
                                data_to_excel.insert(10, "close_price", tmp_ser)
                            data_to_excel.loc[:, ["alert_time"]] = data_to_excel["alert_time"].map(lambda x: get_formatted_time(x + 3*60*60*1000) if len(str(x))!=19 else x)
                            data_to_excel.fillna("", inplace=True)   ### заполнение условного закрытия на момент отправки статы
                            data_to_excel.loc[((data_to_excel.time_close == "") | (data_to_excel.time_close.apply(str.lower) == "nan")) & (data_to_excel.open_price.astype(float) != 0), 
                                              ["time_close", "time_close_serv"]] = get_formatted_time(time.time()*1000 + 3*60*60*1000)
                            data_to_excel.loc[((data_to_excel.time_close == "") | (data_to_excel.time_close.apply(str.lower) == "nan")) & (data_to_excel.open_price.astype(float) != 0), 
                                              "close_price"] = data_to_excel.symbol.map(lambda x: round(float(price_acc[x][-1]), 2))
                            data_to_excel.loc[((data_to_excel.time_close == "") | (data_to_excel.time_close.apply(str.lower) == "nan")) & (data_to_excel.open_price.astype(float) != 0), 
                                              "pnl"] = round((1 - data_to_excel.close_price.astype(float) / data_to_excel.open_price.astype(float)) * 100, 2)
                            data_to_excel.loc[((data_to_excel.time_close == "") | (data_to_excel.time_close.apply(str.lower) == "nan")) & (data_to_excel.open_price.astype(float) != 0), 
                                              "clear_pnl"] = data_to_excel.pnl - 0.16
                            data_to_excel.loc[((data_to_excel.time_close == "") | (data_to_excel.time_close.apply(str.lower) == "nan")) & (data_to_excel.open_price.astype(float) != 0), 
                                              "clear_pnl_x_vol"] = data_to_excel.clear_pnl * data_to_excel.vol

                            data_to_excel.to_excel(writer, index=False, sheet_name='Sheet_name_4')
                        time.sleep(1)
                        print("$ $ $ $ $ $ $ $ $ $")
                        with open(f'/projects/short_VJ/excel/vj_to_hour_{now_hour}.xlsx','rb') as f:
                            bot.send_document(chat_id= VJ_A1_SCR_TG, document=f, caption=f'A1_VJ to_hour {now_hour} {date}')                          
                    except Exception as e: 
                        bot.send_message(ERROR_TG, f'A1_VJ 2nd send VJ_data fail\n\n{e}')
                
                if int(hour_now) == 1:   
                    pass
                else:
                    if hour_now == 0 or check_day_vj != day:  # or hour_now == 1 or hour_now == 2:

                        #info = client.account(recvWindow=50000)
                        #balance = round(float(info['totalWalletBalance']), 2)
                        #bot.send_message(stat_tg, f'Short_DE balance: {balance}$')

                        try:
                            time.sleep(10)
                            with pd.ExcelWriter(f"/projects/short_VJ/VJ_data.xlsx") as writer:
                                data_to_excel = VJ_data[(VJ_data.alert_time.astype(str) > str(int(time.time()*1000//86400000*86400000)-16*60*60*1000))
                                                         & (VJ_data.alert_time.astype(str) <= str(int(time.time()*1000//86400000*86400000)+8*60*60*1000))].copy()
                                
                                tmp_ser = data_to_excel["alert_time"].map(lambda x: get_formatted_time(x + 3*60*60*1000) if len(str(x))!=19 else x)
                                data_to_excel.drop(columns=["alert_time"], inplace=True)
                                data_to_excel.insert(1, "alert_time", tmp_ser)

                                data_to_excel.to_excel(writer, index=False, sheet_name='Sheet_name_4')
                            with open(f'/projects/short_VJ/VJ_data.xlsx','rb') as f:
                                bot.send_document(chat_id= STAT_TG, document=f, caption=f'A1_VJ {before_hour}-{now_hour} {date}')
                            time.sleep(10)
                            # with open(f'/projects/short_VJ/VJ_data.xlsx','rb') as f:
                            with open(f'/projects/short_VJ/excel/vj_to_hour_{now_hour}.xlsx','rb') as f:    
                                bot.send_document(chat_id= ERROR_TG, document=f, caption=f'A1_VJ {before_hour}-{now_hour} {date}')
                            VJ_data = VJ_data[VJ_data.alert_time > int(time.time()*1000//86400000*86400000)-184*60*60*1000].copy()
                            VJ_data = VJ_data[VJ_data.symbol.astype(str) != "0"].copy()
                            time.sleep(1)
                            # pd.DataFrame(columns=name_col_a1)
                        except Exception as e:
                            bot.send_message(ERROR_TG, f'A1_VJ send VJ_data fail\n\n{e}')
                            time.sleep(1)
                        
                
                try:
                    check_day_vj = day
                    hour_check_1h_vj = hour_now
                    with open('/projects/short_VJ/time_last_check.txt', 'w') as f:
                        f.write(json.dumps((time_last_check, time_last_drawn, hour_check_1h_vj, check_day_vj)))
                    #quit()
                except Exception as e:
                    bot.send_message(ERROR_TG, f'A1_VJ hour_check_1h_vj save fail\n\n{e}')                
                

        except Exception as e:
            #bot.send_message(stat_tg, 'send stats fail')
            bot.send_message(ERROR_TG, f'A1_VJ Short_VJ send stats fail\n\n{e}')
            time.sleep(1)
            print('fail send all')        



def screen(symb, i, df, time_last_alert_scr, price_last_alert_scr, df_btc, channel_data, alert_type):
        # из VerNS
        global ERROR_TG, bot
        try:
            # ######################### код Ивана  ###########################
            # try:
            #     df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume']
            #     df['Close'] = df['Close'].astype(float)
            #     df['High'] = df['High'].astype(float)
            #     df['Low'] = df['Low'].astype(float)
            #     df['Open'] = df['Open'].astype(float)
            #     df['Time'] = df['Time'].astype(np.int64)
            #     df['Number of trades'] = df['Number of trades'].astype(int)
            #     df['Volume'] = df['Volume'].astype(float)
            #     df['Taker buy base asset volume'] = df['Taker buy base asset volume'].astype(float)                
            #     df["timestamp"] = df.iloc[:, 0].copy()
            #     time_last_alert_scr = np.int64(float(time_last_alert_scr))
            #     # [True True False True] x1 ->>   [True False False False] , [False True False False] , [ False False False True ] x3 (True x3)
            #     def get_dummies_df( condition ):
            #                 true_indexes = condition[ condition == True].index
            #                 total = []
            #                 for i in range( condition.sum() ):
            #                     b = deepcopy(condition)
            #                     not_false_index = true_indexes[i]
            #                     b.loc[:] = False
            #                     b.loc[not_false_index] = True
            #                     total.append(b)
            #                 return total 
                
            #     # На вход подается массив из меток timestamp , на выходе там где по времени мы в сделке - стоит цена входа , там где не в сделке - np.nan
            #     def filt_price( enter_position_timestamp , close_position_timestamp  , timestamp_series, enter_position_price):
            #             if   enter_position_timestamp <= timestamp_series and timestamp_series <= close_position_timestamp :
            #                 return enter_position_price
            #             else :
            #                 return np.nan
                        
            #     # Возвращает массивы [ False ... True ] , где True - период после сделки 
            #     def after_trades_periods( lst , end_of_all_trades_index , num_candles_after_trade = 15 ): # 15 - Период который анализируется после сделки
            #         indexes = lst[lst != 0].index
            #         diffs = indexes.diff()
            #         total = []
            #         temp = []
            #         for i , d in zip(indexes , diffs):
                        
            #             if  d == np.nan or d == 1.0:
            #                     temp.append(i)
            #             else :
            #                     total.append(deepcopy(temp))
            #                     temp.clear()
            #                     temp.append(i)

            #         if len(temp) != 0 :
            #                 total.append(temp)

            #         total = list(filter(lambda x : len(x), total)) 
            #         after_trades_ind = []
            #         for i in range( len(total) - 1):
            #                 min(total[i+1]) -  max(total[i])
            #                 for i in range( max(total[i]) + 1 , min(total[i+1]) ):
            #                         after_trades_ind.append(i)
                    
            #         for i in range(total[-1][-1] , len(lst)):
            #             after_trades_ind.append(i)
            #         after_trades_list = deepcopy(lst)
            #         after_trades_list.iloc[:] = False
            #         after_trades_list.iloc[ after_trades_ind ] = True
            #         after_trades_list.iloc[len(after_trades_list) - 1  ] = False
            #         continues_by_trades = []
            #         for index_start , index_end  in zip( after_trades_list[ after_trades_list.diff() == 1].index , after_trades_list[ after_trades_list.diff() == -1].index ) :
            #                 temp = deepcopy(after_trades_list)

            #                 temp.iloc[ : index_start] = False 

            #                 temp.iloc[ index_end : ] = False 

            #                 temp.iloc[ index_start + num_candles_after_trade : ] = False 

            #                 temp.iloc[end_of_all_trades_index : ] = False

            #                 continues_by_trades.append(temp)
                        
            #         return continues_by_trades

            # #РАссчет индикатора точки входа в сделку. Отрисовка периода в сделке 
                
            #     #Работа с channel_data
            #     all_price_open = channel_data['open_price']
            #     all_price_close = channel_data['close_price']
            #     all_time_open = channel_data['time_open_serv']
            #     all_time_close = channel_data['time_close']

            #     channel_price = []
            #     channel_time = []

            #     for open , close , t_open , t_close in zip( all_price_open , all_price_close , all_time_open , all_time_close):
            #         channel_price.append(open)
            #         channel_price.append(close)


            #         channel_time.append(t_open)
            #         channel_time.append(t_close)
            #     #
            #     how = 'Close'

            #     ratios = []
            #     all_hlines = []
            #     fill_betweens = []
            #     detailed_ratios = []
            #     trading_periods = []
                

                
            #     channel_price1 = list( map ( lambda x : round((  x - float(price_last_alert_scr)) / float(price_last_alert_scr) * 100, 2) ,  channel_price  ) )
                
            #     position_prices =  [channel_price1[i:i+2] for i in range(0, len(channel_price1), 2)]
            #     position_times =   [channel_time[i:i+2] for i in range(0, len(channel_time), 2)]

            #     num_trades = len(position_prices)

            #     max_potentials_vsdelke = []
            #     for num in range(num_trades):


            #         enter_position_price_line = np.vectorize(filt_price)( position_times[num][0] , position_times[num][1] , df['timestamp'] , position_prices[num][0])
            #         all_hlines.append( enter_position_price_line )

            #         in_position_indexes = df[ pd.Series(enter_position_price_line).notna()].index

            #         in_position_df = deepcopy( df.iloc[ in_position_indexes ])


            #         trading_periods.append( [ 0 if num not in in_position_indexes else float(x)  for num ,  x in enumerate(enter_position_price_line)] )

            #         in_trades_gather = pd.Series([sum(column) for column in zip(*trading_periods)])


            #         if how == 'Close' :
            #             delta = ( (in_position_df['Close'].astype(float) - float(price_last_alert_scr)) / float(price_last_alert_scr) * 100 ) - position_prices[num][0]

            #         if how == 'open' :
            #             delta = ( (in_position_df['open'].astype(float) - float(price_last_alert_scr)) / float(price_last_alert_scr) * 100 ) - position_prices[num][0]

            #         if how == 'median':
            #             delta = (in_position_df['high'].astype(float) + in_position_df['low'].astype(float))/2 - position_prices[num][0]

                    
            #         positiv_delta =  delta[ delta >= 0 ].sum()
            #         negativ_delta =  delta[ delta < 0 ].sum()

            #         ratio = float(np.round( float( np.abs(negativ_delta) / np.abs(positiv_delta)) , 4 ))
            #         detailed_ratios.append( [ positiv_delta , np.abs(negativ_delta)])
            #         ratios.append(ratio)

            #         norm_close = ( (df['Close'].astype(float) - float(price_last_alert_scr)) / float(price_last_alert_scr) * 100 )

                    
            #         potential_vsdelke = np.array([0])
                    


            #         #for green

            #         condition = (pd.Series(enter_position_price_line).notna()) & (norm_close > position_prices[num][0])
            #         lst_of_conditions = get_dummies_df(condition)


            #         for lst in lst_of_conditions:


            #             fill_betweens.append(  dict(y1= position_prices[num][0] , y2= norm_close  , 
                
            #                                 alpha = 0.8 , where = lst , color = '#FF9999' , 
            #                                     linewidths = [ 5 for i in range(len(lst))]) 
            #                 )
                        
            #             ind_green =  list(lst[ lst == True].index)[0] 
                        
            #             potential = np.array(norm_close[ind_green] -  position_prices[num][0] )

            #             potential_vsdelke = np.append( potential_vsdelke , potential)

                    

            #         # for red 

            #         condition1 = (pd.Series(enter_position_price_line).notna()) & (norm_close <=  position_prices[num][0] )
            #         lst_of_conditions1 = get_dummies_df(condition1)

            #         for lst in lst_of_conditions1:
                    
            #             fill_betweens.append(  dict(y1= position_prices[num][0] , y2= norm_close   , 
            #                                     alpha = 0.8 , where = lst  , color = '#CCFFCC',
            #                                     linewidths  = [ 5 for i in range(len(lst))] ) 
            #                                     )
            #             ind_red =  list(lst[ lst == True].index)[0] 

            #             potential = np.array(norm_close[ind_red] -  position_prices[num][0] )

            #             potential_vsdelke = np.append( potential_vsdelke , potential)

            #         max_potentials_vsdelke.append( [  -1 *  round( float(potential_vsdelke[ potential_vsdelke >= 0 ].max()) + 0.16 , 4 )          ,   round( np.abs(float(potential_vsdelke[ potential_vsdelke < 0 ].min() )) - 0.16 , 4 )         ]  )

                    
                                        
            #     # Индикатор точки выхода из сделки . Отрисовка периода после сделки 
            #     detailed_ratios = list(map( lambda x : [ round(float(x[0]) , 4) , round( float(x[1]) , 4) ] , detailed_ratios  ))
            
            #     if not isinstance(time_last_alert_scr , (np.int64 , np.float64 , int , float)) :
                    
            #         time_last_alert_scr = list(time_last_alert_scr)[0]
                    

            #     del_sec_time_alert_scr = int(datetime.datetime.fromtimestamp( time_last_alert_scr / 1000).replace(second= 0 ).timestamp() ) * 1000
            #     end_of_all_trades_index = list(df[ df['timestamp'] == del_sec_time_alert_scr ].index)[0] + 120

            #     after_trades_zones = after_trades_periods(in_trades_gather , end_of_all_trades_index , num_candles_after_trade = 15)

            #     norm_close = ( (df['Close'].astype(float) - float(price_last_alert_scr)) / float(price_last_alert_scr) * 100 ) 

                
            #     position_prices =  [channel_price[i:i+2] for i in range(0, len(channel_price), 2)]
            
            #     position_times =   [channel_time[i:i+2] for i in range(0, len(channel_time), 2)]

                
            #     position_prices_norm = []
            #     for pos in position_prices:
            #         temp = []
            #         for digit in pos:
            #             norm_digit = (digit - float(price_last_alert_scr) ) /  float(price_last_alert_scr) * 100
            #             temp.append(norm_digit)
            #         position_prices_norm.append( deepcopy(temp))
                    
                        
            #     position_prices =  position_prices_norm        

            #     adjustment_ratios = []
            #     abs_adj_squares = []
            #     max_potentials_posle_sdelki = [ ]

            #     for num , current_trade_zone in enumerate(after_trades_zones):

            #         mp = np.array([ 0 ])
                    


            #         pos_component = 0 
            #         neg_component = 0 

            #         current_trade_zone_by_candle = get_dummies_df(current_trade_zone)

            #         for candle in current_trade_zone_by_candle:
                            
            #                 true_ind = candle[ candle == True ].index
                            

            #                 #print('trueind' , true_ind)

            #                 close = list(norm_close[true_ind])[0]
            #                 #print(close - np.abs(close - position_prices_norm[num][1]) ) 
                            
            #                 mp = np.append( mp , np.array([ close - position_prices_norm[num][1] ]) )
                        
            #                 #position_prices_norm[num][0]

            #                 if close > position_prices_norm[num][1]:
            #                     pos_component += np.abs(close - position_prices_norm[num][1] ) 
                            

                                

            #                     #y1= position_prices[num][0]
            #                     fill_betweens.append(  dict(y1= position_prices[num][1] , y2= norm_close   , 
            #                                     alpha = 0.6 , where = candle  , color = '#CCFFCC', 
            #                                     linewidths  = [ 5 for i in range(len(candle))] ) 
            #                                     )
            #                 else : 
            #                     neg_component += np.abs(  close - position_prices_norm[num][1]  )
                            
                                

            #                     fill_betweens.append(  dict(y1= position_prices[num][1] , y2= norm_close   , 
            #                                     alpha = 0.6 , where = candle  , color = '#FF9999',
            #                                     linewidths  = [ 5 for i in range(len(candle))] ) 
            #                             )

                            
                                
            #                 #true_ind = list(true_ind)[0]

            #         max_potentials_posle_sdelki.append( [ round( -1 * float( mp[ mp >= 0 ].max() + 0.16 ) , 4 ) ,  round(  float( abs(mp[ mp < 0 ].min()) - 0.16 ) , 4 )   ] )

            #         #max_potentials_adj.append( [ round(float(mp_pos) - 0.16 , 4 )  , round(float(mp_neg)  + 0.16 , 4 ) ])
                    
                                
            #         #adjustment_ratios.append( round( float(( detailed_ratios[num][0] + pos_component ) / ( detailed_ratios[num][1] + neg_component ))  , 4 ))
            #         abs_adj_squares.append( [ round(float(pos_component),4) , round(float(neg_component),4) ])
            #         adjustment_ratios.append( round( float((  pos_component ) / (  neg_component + 0.0000001 ))  , 4 ))
            #         #print(f' det pos {detailed_ratios[num][0]} , pos {pos_component} , det neg {detailed_ratios[num][1]} , neg {neg_component}')
                                
                    
                    
            #     t = []
            #     for num , current_trade_zone in enumerate(after_trades_zones):
            #         digit = position_prices_norm[num][1] #0
            #         current_trade_zone = pd.Series(current_trade_zone)
            #         current_trade_zone[ current_trade_zone == True ] = digit 
            #         current_trade_zone[ current_trade_zone == False ] = np.nan
            #         t.append( current_trade_zone)

            
            #     open_price_lines = [ mpf.make_addplot(i , color='b' ,  secondary_y=False , marker = '--') for i in all_hlines]
            #     close_price_lines = [ mpf.make_addplot(i , color='red' ,  secondary_y=False , marker = '--') for i in t]



                

            # except Exception as e:
            #     bot.send_message(ERROR_TG, f'Drawer_VJ  screen failed-1 {symb} i={i}\n\n{e}')
            #     time.sleep(1)


            #     ###################  КОНЕЦ КОДА ИВАНА  ###########################

            try:
                # print('start send screen Drawer_VJ', symb, end="\t") 

                #time.sleep(0.01)
                # bot.send_message(ERROR_TG, f'start send screen Drawer_VJ {symb}, alert_type={alert_type}, time_last_alert={time_last_alert_scr}')
                time.sleep(1)
                df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume']
                time_alert = int(time_last_alert_scr - (time_last_alert_scr % 60000))

                print("time_alert=", time_alert, get_formatted_time(time_alert), end=" \t")

                df['Time_alert'] = time_alert
                price_last_alert_scr = price_last_alert_scr if price_last_alert_scr != 0 else price_last_alert_scr + 0.000001
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
                bot.send_message(ERROR_TG, f'Drawer_VJ  screen failed-1 {symb} i={i}\n\n{e}')
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
                if len(ind) == 0:
                    ind = df.index.values.astype(int)[:1]
                    print("###    len(ind) == 0     ###")
                    bot.send_message(ERROR_TG, f'Drawer_VJ screen: {symb} len(ind) == 0')
                    time.sleep(1)

                print("ind=", ind, end=" \t")

                # ind_1_line = ind[0] - 15
                ind_2_line = ind[0] + 120 + 1
                
                line_1 = time_alert - 10 * 60 * 1000 + 3 * 60 * 60 * 1000
                line_2 = time_alert + 120 * 60 * 1000 + 3 * 60 * 60 * 1000
                line_3 = time_alert + 12*60 * 60 * 1000 + 3 * 60 * 60 * 1000
                df_line = pd.DataFrame({'Data': [line_1, line_2, line_3]})
                df_line['Data_line'] = pd.to_datetime(df_line['Data'], unit = 'ms')

                # if len(channel_time_scr) % 2 == 1:s
                #     channel_time_scr = channel_time_scr + [int(time_alert + 299 * 60 * 1000)]
                #     channel_price_scr = channel_price_scr + [float(df.iloc[ind[0] + 299]['Close'])]
                #     channel_cond_scr = channel_cond_scr + ['e']

                VJ_pnl = []
                x_pnl = []
                x_pnl_clear = 0

                print("VJ_pnl=", VJ_pnl)
                linestyle =  "-"

                for _, row in channel_data.iterrows():
                    row.fillna(0, inplace=True)
                    # print(row)
                    if row.open_price and row.quantity != 0 and row.quantity != "0":

                        print(f"if-1 row={row.values}")

                        time_open = int(dt2ts(row.time_open) // 60000 * 60000)
                        ind_time_open = df[df['Time'] >= time_open].index.values.astype(int)[0]
                        df.loc[ind_time_open, 'price_open'] = round((float(row.open_price) - price_last_alert_scr) / price_last_alert_scr * 100, 2)
                        try:
                            df.loc[ind_time_open, 'open_cond'] = f"x{int(row.vol)}"
                        except Exception: pass
                        df.loc[df[df['Time'] >= int(row.alert_time)].index.values.astype(int)[0], 'signal'] = round((float(row.alert_price) - price_last_alert_scr) / price_last_alert_scr * 100, 2)
                    elif int(row.alert_time) != 0:

                        print("elif-1 row=", str(row.values))

                        df.loc[df[df['Time'] >= int(row.alert_time)].index.values.astype(int)[0], 'signal'] = round((float(row.alert_price) - price_last_alert_scr) / price_last_alert_scr * 100, 2)
                        # try:
                        #     df.loc[df[df['Time'] >= int(row.alert_time)].index.values.astype(int)[0], 'open_cond'] = str(row.cond)
                        # except Exception: pass

                    if row.close_price and row.quantity != 0 and row.quantity != "0":

                        print("if-2 row=", str(row.values))

                        time_close = int(dt2ts(row.time_close) // 60000 * 60000)
                        ind_time_close = df[df['Time'] >= time_close].index.values.astype(int)[0]
                        df.loc[ind_time_close, 'price_close'] = round((float(row.close_price) - price_last_alert_scr) / price_last_alert_scr * 100, 2)
                        try:
                            df.loc[ind_time_close, 'close_cond'] = str(row.cond)
                        except Exception: pass
                    # elif row.open_price and row.quantity != 0 and row.quantity != "0":

                    #     print("elif-2 row=", str(row.values))

                    #     time_close = int(df.iloc[-1, 0] // 60000 * 60000)  ### последний тиаймстамп в датафрейме
                    #     ind_time_close = df[df['Time'] >= time_close].index.values.astype(int)[0]
                    #     df.loc[ind_time_close, 'price_close'] = round((float(df.iloc[-1, 4]) - price_last_alert_scr) / price_last_alert_scr * 100, 2)
                    #     try:
                    #         df.loc[ind_time_close, 'close_cond'] = "cont"
                    #     except Exception: pass                        

                    if "cont" in row.cond and float(row.open_price) != 0:

                        print("if-3 row=", str(row.values))
                        linestyle= "--"

                        VJ_pnl = VJ_pnl + [round((float(row.open_price) - float(row.close_price)) / float(row.open_price) * 100, 2) + 0.16]
                        x_pnl = x_pnl + [round(VJ_pnl[-1] * float(row.vol), 2)]
                        x_pnl_clear = round(x_pnl_clear + x_pnl[-1] - 0.16 * float(row.vol), 2)

                    elif row.cond in ("SL", "DE", "SL^", "DE^", "e", "e^", "0", 0) and float(row.open_price) != 0:

                        print("elif-3 row=", str(row.values))

                        VJ_pnl = VJ_pnl + [round((float(row.open_price) - float(row.close_price)) / float(row.open_price) * 100, 2)]
                        x_pnl = x_pnl + [round(VJ_pnl[-1] * float(row.vol), 2)]
                        x_pnl_clear = round(x_pnl_clear + (VJ_pnl[-1] - 0.16) * float(row.vol), 2)
                    else:

                        # print("else-3 row=", str(row.values))

                        pass
                        # VJ_pnl = VJ_pnl + [0.16]

                df.loc[df.index[0], 'signal'] = None

                VJ_pnl_total = round(sum(VJ_pnl), 2)
                VJ_pnl_clear = round(VJ_pnl_total - len(VJ_pnl) * 0.16, 2)     ### комисс + сквиз

                df.loc[ind_2_line + 2, 'pnl_description'] = x_pnl_clear / 2
                # df['avg_vol'] = df['Volume'] / df['Number of trades']
                index_vol = round(float(df.iloc[ind[0]]['Volume'] / max(df['Volume'][ind[0]-5: ind[0]].mean(), 0.000000001)), 2)
                
                # df['typ_price'] = ((df.High + df.Close + df.Low) / 3 ) * df.Volume
                # df.loc[ind[0], 'signal'] = 0 

            except Exception as e:
                bot.send_message(ERROR_TG, f'Drawer_VJ  screen failed-2 {symb} i={i}\n\n{e}')
                time.sleep(1)
                ind = df[df['Time'] >= time_alert].index.values.astype(int)[:1]
            try:                
                df['Time'] = df['Time'] + 3 * 60 * 60 * 1000
                # df = df.merge(df_vol, on='Time', how='left')
                df = df.merge(df_btc, on='Time', how='left')
                df = df.where(pd.notnull(df), None)
                df['Close_btc'] = df['Close_btc'].astype(float)
                df['High'] = df['High'].astype(float)
                df['Low'] = df['Low'].astype(float)

            except Exception as e:
                bot.send_message(ERROR_TG, f'Drawer_VJ  screen failed-3 {symb} i={i}\n\n{e}')
                time.sleep(1)
            try:                
                if len(df['Low']) == 0:
                    bot.send_message(ERROR_TG, f"Drawer_VJ len(df['Low']) == 0 in screen, i={i}, symb={symb}")  ### отладка - поиск min([])   -nk-
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
                
                percent_high = round(((float(max(df['High'][ind[0]: ind_2_line])) - float(price_last_alert_scr)) / float(price_last_alert_scr) * 100), 2)
                
                if len(df['Low'][(ind[0]+1):ind_2_line]) == 0:
                    bot.send_message(ERROR_TG, f"Drawer_VJ bag min([]): len(df['Low'][(ind[0]+1):ind_2_line]) == 0 in screen, i={i}, symb={symb}")  ### отладка - поиск min([])   -nk-
                    time.sleep(1)

                percent_low = round(((float(min(df['Low'][(ind[0]+1): ind_2_line])) - float(price_last_alert_scr)) / float(price_last_alert_scr) * 100), 2)
                
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
                bot.send_message(ERROR_TG, f'Drawer_VJ  screen failed-4 {symb} i={i}\n\n{e}')
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
                    power_emoji = f'{"legendary_100"}'
                elif percent_high >= 60 or percent_low <= -60:
                    power_emoji = f'{"legendary_60"}'
                elif percent_high >= 40 or percent_low <= -40:
                    power_emoji = f'{"legendary_40"}'
                elif percent_high >= 30 or percent_low <= -30:
                    power_emoji = f'{"legendary_30"}'
                elif percent_high >= 20 or percent_low <= -20:
                    power_emoji = f'{"legendary_20"}'
                elif percent_high >= 16 or percent_low <= -16:
                    power_emoji = f'{"legendary_16"}'
                elif percent_high >= 12 or percent_low <= -12:
                    power_emoji = f'{" ! "}{" ! "}{" ! "}'
                elif percent_high >= 6 or percent_low <= -6:
                    power_emoji = f'{" ! "}{" ! "}'
                elif percent_high >= 3 or percent_low <= -3:
                    power_emoji = f'{" ! "}'
                else:
                    power_emoji = ' '

                df['Close'] = round((df['Close'] - float(price_last_alert_scr)) / float(price_last_alert_scr) * 100, 2)
                df['Open'] = round((df['Open'] - float(price_last_alert_scr)) / float(price_last_alert_scr) * 100, 2)
                df['High'] = round((df['High'] - float(price_last_alert_scr)) / float(price_last_alert_scr) * 100, 2)
                df['Low'] = round((df['Low'] - float(price_last_alert_scr)) / float(price_last_alert_scr) * 100, 2)
                btc_zero_price = df.iloc[ind[0]]['Close_btc']
                delta = df.iloc[0]['Close']
                df['Close_btc'] = round((df['Close_btc'] - float(btc_zero_price)) / float(btc_zero_price) * 100, 2) + delta

                if len(df['Close'][:ind[0]]) == 0:
                    bot.send_message(ERROR_TG, f"Drawer_VJ len(df['Close'][:ind[0]]) == 0 in screen, i={i}, symb={symb}")  ### отладка - поиск min([])   -nk-
                    time.sleep(1)
                    return ""

            except Exception as e:
                bot.send_message(ERROR_TG, f'Drawer_VJ  screen failed-5 {symb} i={i}\n\n{e}')
                time.sleep(1)
            try:
                if len(VJ_pnl) == 0:
                    df['pnl_line'] = 0
                else:
                    df['pnl_line'] = VJ_pnl_clear
                
                apds = [mpf.make_addplot(df['signal'],type='scatter', color='#2d5ff5', alpha = 0.6, markersize=50, secondary_y=False),
                        mpf.make_addplot(df['pnl_line'],type='scatter', color='purple', alpha = 0.6, markersize=0.1, secondary_y=False),
                        mpf.make_addplot(df['line_alert'],type='scatter', color='g', markersize=0.1, secondary_y=False),
                        mpf.make_addplot(df['price_close'], type='scatter', color='r', markersize=20, marker='v', secondary_y=False),
                        mpf.make_addplot(df['price_open'], type='scatter', color='g', markersize=20, marker='^', secondary_y=False),
                        mpf.make_addplot(df['Close_btc'], color='y', alpha = 0.3, secondary_y=False),
                        ]
                # ###КОД ИВАНА
                # apds.extend(open_price_lines)
                # apds.extend(close_price_lines)
                # ###
            except Exception as e:
                bot.send_message(ERROR_TG, f'Drawer_VJ  screen failed-6 {symb} i={i}\n\n{e}')
                time.sleep(1)
            try:
                cap = (f'VJ \t {description} \t {symb} \t {power_emoji} \t clear_pnl: {VJ_pnl_clear}%')
                    #    f'\t take_clear_potential: {round(VJ_pnl_clear/(percent_high if alert_type != 2 else -percent_low)*100, 2)}%')
                
                title_mess = (f'\n\n\nVJ {symb}, price: {price_last_alert_scr}, time: {time_pump}\n'
                              f'max={percent_high}%, min={percent_low}%, coef={count_plus_pnl}/{count_minus_pnl}, Ind_Vol= {index_vol}\n'
                              f'x_pnl_clear: {x_pnl_clear:.2f}%, x_pnl_total: {sum(x_pnl):.2f}%, x_comm+sq: {x_pnl_clear - sum(x_pnl):.2f}%, '
                              f'count_trades: {len(VJ_pnl)},    '
                              f'clear_pnl: {VJ_pnl_clear}%, total_pnl: {VJ_pnl_total}%, comm+sq: {round(len(VJ_pnl) * 0.16, 2)}%, \n'
                            #   f'take_potential: {round(VJ_pnl_total/percent_high*100,2)}%, '
                            #   f'take_clear_potential: {round(VJ_pnl_clear/(percent_high if alert_type != 2 else -percent_low)*100,2)}%,\n'
                              f'x_pnl_trades: {x_pnl},     pnl_trades: {VJ_pnl}') 
                            #   f'x_pnl_trades: {x_pnl},     pnl_trades: {VJ_pnl}\n'
                            #   #От Ивана
                            #   f'ratios : {ratios} abs_squares: {detailed_ratios} max_potentials% {max_potentials_vsdelke} \n'
                            #   f'adj_ratios: {adjustment_ratios} abs_adj_squares: {abs_adj_squares} max_potentials_adj% {max_potentials_posle_sdelki} \n')
                            #   #От Ивана

                ### сохраняем последний трейд для отправки в wtp all
                # trade_str = f'Drawer_VJ: {VJ_pnl_clear}% / {round(VJ_pnl_clear/percent_high*100,2)}%'
                
                vl = dict(vlines=[df_line.iloc[0, 1], df_line.iloc[1, 1], df_line.iloc[2, 1]], linewidths=(1, 1, 1), colors=("blue", "blue", "darkred"), alpha=0.6, linestyle=linestyle)
                buf6 = io.BytesIO()

                # df['where'] = (df['Close'] == df['Close'].iloc[ind_2_line + 2]) & (df['Open'] == df['Open'].iloc[ind_2_line + 2]).values
            except Exception as e:
                title_mess = ''
                bot.send_message(ERROR_TG, f'Drawer_VJ  screen failed-7 {symb} i={i}\n\n{e}')
                time.sleep(1)
            try:
                fig, axlist = mpf.plot(df, type='candle', style='yahoo', volume=True, addplot=apds, vlines=vl,
                                       title=title_mess, fontscale=0.6, panel_ratios=(4,1), figratio=(30,14), 
                                       returnfig=True, show_nontrading=True, warn_too_much_data=1000)
                axlist[0].set_xticks(np.arange((min(df.index.to_list()) + datetime.timedelta(1/24/4)).round('30 min'), max(df.index.to_list()), 1800000000))
                axlist[0].set_yticks(range(int(df.Low.min()), int(df.High.max()) + 1))
                # axlist[0].set_ylim(-20, 15)
                # axlist[0].text(df.index[0], df.High.max() * 0.9 + df.Low.min() * 0.1, "LONG" if alert_type == 1 else "SHORT",
                # axlist[0].text(df.index[0], 10, "LONG" if alert_type == 1 else "SHORT", color= "lime" if alert_type == 1 else "magenta", fontstyle='normal', fontsize=24)                    
                df_op_cond = df.open_cond.dropna()
                for x,t in df_op_cond.items():
                    y = df.loc[x,'price_open']+percent_high/2*0.2
                    # print("x=", x, " y=", y, " t=", t, end=" \t")
                    axlist[0].text(x,y,t,fontstyle='normal', fontsize='x-large')
                df_cl_cond = df.close_cond.dropna()
                for x,t in df_cl_cond.items():
                    y = df.loc[x,'price_close']+percent_high/2*0.2
                    # print("x=", x, " y=", y, " t=", t, end=" \t")
                    axlist[0].text(x,y,t,fontstyle='normal', fontsize='x-large')
                df_pnl_description = df.pnl_description.dropna()
                for x,t in df_pnl_description.items():
                    y = df.loc[x,'pnl_description']
                    t = t * 2
                    # print("x=", x, " y=", y, " t=", t, end=" \t")
                    axlist[0].text(x,y,t,fontstyle='italic', fontsize='x-large')
            except Exception as e:
                bot.send_message(ERROR_TG, f"Drawer_VJ  screen failed-8 {symb} i={i}\n\n{e}\n\nI'll try 1 more time")
                time.sleep(1)
                try:
                    fig, axlist = mpf.plot(df, type='candle', style='yahoo', volume=True, addplot=apds, vlines=vl, 
                                           title=title_mess, fontscale=0.6, panel_ratios=(4,1), figratio=(30,14), 
                                           returnfig=True, show_nontrading=True, warn_too_much_data=1000)
                    axlist[0].set_xticks(np.arange((min(df.index.to_list()) + datetime.timedelta(1/24/4)).round('30 min'), max(df.index.to_list()), 1800000000))
                    axlist[0].set_yticks(range(int(df.Low.min()), int(df.High.max()) + 1))
                    # axlist[0].set_ylim(-20, 15)
                    # axlist[0].text(df.index[0], df.High.max() * 0.9 + df.Low.min() * 0.1, "LONG" if alert_type == 1 else "SHORT", color= "lime" if alert_type == 1 else "magenta", fontstyle='normal', fontsize=36)                       
                    df_op_cond = df.open_cond.dropna()
                    for x,t in df_op_cond.items():
                        y = df.loc[x,'price_open']+percent_high/2*0.2
                        # print("x=", x, " y=", y, " t=", t, end=" \t")
                        axlist[0].text(x,y,t,fontstyle='normal',fontsize='x-large')
                    df_cl_cond = df.close_cond.dropna()
                    for x,t in df_cl_cond.items():
                        y = df.loc[x,'price_close']+percent_high/2*0.2
                        # print("x=", x, " y=", y, " t=", t, end=" \t")
                        axlist[0].text(x,y,t,fontstyle='normal',fontsize='x-large')
                    df_pnl_description = df.pnl_description.dropna()
                    for x,t in df_pnl_description.items():
                        y = df.loc[x,'pnl_description']
                        t = t * 2
                        # print("x=", x, " y=", y, " t=", t, end=" \t")
                        axlist[0].text(x,y,t,fontstyle='italic',fontsize='x-large')
                except Exception as e:
                    bot.send_message(ERROR_TG, f'Drawer_VJ  screen failed-8 & lost (2 attempt) {symb} i={i}\n\n{e}')
                    time.sleep(1)
                    return ""
            try:
                fig.savefig(fname=buf6, dpi=100, pad_inches=0.25)

                f_id = 0
            # except Exception as e:
            #     bot.send_message(ERROR_TG, f'Drawer_VJ  screen failed-8.1 {symb} i={i}\n\n{e}')
            # try:
                buf6.seek(0)
                # f_id = send_photo(chat_id=ERROR_TG, file=buf6, cap=cap)
                f_id = send_photo(chat_id=VJ_A1_SCR_TG, file=buf6, cap=cap)
                try:
                    f_id = str(f_id['result']['message_id'])
                except Exception as e:
                    print("\nDrawer_VJ  screen f_id =", f_id, "\n", e)
                    bot.send_message(ERROR_TG, f'Drawer_VJ  screen f_id = {f_id}')                
                link = f'https://t.me/{f_id}'
                time.sleep(1)
                try:
                    if any(channel_data[channel_data.alert_time == time_last_alert_scr].time_close.apply(lambda x: len(str(x)) > 5)):
                        bot.send_message(ERROR_TG, f"\nDrawer_VJ send 2 screen {symb}\n{channel_data[channel_data.alert_time == time_last_alert_scr].time_close}\n{channel_data[channel_data.alert_time == time_last_alert_scr].time_close.apply(lambda x: len(str(x)))}")
                        
                    # if len(VJ_pnl) > 0:
                        fig.savefig(fname=buf6, dpi=150, pad_inches=0.05)
                        buf6.seek(0)
                        time.sleep(1)
                        f_id = send_photo(chat_id=VJ_TRADES_TG, file=buf6, cap=cap)
                        try:
                            f_id = str(f_id['result']['message_id'])
                        except Exception as e:
                            print("\nDrawer_VJ  screen f_id =", f_id, "\n", e)
                            bot.send_message(ERROR_TG, f'Drawer_VJ  screen f_id = {f_id}')
                        link = f'https://t.me/{f_id}'
                        time.sleep(1)
                except Exception as e:
                    print(f"\nDrawer_VJ send 2 screen failed {symb}\n", e)
                    bot.send_message(ERROR_TG, f"\nDrawer_VJ send 2 screen failed {symb}\n\n{e}")
                buf6.close()
                
                try:
                    for ax in axlist:
                            del ax
                    plt.cla()
                    plt.clf()

                    #plt.close(fig)
                    plt.close('all')
                    del fig, axlist
                except Exception: pass

                time.sleep(0.25)
                # print(f"Drawer_VJ  screen f_id = {f_id}")
                
            except Exception as e:
                bot.send_message(ERROR_TG, f'Drawer_VJ  screen failed-9 {symb} i={i}\n\n{e}')
                time.sleep(1)
            try:
                print('end send screen VJ')            
                return link
            except Exception as e:
                bot.send_message(ERROR_TG, f'Drawer_VJ  screen failed-10 {symb} i={i}\n\n{e}')
                time.sleep(1)
                return ""

        except Exception as e:
                bot.send_message(ERROR_TG, f'Drawer_VJ fail screen {symb} i={i}\n\n{e}')
                time.sleep(1)
                return ""


        
def send_screen(symb, alert_time, alert_price, short_data_ver):
        
        global e_str, bot, ERROR_TG, vj_links
        # взял из A1 
        for delay in range(5):
            try:
                dff = pd.DataFrame(client_0.klines(symbol=symb, interval='1m', limit=901))
                df_btc = pd.DataFrame(client_0.klines(symbol='BTCUSDT', interval='1m', limit=901))
                df_btc = df_btc.iloc[:,:-2]
                df_btc.columns = ['Time', 'Open', 'High', 'Low', 'Close_btc', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume']
                df_btc = df_btc[['Time', 'Close_btc']]
                df_btc['Time'] = df_btc['Time'] + 3 * 60 * 60 * 1000
                break
            except Exception as e:
                time.sleep(0.02 + 0.02 * delay)
                e_str = f"{e.args}, {e.__class__}, {e.__doc__}"
        else:
            bot.send_message(ERROR_TG, f'Drawer: {symb} klines load fail.\n{e_str}')
            time.sleep(1)
            return

        dff = dff.iloc[:, :-2]
        channel_data = short_data_ver[(short_data_ver.alert_time >= int(dff.iloc[0, 0])) & (short_data_ver.symbol == symb)].reset_index(drop=True)
        
        link = screen(symb=symb, i=1, df=dff, time_last_alert_scr=alert_time, 
                               price_last_alert_scr=alert_price, df_btc=df_btc, 
                               channel_data=channel_data, alert_type="short")
        # time.sleep(0.25)       
        excel_sand(symb=symb, time_alert=alert_time, link=link)

        ####################################################################  Выгрузка свеч в csv в defolt ##############
        try:
            # max_high = dff.loc[(dff.Time.astype(np.int64) > alert_time) & (dff.Time.astype(np.int64) <= alert_time + 120*60*1000), 'High'].astype(float).max()
            # bot.send_message(ERROR_TG, f'Drawer: {symb} alert_price={alert_price}, max_high={max_high}, %={max_high/alert_price}, {dff.loc[(dff.High.astype(float) == max_high), ["Time", "High"]]}'
            #                            f'min: {dff.loc[(dff.Time.astype(np.int64) > alert_time) & (dff.Time.astype(np.int64) <= alert_time + 120*60*1000), "High"].index.min()}'
            #                            f'min: {dff.loc[(dff.Time.astype(np.int64) > alert_time) & (dff.Time.astype(np.int64) <= alert_time + 120*60*1000), "High"].index.max()}')            
            # print("\nlen(all)=", len(dff), end=" ")
            # print("len(from)=", len(dff.loc[(dff.Time.astype(np.int64) > alert_time + 3*60*60*1000), 'High']), end=" ")
            # print("len(from)=", len(dff.loc[(dff.Time.astype(np.int64) > alert_time + 3*60*60*1000), 'High']), end=" ")
            # print("len(before)=", len(dff.loc[(dff.Time.astype(np.int64) <= alert_time + 3*60*60*1000 + 120*60*1000), 'High']), end=" ")
            # print("len(121)=", len(dff.loc[(dff.Time.astype(np.int64) > alert_time + 3*60*60*1000) & (dff.Time.astype(np.int64) <= alert_time + 3*60*60*1000 + 120*60*1000), 'High']), "\n")
            if (dff.loc[(dff.Time.astype(np.int64) > alert_time + 3*60*60*1000) & 
                        (dff.Time.astype(np.int64) <= alert_time + 3*60*60*1000 + 120*60*1000), 'High'].astype(float).max() / float(alert_price) > 1.03):
                bot.send_message(ERROR_TG, f'Drawer: {symb}-OK, %>3')
                for delay in range(5):
                    try:
                        csv_name = f'{symb}_{get_formatted_time(alert_time + 3*60*60*1000).replace(":", "_")}'
                        # if len(dff.columns) == 10:
                        #     dff.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume']
                        # else:
                        #     bot.send_message(ERROR_TG, f'Drawer: len(dff.columns) != 10   {csv_name}')
                        dff['Time_alert'] = int(alert_time - (alert_time % 60000))
                        dff['Price_alert'] = alert_price
                        dff.to_csv(f'short_VJ/defolt/{csv_name}.csv', index=False)
                        del(csv_name)
                        break
                    except Exception as e:
                        e_str = f"{e.args}, {e.__class__}, {e.__doc__}"
                        time.sleep(0.5 + 0.5 * delay)
                else:
                        print(f'Drawer: vj_links save fail')
                        time.sleep(1)
                        bot.send_message(ERROR_TG, f'Drawer: fail to load klines into csv into VJ-defolt 5 times {csv_name}\n{e_str}')
            del(dff)
        except Exception as e:
            bot.send_message(ERROR_TG, f'Drawer: loading klines into csv failed {symb}_{alert_time}\n{e}')
        ####################################################################  Конец выгрузки свеч в csv в defolt ##############        


def excel_sand(symb, time_alert, link):
    """Добавляет ссылку в стату в отдельном csv"""
    try:
        global VJ_data, bot, ERROR_TG, e_str, short_data_ver, vj_links

        vj_links[f"{symb}_{int(time_alert)}"] = link
    except Exception as e:
        bot.send_message(ERROR_TG, f'Drawer: excel_sand fail-1.1 {symb}\n{e}')
    try:        
        for delay in range(5):
            try:
                with open('/projects/short_VJ/vj_links.txt', 'w') as f:
                    f.write(json.dumps(vj_links))
                break
            except Exception as e:
                time.sleep(0.5 + 0.5 * delay)
        else:
                print(f'Drawer: vj_links save fail')
                time.sleep(1)
                bot.send_message(ERROR_TG, f'Drawer: vj_links save fail\n{e}')
    except Exception as e:
        bot.send_message(ERROR_TG, f'Drawer: excel_sand fail-1.2 {symb}\n{e}')
    try:

        VJ_data = short_data_ver.drop(columns=["link"])

        # tmp_ser = short_data_ver[["symbol", "alert_time"]].apply(lambda x: vj_links.setdefault(f"{x[0]}_{int(x[1])}", ""), axis=1).copy()
        tmp_ser = short_data_ver[["symbol", "alert_time"]].apply(lambda x: vj_links.setdefault(f'{x["symbol"]}_{int(x["alert_time"])}', ""), axis=1)
        VJ_data.insert(2, "link", tmp_ser)

    except Exception as e:
        bot.send_message(ERROR_TG, f'Drawer: excel_sand fail-1.3 {symb}\n{e}')
    try: 
        VJ_data = VJ_data.reset_index(drop=True).fillna(0)[NAME_COL_A1].copy()
        VJ_data["link"] = VJ_data["link"].map(lambda x: x if (x == "" or str(x)[0] != "0") else "") 
        if any((VJ_data.symbol == symb) & (VJ_data.alert_time == time_alert)):

            VJ_data.loc[(VJ_data.symbol == symb) & (VJ_data.alert_time == time_alert), "link"] = link
        for delay in range(5):
            try:
                # VJ_data = VJ_data[VJ_data.symbol.astype(str) != "0"]
                VJ_data.to_csv('/projects/short_VJ/VJ_data.csv', index=False)
                break
            except Exception as e:
                time.sleep(0.02 + 0.02 * delay)
                e_str = f"{e.args}, {e.__class__}, {e.__doc__}"
        else:
                print(f'Drawer: VJ_data save fail.\n{e_str}')
                bot.send_message(ERROR_TG, f'Drawer: VJ_data save fail.\n{e_str}')
                time.sleep(1)
    except Exception as e:
        bot.send_message(ERROR_TG, f'Drawer: excel_sand fai-2.{symb}\n{e}')
                        


def get_formatted_time(timestamp):
        dt_object = datetime.datetime.fromtimestamp(timestamp / 1000.0)
        time_str = dt_object.strftime("%Y-%m-%d %H:%M:%S")
        return time_str


bot.send_message(ERROR_TG, f'VJ Drawer restsrted')


if __name__ == "__main__":

    try:
        while True:
            try_to_draw()
            pass
            
    except KeyboardInterrupt:
        bot.send_message(ERROR_TG, f'!!! Drawer KeyboardInterrupt !!!')
        time.sleep(1)
        print("\n Drawer KeyboardInterrupt.")
