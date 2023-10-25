import functions as fc
from tkinter import ttk, HORIZONTAL, filedialog, messagebox
import tkinter as tk
import pandas as pd
from pathlib import Path
import os

import warnings
warnings.filterwarnings('ignore')


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Расчет неустойки')
        self.geometry('450x250')
        self.resizable(width=False, height=False)
        self["bg"] = "#e0e9f4"

        self.pr_bar = ttk.Progressbar(self, orient=HORIZONTAL, length=200, mode='determinate')
        self.pr_bar.place(x=170, y=150)

        self.name_table = tk.Label(self, text='', bg='#e0e9f4')
        self.name_table.place(x=150, y=50)

        self.file_path = tk.Label(self, text='', bg='#e0e9f4')
        self.file_path.place(x=30, y=180)

        self.load_table_btn = tk.Button(self, text='Загрузить таблицу', command=self.choose_file)
        self.load_table_btn.place(x=30, y=50)
        self.calc_btn = tk.Button(self, text='Выполнить расчёт', command=self.main_process)
        self.calc_btn.place(x=30, y=150)
        self.calc_btn['state'] = 'disabled'

    def choose_file(self):
        filetypes = (("Файлы Excel", "*.xlsx *.xlsm *.xls *.xlsb"),)
        filename = filedialog.askopenfilename(title="Открыть файл", initialdir=os.path.curdir,
                                              filetypes=filetypes)
        if filename:
            path = Path(filename)
            self.df_input = pd.read_excel(filename)
            if len(self.df_input) == 0:
                self.name_table['text'] = 'Вы выбрали пустую таблицу'
                self.name_table['fg'] = 'red'
                self.update_idletasks()
            elif not set(self.df_input.columns) == {'document', 'sum', 'sale_date', 'days_for_pay', 'payment_date'}:
                self.name_table['text'] = 'Неверное название колонок в таблице'
                self.name_table['fg'] = 'red'
                self.update_idletasks()
            else:
                self.name_table['text'] = path.name
                self.name_table['fg'] = 'black'
                self.calc_btn['state'] = 'normal'
                self.update_idletasks()

        else:
            self.name_table['text'] = 'Таблица не выбрана'
            self.name_table['fg'] = 'red'
            self.update_idletasks()

    def main_process(self):
        # обновление базы данных при необходимости
        min_date = self.df_input['sale_date'].min()
        max_date = self.df_input['payment_date'].max()

        self.file_path['text'] = 'Обновление базы данных...'
        self.update_idletasks()

        # При обновлении базы данных возвращается статус код, который далее обрабатываем в случае ошибки
        self.code_error = fc.rate_bd_update(first_date=min_date, last_date=max_date)
        if self.code_error == 403:
            messagebox.showwarning(title='Ошибка 403', message='Возможно количество обращений к сайту www.cbr.ru превышено\nПопробуйте запустить расчет через некоторое время')
            self.file_path['text'] = ''
            self.update_idletasks()
            return None
        elif self.code_error == 404:
            messagebox.showwarning(title='Ошибка 404', message='Проверьте соединение с интернетом')
            self.file_path['text'] = ''
            self.update_idletasks()
            return None

        # загружаем обновленную базу со ставками
        rate_df = pd.read_csv('tables/rate_db.csv', parse_dates=['date'])

        # Формируем итоговый датафрейм
        df_res = pd.DataFrame()

        self.pr_bar['value'] = 0
        self.pr_bar['maximum'] = len(self.df_input)

        for i in range(len(self.df_input)):
            # Берем по одной строке и далее уже работаем с ней
            row = self.df_input.loc[i, :]
            # Определяем дату последнего дня отсрочки платежа
            pay_before = fc.calc_pay_before_day(sale_date=row['sale_date'], days_for_pay=row['days_for_pay'])
            pay_date = self.df_input['payment_date'][i]
            df_delay = rate_df[(rate_df['date'] > pay_before) & (rate_df['date'] <= pay_date)]

            # Добавляем количество дней в году
            df_delay['day_in_year'] = df_delay['date'].map(fc.is_leap)
            # Выполняем агрегации и добавляем необходимые колонки
            df_group_delay = df_delay.groupby(['rate', 'day_in_year'])['date'].agg(['count'])
            df_group_delay = df_group_delay.reset_index().rename(columns={'count': 'delay_period'})
            df_group_delay['document'] = row['document']
            df_group_delay['pay_before'] = pay_before
            df_res = pd.concat((df_res, df_group_delay), axis=0, ignore_index=True)
            self.pr_bar['value'] = i + 1

        # Выполняем соединение полученной таблицы с исходной по названию документа
        df_res = pd.merge(df_res, self.df_input, on='document', how='left')
        # Рассчитываем неустойку
        df_res['penalty'] = df_res.apply(fc.calc_penalty, axis=1)
        # Выполняем косметические преобразования с требованиями заказчика и сохраняем таблицу
        path_to_file = fc.bild_and_save_final(df=df_res, name=self.name_table['text'])
        self.file_path['text'] = path_to_file
        self.update_idletasks()


if __name__ == '__main__':
    app = App()
    app.mainloop()
