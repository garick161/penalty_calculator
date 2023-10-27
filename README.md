# Описание проблемы
Компания занимается арендой крупной строительной техники. Не все контрагенты оплачивают услугу вовремя по договору. По закону на период просрочки должна начисляться неустойка. Юридический отдел при подготовке документов рассчитывает сумму неустойки по каждой такой неуплаченной вовремя услуге.
Расчет неустойки производится по формуле:

$$Неустойка = \dfrac{ сумма\quad задолженности \quad *\quad ставка\quad ЦБ\quad *\quad Количество\quad дней\quad просрочки }{ Количество\quad дней\quad в\quad году }$$
Расчет усложняется тем, что ставка ЦБ в период просрочки может меняться и это нужно учитывать. Разбивать период на несколько и считать отдельно.
Год может быть високосным, тогда количество дней в году будет меняться.
У разных контрагентов разные условия по договору. У одного 20 рабочих дней отсрочки, у другого 20 календарных, у третьего другое количество дней.
>- Для расчета периода отсрочки платежа необходимо использовать рабочий календарь
>- День подписания договора, реализации не входит в срок отсрочки платежа
>- В случае рабочих дней по договору учитаваются только рабочии дни
>- В случае календарных дней по договору - считаются календарные дни. Но если последний день окончания срока попадает на выходной/праздничный день, тогда дата окончания срока переносится на ближайший следующий рабочий день.

Все эти моменты неудобно постоянно учитывать, а расчет для каждого документа становится очень трудозатратным.
Готового иструмента для расчета нет, а существующие онлайн-калькуляторы выдают неподходящий, местами избыточный результат. Такие отчеты требуют дополнительной ручной обработки.

# Постановка задачи
Нужно разработать программное обеспечение, которое выполняло бы расчет нейустойки автоматически с учетом вышеупомянутых условий.
Также в ходе общения будущими пользователями было принято решение не обрабатывать каждую заявку отдельно, а составлять таблицу со документами, а потом уже отдавать на обработку программы.\
В итоге была определена следующая структура:

![penalty_block_schema](https://github.com/garick161/penalty_calculator/assets/114688542/ae269876-9149-4cdb-b1bb-c00e373dbb10)

Данные о ключевой ставке будут запрашиватся с сайта ЦБ:\
[Ключевая ставка Банка России | Банк России (cbr.ru)](https://cbr.ru/hd_base/KeyRate/)https://cbr.ru/hd_base/KeyRate/

Пример исходной таблицы от пользователя:

![table_in](https://github.com/garick161/penalty_calculator/assets/114688542/b1a354a9-1939-44e4-8b20-9f720da6016f)


Пример таблицы - результат:

![table_out](https://github.com/garick161/penalty_calculator/assets/114688542/26cc7215-d926-4c27-aaee-17d1ce6edc92)

В качестве интерфейса взаимодействия пользователя было выбрано диалоговое окно Windows

![veiw_window_calc](https://github.com/garick161/penalty_calculator/assets/114688542/0d56c06d-23b3-489d-86e2-9dd13db42a07)


# Используемые ресурсы и библиотеки
- [Ключевая ставка Банка России | Банк России (cbr.ru)](https://cbr.ru/hd_base/KeyRate/)https://cbr.ru/hd_base/KeyRate/ - офицаильный сайт ЦБ. Можно получить актуальные значения ключевой ставки во указанный временной период
- https://isdayoff.ru/ - ресурс для определение выходного дня согласно рабочему календарю
- модуль `requests` - выполнение HTTP-запросов
- модуль `BeautifulSoup` - удобное полученние иформации с HTML разметки
- модуль `pandas` - работа с таблицами, расчеты, агрегации
- модуль `tkinter` - создание визуального интерфейса пользователя
- модуль `py2exe` - перобразовние Python скриптов в исполняемые программы Windows
- модуль `Inno Setup` - создание установщика программ Windows из набора файлов

# Файловая структура проекта
`root`
- `app.py` - главный файл приложения. Отвечает за визульное оформление, логику управления.
- `functions.py` - вспомгательный файл с функциями для `app.py`
- `calc_installer.exe` - установщик программ Windows. В него упаковно приложение. Вы можете скачать и установить как обычное приложение в Windows
- `requirements.txt` - полный список используемых библиотек

# Логика работы кратко
Логика работы для пользователя будет подробно расмотренна в руководстве пользователя 
https://drive.google.com/file/d/156DbUxLAj2Oeho4AcqCxlCchslWpW6xD/view?usp=sharing


После запуска приложения пользователю неоходимо выбрать исходную таблицу в любом доступном формате Excel.

> Количество запросов единицу времени на сайт ЦБ ограничено службой безопасности (3-5 раза подряд обработает, потом минут 10 блокирует). Система понимает, что запросы ведутся из приложения. Найти рабочего решения как сделать подмену и система думала, что запросы выполняются из браузера и реальным человеком у меня не получилось. Поэтому было принято решение свести количество запросов к минимуму и использовать кеширование данных. После первого запуска программы будет создан файл: `../tables/rate_df.csv`, где будут хранится данные о ставках и рабочий календарь за указанный временной период.

Программа анализирует диапазон дат в исходной таблице. Если он больше, чем в `rate_df.csv`, то подгружает недостающие данные.

Программа расчитывает период отсрочки согласно количеству дней по договору. Также выполняет агрегации и необходимые расчеты для получния финального формата таблицы, указанного заказчиком. Сохраняет в формате Excel.

# Руководство пользователя
https://drive.google.com/file/d/156DbUxLAj2Oeho4AcqCxlCchslWpW6xD/view?usp=sharing
















