# -----------------------------------------------------
# мини-модуль под HOI4 - по типу datetime, но без высокосных лет,
# для ~date используется формат (y,m,d) - tuple;

# замечание: можно легко сделать модуль обычным, установив month_days_dict[2] = 29, если год - высокосный 

# замечание: модуль был введен, потому что: 
# - с одной строны, при вводе/выводе данных хочется пользоваться удобством даты в формате ~(y,m,d),
# - а с другой - глупые парадоксы УБРАЛИ ВЫСОКОСНЫЕ ГОДЫ (1936, 1940, ...), 
# и поэтому стандартный datetime не работает (либо нужны лишние танцы с бубном для его допиливания под конкретную ситуацию)
# -----------------------------------------------------

from itertools import chain

month_days_dict = {1:31, 2:28, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}
# -----------------------------------------------------

def get_days_total(date):
    year, month, day = date
    days = 365 * year
    for month in range(1, month):
        days += month_days_dict[month]
    days+= day
    return days

def get_days_diff(date_1, date_2):
    days_1 = get_days_total(date_1)
    days_2 = get_days_total(date_2)
    return days_2 - days_1

def add_days(date, days):
  
    # print(date, days)
    year, month, day = date

    # устанавливаем - какой будет год
    while days > 365:
        days -= 365
        year += 1
    # print(year, month, day, days)
    
    if get_days_total((0, month, day)) + days > 365:
        year += 1
    # print(year, month, day, days)
    
    # остальная часть - дорабатываем месяцы, дни
    month_list = list(chain(range(month, 13), range(1, 13)))  
    # print(month_list)

    for idx, month_temp in enumerate(month_list):

        if days + day > month_days_dict[month_temp]: # => как минимум следующий месяц
            days -= month_days_dict[month_temp]
            # print(month_temp, year, month, day, days, days+day)
        
        else: # => определили месяц, 
              # при этом days может быть отрицательным, но если условия выше хоть раз страбатывали, из них следует: 
              # day > month_days - days => day > - days (обновленного) 
              # => если days - отрицательное, то day > abs(days), и мы никогда не получим в day += days отрицательное значение;
              # если же условие выше не срабатывало, то все элементарно, при этом - выводы те же
            day += days
            month = month_temp
            # print(month_temp, year, month, day, days, days+day)
            break

    return year, month, day 
 
# =====================================================
def testing():
    pass

if __name__ == '__main__':
    testing()
# =====================================================

