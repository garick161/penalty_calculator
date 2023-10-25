from datetime import date, timedelta
from bs4 import BeautifulSoup
import pandas as pd
import requests
import os

import warnings
warnings.filterwarnings('ignore')


def is_workday(day: date) -> bool:
    """Функция определяет рабочий день или выходной согласно рабочему календарю.
    True - рабочий
    False - выходной"""
    res = requests.get(f"https://isdayoff.ru/{day.strftime('%Y%m%d')}")
    return not bool(int(res.text))


def get_rate_df(start_date: date, end_date: date) -> (pd.DataFrame, int):
    """Функция для формирования датафрейма со ставками ЦБ в указанном временном диапазоне
    """
    #  Выполняем запрос на сайт ЦБ и вытягиваем данные о ключевых ставках в указанный период
    url = f"https://www.cbr.ru/hd_base/KeyRate/?UniDbQuery.Posted=True&UniDbQuery.From={start_date.strftime('%d.%m.%Y')}&UniDbQuery.To={end_date.strftime('%d.%m.%Y')}"
    full_page = requests.get(url)
    soup = BeautifulSoup(full_page.content, 'html.parser')
    res = soup.find_all("td")
    date_list = []
    rate_list = []
    [rate_list.append(float(res[i].text.replace(',', '.'))) if i % 2 != 0
     else date_list.append(res[i].text) for i in range(len(res))]
    #  Для удобства работы формируем датафрейм
    df = pd.DataFrame()
    df['date'] = date_list
    df['rate'] = rate_list
    df['date'] = pd.to_datetime(df['date'], dayfirst=True)
    #  Данные с сайта ЦБ имеют пропуски в выходные дни. Нам необходимо добавить пропущенные даты, а пустые ячейки
    #  со ставками заполняем последним актуальным значением
    df_date = pd.DataFrame(pd.date_range(start=df['date'].min(), end=df['date'].max()), columns=['date'])
    comm_df = pd.merge(df_date, df, on='date', how='left')
    comm_df['rate'] = comm_df['rate'].ffill()
    comm_df['is_work_day'] = comm_df['date'].map(is_workday)

    return comm_df, full_page.status_code


def rate_bd_update(first_date: date, last_date: date) -> int or None:
    """Функция для обновления базы ставок ЦБ, если запрошенный диапазон дат отсутствует"""
    status_code = None

    #  Если файла с базой ставок нет, то берем весь диапазон и результат записываем в файл
    if not os.path.exists('tables'):
        os.mkdir('tables')
    if not os.path.exists('tables/rate_db.csv'):
        df, status_code = get_rate_df(start_date=first_date, end_date=last_date)
        df.to_csv('tables/rate_db.csv', index=False)
        return status_code

    # Если файла с базой ставок - есть, подгружаем только необходимый диапазон
    df_rate = pd.read_csv('tables/rate_db.csv', parse_dates=['date'])
    max_date = df_rate['date'].max()
    min_date = df_rate['date'].min()
    if first_date < min_date:
        df, status_code = get_rate_df(start_date=first_date, end_date=min_date - timedelta(days=1))
        df_rate = pd.concat((df_rate, df), axis=0, ignore_index=True)
        df_rate = df_rate.sort_values('date')
        df_rate = df_rate.reset_index(drop=True)
        df_rate.to_csv('tables/rate_db.csv', index=False)
    if last_date > max_date:
        df, status_code = get_rate_df(start_date=max_date + timedelta(days=1), end_date=last_date)
        df_rate = pd.concat((df_rate, df), axis=0, ignore_index=True)
        df_rate = df_rate.sort_values('date')
        df_rate = df_rate.reset_index(drop=True)
        df_rate.to_csv('tables/rate_db.csv', index=False)

    return status_code


def calc_pay_before_day(sale_date: date, days_for_pay: str):
    """
    Функция - агрегатор. Определяет тип дней по договору(рабочие/календарные) и вызывает соответсвующую функцию.
    :param sale_date: дата продажи или оказания услуги.
    :param days_for_pay: количество и тип дней в виде строки (Например: 20 календарных).
    :return:
    - дату последнего дня отсрочки
    или
    - строку 'Дата не определена' в случае некорректных входных данных
    """
    count_days, type_days = days_for_pay.strip().split()
    if type_days == 'рабочих':
        return pay_before_for_workdays(sale_date=sale_date, count_days=int(count_days))
    elif type_days == 'календарных':
        return pay_before_for_cal_days(sale_date=sale_date, count_days=int(count_days))
    else:
        return 'Дата не определена'


def pay_before_for_cal_days(sale_date: date, count_days: int) -> date:
    """
    Функция расчета последнего дня отсрочки платежа с учетом календарных дней.
    :param sale_date: дата продажи или оказания услуги.
    :param count_days: количество дней по договору.
    :return: дата последнего дня отсрочки.
    """
    rate_df = pd.read_csv('tables/rate_db.csv', parse_dates=['date'])
    temp_df = rate_df[rate_df['date'] > sale_date].reset_index(drop=True)
    day_index = count_days - 1
    while not temp_df['is_work_day'][day_index]:
        day_index += 1
    return temp_df['date'][day_index]


def pay_before_for_workdays(sale_date: date, count_days: int) -> date:
    """
    Функция расчета последнего дня отсрочки платежа с учетом только рабочих дней.
    :param sale_date: дата продажи или оказания услуги.
    :param count_days: количество дней по договору.
    :return: дата последнего дня отсрочки.
    """
    rate_df = pd.read_csv('tables/rate_db.csv', parse_dates=['date'])
    return rate_df[(rate_df['date'] > sale_date) & (rate_df['is_work_day'])].reset_index(drop=True)['date'][count_days - 1]


def is_leap(date: pd.Timestamp) -> int:
    year = date.year
    if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
        return 366
    else:
        return 365


def calc_penalty(row):
    return round((row['sum'] * (row['rate']/100) * row['delay_period']) / row['day_in_year'], 2)


def date2str(date):
    return date.strftime('%d.%m.%Y')


def bild_and_save_final(df: pd.DataFrame, name: str):
    """Функция выполнят преобразование итогового датафрейма для получения формата в соответствии
    с требованиями заказчика"""
    name = name.split('.')[0]
    final_col = ['document', 'sum', 'sale_date', 'pay_before', 'payment_date', 'delay_period', 'rate', 'penalty']
    col_with_dubl = ['document', 'sum', 'sale_date', 'pay_before', 'payment_date']

    # Отбираем только необходимые колонки
    final_df = df.copy()[final_col]

    # Переводим формат даты в строку
    for col in ['sale_date', 'pay_before', 'payment_date']:
        final_df[col] = final_df[col].map(date2str)

    # Меняем дубликаты на пустые ячейки
    final_df[col_with_dubl] = final_df[col_with_dubl].mask(final_df[col_with_dubl].duplicated(), "")
    final_df = final_df.reset_index().rename(columns={'index': 'num_row'})
    final_df.loc[len(final_df)] = ['', '', 'Итого:', '', '', '', '', '', final_df['penalty'].sum()]

    final_df = final_df.rename(columns={'num_row': '№ строки',
                                        'document': 'док-ты о реализации(акт, накладная, УПД)',
                                        'sum': 'Сумма долга',
                                        'sale_date': 'Дата реализации',
                                        'pay_before': 'Оплатить до',
                                        'payment_date': 'Дата оплаты',
                                        'delay_period': 'Срок просрочки',
                                        'rate': 'Ставка ЦБ',
                                        'penalty': 'Неустойка'})
    final_df.to_excel(f'tables/{name}_result.xlsx', index=False)
    return os.path.abspath(f'tables/{name}_result.xlsx')
