# Постановка проблемы
Компания занимается аредной крупной строительной техники. Не все контрагенты оплачивают услугу во время по договору. По закону на время просрочки должна начисляеться неустойка. Юридический отдел при подготовке документов расчитывает сумму неустойки по каждой такой неоплаченной вовремя услуге.
Расчет неустойки производится по формуле:

$$Неустойка = \dfrac{ сумма\quad задолженности \quad *\quad ставка\quad ЦБ\quad *\quad Количество\quad дней\quad просрочки }{ Количество\quad дней\quad в\quad году }$$
Расчет усложняется тем, что ставка ЦБ в период просрочки может меняться, это нужно учитывать. Разбивать период на несколько и считать отдельно.
Год может быть високосным, тогда количество дней в году будет меняться.
У разных контрагентов разные условия по договору. У одного 20 рабочих дней отсрочки, у другого 20 календарных, у третьего другое количество дней.
>- Для расчета периода отсрочки платежа необходимо использовать рабочий календарь\
>- День подписания договора, реализации не входит в срок отсрочки платежа\
>- В случае рабочих дней по договору учитаваются только рабочии дни\
>- В случае календарных дней по договору - считаются календарные дни. Но если последний день окончания срока попадает на выходной/праздничный день, тогда дата окончания срока переносится на ближайший следующий рабочий день.

Все эти моменты неудобно постоянно учитывать, а расчет каждого документа становится очень трудозатратным.
Готового иструмента для рачета нет, а существующие онлайн калькуляторы выдают неподходящий, местами избыточный результат. Такие отчеты требуют дополнительной ручной обработки.

# Постановка задачи
Нужно разработать программное обеспечение, которое выполняло бы расчет нейустойки автоматически с учетом вышеупомянутых условий.
Также сходе общения будущими пользователями было принято решение не обрабатывать каждую заявку отдельно, а составлять таблицу со документами, а потом уже отдавать на обработку программы. В итоге было определена следующая структура:

![penalty_block_schema](https://github.com/garick161/penalty_calculator/assets/114688542/ae269876-9149-4cdb-b1bb-c00e373dbb10)








