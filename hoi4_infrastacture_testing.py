# симулятор строительства в HOI4 - промышленная эффективность инфраструктуры
# =====================================================
# схема симуляции:

#     - сравнение строительства в 2х ячейках с изначально одинаковой инфраструктурой:
#         - ячейка 0 - строим некоторое количество инфраструктуры, затем фабрики
#         - ячейка 1 - сразу строим фабрики 

#     - для простоты предполагается: 
#         - изначально в наличии имеется 15 фабрик, т.е. стройка идет на полной производственной мощности

#     - модификаторы строительства и ТНП динамически изменяются в процессе симуляции и настраиваются пользователем

#     - выход из симуляции происходит по достижении "точки равновесия", определенной следующим образом:
#         - точка равновесия - день симуляции, когда количество фабрико-дней для фабрик, полученных от строительства в ячейке 0, 
#         станет выше аналогичного показателя в ячейке 1; при расчете количества полученных фабрик учитывается фактор ТНП
# -----------------------------------------------------
# функционал для клиента:

#     - equilibrium() - непосредственно симуляция по описанной выше схеме - с подробной или краткой печатью ключевых событий
#     - show_plot() - 2 графика в зависимости от изначального уровня инфраструктуры в ячейках:
#         - "точки равновесия" по описанной выше схеме
#         - фабрики, построенных в ячейке 0 в момент "точки равновесия" 
# -----------------------------------------------------
# источники при составлении:

#     - HOI4, версия: 1.4.0
#     - http://www.hoi4wiki.com
# =====================================================

import matplotlib.pyplot as plt
import math
import itertools
from datetime import datetime, timedelta

# =====================================================
# CONSTANTS:
# =====================================================

# COST_DICT - стоимость постройки объектов 
COST_DICT = {'fact':10800, 'infr':3000}

# GAME_START - дата старта игры, формат (год, месяц, день)
# замечание: дата взята таким образом, чтобы, исходя из формулы: текущий день = текущая дата - GAME_START, (1936,12,31) было 1м днем, а не 0м
# это позволяет быть последовательным 
GAME_START = datetime(1935,12,31)

# -----------------------------------------------------
# LAWS MODIFICATORS BLOCK: 
# -----------------------------------------------------

# BUILD_MODIFICATORS - модификаторы строительства инфраструктуры и фабрик в зависимости от законов, технолоний и советников;
# наполнение BUILD_MODIFICATORS - 'title':[infr_modificator, fact_modificator, 'tag']

# замечание: в словаре действующих модификаторов laws_current в любой момент симуляции в каждом из его ключей вида 'tag' 
# может быть не более одного значения вида 'title', притом имеющего данный 'tag' в BUILD_MODIFICATORS
# tag_list = ['law1', 'law2', 'law3', 'tech', 'capt']

BUILD_MODIFICATORS = { 
                       'Обезоруженная_нация':[0, 0, 'law1'],
                       'Только_добровольцы':[0, 0, 'law1'],
                       'Ограниченный_призыв':[0, 0, 'law1'],
                       'Расширенный_призыв':[0, 0, 'law1'],
                       'Обязательная_служба':[-0.1, -0.1, 'law1'],
                       'Все_взрослые':[-0.3, -0.3, 'law1'],
                       'Всех_под_ружье':[-0.4, -0.4, 'law1'],                      

                      'Свободная_торговля':[0.15, 0.15, 'law2'],
                      'Приоритет_экспорт':[0.1, 0.1, 'law2'],
                      'Ограниченный_экспорт':[0.05, 0.05, 'law2'],
                      'Закрытая_экономика':[0, 0, 'law2'],

                      'Ненарушаемая_изоляция':[0, -0.5, 'law3'],
                      'Изоляция':[0, -0.4, 'law3'],
                      'Гражданская_экономика':[0, -0.3, 'law3'],
                      'Ранняя_мобилизация':[0, -0.1, 'law3'],
                      'Частичная_мобилизация':[0, 0.1, 'law3'],
                      'Военная_экономика':[0, 0.2, 'law3'],
                      'Всеобщая_мобилизация':[0, 0.3, 'law3'],

                      'Строительство_1':[0.1, 0.1, 'tech'],
                      'Строительство_2':[0.2, 0.2, 'tech'],
                      'Строительство_3':[0.3, 0.3, 'tech'],
                      'Строительство_4':[0.4, 0.4, 'tech'],
                      'Строительство_5':[0.5, 0.5, 'tech'],

                      'Капитан_индустрии':[0.1, 0.1, 'capt'],
                      'Капитан_индустрии_уволен':[0, 0, 'capt'],

                      # замечание: для добавления новых модификаторов, можно использовать произвольный tag из незанятых, например:
                      # 'Новый_курс_США':[0.2,0, 'new_tag'] 
                      # 'Новый_курс_США_убран':[0,0, 'new_tag'] 

                     }  

# CONS_GOODS_MODIFICATORS - штраф ТНП в зависимости от закона;
# наполнение CONS_GOODS_MODIFICATORS - 'title':cons_goods_penalty

CONS_GOODS_MODIFICATORS = { 
                           'Ненарушаемая_изоляция':0.4,
                           'Изоляция':0.35,
                           'Гражданская_экономика':0.3,
                           'Ранняя_мобилизация':0.25,
                           'Частичная_мобилизация':0.2,
                           'Военная_экономика':0.15,
                           'Всеобщая_мобилизация':0.1
                          }

# =====================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ч1:
# (работа с глобальными переменными)
# =====================================================

# -----------------------------------------------------
# дополнительные глобальные переменные:
# - obj_built - актуальное количество построенных в симуляции объектов 
# - fact_diff_sum - актуальное состояние разницы фабрико-дней относительно ячейки с поднятой инфраструктурой
# - laws_current - актуальный набор законов и модификаторов строительства
# - laws_timeline_copy - deep-копия laws_timeline, актуальное состояние очереди законов на изменение 

# замечание: переменная laws_timeline_copy введена на случай многократной симуляции, 
# в противном случае можно было бы обойтись непосредственно laws_timeline 
# -----------------------------------------------------

def reset_to_start_conditions():
    # вводим дополнительные глобальные переменные и определяем их начальные значения 
    
    reset_obj_built()
    reset_fact_diff_sum()
    reset_laws_timeline()
    reset_laws_current()

def reset_obj_built():
    global obj_built 
    obj_built = {'infr':[0, 0], 'fact':[0, 0]} # здесь и далее: ключи = 'infr', 'fact' соответствуют:
                                               # 'fact' - от 'factory' (гражданская фабрика)
                                               # 'infr' - от 'infrastructure' (инфраструктура)

    # замечание: 
    # индекс значений словаря obj_built соответствует индексу ячейки;
    # тк по схеме строительство инфраструктуры ведется только в ячейке 0, достаточно было использовать: 
    # obj_built = {'infr':[0], 'fact':[0, 0]}, но 2 индекса в 'infr' делают printout более наглядным

def reset_fact_diff_sum():
    global fact_diff_sum
    fact_diff_sum = {'total': 0, 'actual_fact_diff': 0} # ключи = 'total', 'actual_fact_diff' соответствуют следующим значениям: 
                                                        # сумма потерянных фабрико-дней, актуальная разница доступных фабрик из построенных в ячейках (с учетом ТНП)

def reset_laws_current():
    global laws_current 
    laws_current = {}

def reset_laws_timeline():
    global laws_timeline_copy 
    laws_timeline_copy = laws_timeline[:][:] 

# -----------------------------------------------------

def change_fact_diff():
    # функция изменяет 'actual_fact_diff' часть словаря fact_diff_sum
    # функция используется при постройке фабрики, а также при изменении закона, если закон - среди ключей CONS_GOODS_MODIFICATORS

    fact_available = get_fact_available()
    fact_diff_sum['actual_fact_diff'] = fact_available[1] - fact_available[0] 

    # замечание:
    # fact_diff_sum - трек потерянных фабрико-дней - словарь с 2мя ключами = 'total', 'actual_fact_diff' 
    # 'total' часть пересчитывается на основе 'actual_fact_diff' каждый день в основном цикле equilibrium() и является триггером выхода из цикла;


def change_laws_current():
    # функция изменяет действующий набор законов laws_current
    # соответственно, функция используется в дни изменения законов

    if printout: 
        return_str = ''

    is_cons_goods_law = False # флаг - есть ли среди законов закон на изменение ТНП, т.е - закон среди ключей CONS_GOODS_MODIFICATORS
    laws_to_change = laws_timeline_copy[0][1]
    
    for law in laws_to_change:

        tag = BUILD_MODIFICATORS[law][-1]

        if law in CONS_GOODS_MODIFICATORS:
            is_cons_goods_law = True

        # -----------------------------------------------------
        if printout:
            law_old = laws_current.get(tag, 'None (1st change)')
            return_str += 'Law was changed: %s -> %s\n' %(law_old, law)
        # -----------------------------------------------------

        laws_current[tag] = law

    laws_timeline_copy.pop(0) # замечание: такой подход позволяет легко получать актуальный day_to_change_law - как laws_timeline_copy[0][0]

    if is_cons_goods_law:
        change_fact_diff()

    if printout: 
        return return_str.rstrip()

# =====================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ч2: 
# (~независимые функции - get-функции без параметров)
# =====================================================

def get_day_to_change_law(): # замечание: однозначно определяется из laws_timeline_copy => из глобальных переменных
    # day_to_change_law - ближайший из дней изменения закона
    # day_to_change_law изменяется на старте, а также при изменении закона

    if len(laws_timeline_copy):
        day_to_change_law_datetime = laws_timeline_copy[0][0]
        day_to_change_law = (day_to_change_law_datetime - GAME_START).days
    else:
        day_to_change_law = -1
    return day_to_change_law

# -----------------------------------------------------

def get_cons_goods_penalty(): # замечание: однозначно определяется из laws_current и CONS_GOODS_MODIFICATORS => из глобальных переменных
    # cons_goods_penalty - штраф ТНП
    # cons_goods_penalty изменяется при изменении закона, если закон - среди ключей CONS_GOODS_MODIFICATORS
    # функция используется как вспомогательная функция для get_fact_available()

    cons_goods_law = laws_current['law3'] # замечание: законы, влияющие на ТНП, собраны в BUILD_MODIFICATORS и => в laws_current под тегом 'law3'
    cons_goods_penalty =  CONS_GOODS_MODIFICATORS[cons_goods_law]

    return cons_goods_penalty

def get_fact_available(): # замечание: однозначно определяется из obj_built и get_cons_goods_penalty() => из глобальных переменных
    # fact_available - доступные из построенных ячейками фабрик - те, которые миновали штраф ТНП
    # fact_available изменяется при постройке фабрики, а также при изменений закона, если закон - среди ключей CONS_GOODS_MODIFICATORS
    # функция используется как вспомогательная функция для change_fact_diff()

    fact_built_list = obj_built['fact']
    cons_goods_penalty = get_cons_goods_penalty()
    cons_goods_required = [math.ceil(item * cons_goods_penalty) for item in fact_built_list]
    fact_available = [built - required for built, required in zip(fact_built_list, cons_goods_required)]
        
    return fact_available 

# -----------------------------------------------------

def get_build_bonus(): # замечание: однозначно определяется из laws_current и BUILD_MODIFICATORS => из глобальных переменных
    # build_bonus - бонус скорости строительства, зависящий от законов, технологий и советников
    # build_bonus изменяется при переключении с инфраструктуры на фабрики в ячейке 0, а также при изменении закона
    # функция используется как вспомогательная функция для get_progress_per_day()

    build_bonus = {'infr':1, 'fact':1}
    for key, value in laws_current.items():
        build_bonus['infr'] += BUILD_MODIFICATORS[value][0]
        build_bonus['fact'] += BUILD_MODIFICATORS[value][1]

    for key in build_bonus: 
        build_bonus[key] = round(build_bonus[key], 2) 

    return build_bonus

# =====================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ч3: 
# (~внутренние функции - функции с параметрами из equilibrium())
# =====================================================

def is_infr_completed(infr_plus_num):
    return obj_built['infr'][0] == infr_plus_num # достроили ли инфраструктуру в ячейке 0

def get_progress_per_day(infr_initial, infr_plus_num): 
    # progress_per_day - актуальное изменение прогресса строительтва в ячейках за день
    # progress_per_day изменяется при переключении строительства с инфраструктуры на фабрики в ячейке 0, а также при изменении закона

    build_bonus = get_build_bonus()
    infr_speed_bonus = build_bonus['infr'] 
    fact_speed_bonus = build_bonus['fact']

    infr_max = [infr_initial + infr_plus_num, infr_initial]
    infr_bonus = [(10 + infr_max_cell) / 10 for infr_max_cell in infr_max] # бонус от инфраструктуры ячеек при строительстве фабрик

    progress_per_day = [15 * 5 * fact_speed_bonus * infr_bonus_cell for infr_bonus_cell in infr_bonus]
    if not is_infr_completed(infr_plus_num):
        progress_per_day[0] = 15 * 5 * infr_speed_bonus

    return progress_per_day

def check_object_completed(progress, cell_num, obj_type):
    # проверка - завершено ли строительство объекта obj_type в ячейке номер cell_num
    # в зависимости от progress - актуального прогресса строительства в ячейках

    if progress[cell_num] >= COST_DICT[obj_type]:

        obj_built[obj_type][cell_num] += 1

        if printout:
            return_str = 'Progress in cells: %s' %progress

        # --------------------------------------------
        # как оказалось, при строительтве того же объекта в ячейке,
        # прогресс сверх стоимости объекта перекидывается на новое строительство
        # --------------------------------------------
        progress[cell_num] = progress[cell_num] - COST_DICT[obj_type] 
        # --------------------------------------------
        # --------------------------------------------
            # obj_to_build = build_order.pop(0)
            # if obj_to_build == obj_type:
            #     self.progress[line_idx][1] -= COST_DICT[obj_type]
            # else:
            #     self.progress[line_idx] = [obj_to_build, 0]

            # if obj_type != 'infr':
            #     return self.progress_change_lines_num()
        # --------------------------------------------

        if obj_type == 'fact': 
            change_fact_diff()

        if printout: 
            return_str += '\nObject "%s" #%i is completed in cell %i' %(obj_type, obj_built[obj_type][cell_num], cell_num)
            return return_str

def print_output(return_str, day, progress, progress_per_day):
    # печать параметров симуляции в едином формате 
    # функция используется в день события - при изменении закона или постройке объекта 

    # замечание:
    # преимущества - единообразие печати и легкость форматирования
    # недостаток - делает лишние вызовы функций

    actual_date = (GAME_START + timedelta(days=day+leap_year_count)).date()

    print('Day = %i (%s)' %(day, actual_date))
    print(return_str)
    if return_str.lstrip().startswith('Law'): print('Current laws:', laws_current) # замечание: global // говнокод
    print('Build modificators:', get_build_bonus())
    print('Progress per day:', progress_per_day)
    print('Progress in cells:', progress)
    print('Consumer goods penalty:', get_cons_goods_penalty())
    print('Completed objects:', obj_built) # замечание: global
    print('Completed factories available:', get_fact_available())
    print('Factory-days lost:', fact_diff_sum) # замечание: global
    print()

# =====================================================
# ОСНОВНАЯ ФУНКЦИЯ - СИМУЛЯЦИЯ СТРОИТЕЛЬСТВА:
# =====================================================

# вся цепочка с префиксом 'leap' введена, потому что глупые парадоксы убрали высокосные годы,
# и при этом не хочется убирать datetime
leap_years_list = [1936 + 4*idx for idx in range(4)]
leap_years_dates = [datetime(2016, 2, 29).replace(year=leap_year) for leap_year in leap_years_list]
leap_days_from_start = [(leap_date - GAME_START).days for leap_date in leap_years_dates]
# print(leap_days_from_start)


def equilibrium(infr_initial, infr_plus_num=1):
    # симуляция строительства согласно описанию в шапке файла
    # infr_initial - начальный уровень инфраструктуры в ячейках
    # infr_plus_num - количество уровней инфраструктуры, которые будут построены в ячейке 0

    # 0 <= infr_initial, infr_plus_num <= 10 
    # infr_initial + infr_plus_num <= 10
    
    # --------------------------------------------
    # начальные условия:
    # --------------------------------------------

    reset_to_start_conditions()

    progress = [0, 0] # прогресс строительства в ячейках
    progress_per_day = get_progress_per_day(infr_initial, infr_plus_num) # изменение прогресса строительтва в ячейках в день
    day_to_change_law = get_day_to_change_law() # ближайший день изменения закона

    # --------------------------------------------
    if printout: print('=============================')
    print('Infrastructure initial:', infr_initial)
    print('Infrastructure num to build in cell_0:', infr_plus_num)
    if printout: print('=============================\nSTART SIMULATION...\n-----------------------------\n')
    # --------------------------------------------

    global leap_year_count
    leap_year_count = 0 

    for day in itertools.count(1): # замечание: бесконечный range = 1,2,3,... => можно не использовать связку day=0 -> while True -> day+=1

        if day in leap_days_from_start: 
            leap_year_count += 1

        # как было установлено из игрового процесса, бонусы строительства действуют в день изменения закона, 
        # но первый эффект от них - добавление измененного progress_per_day в progress, наступает на следующий день
        # на основе этого использую следующий порядок:
        # чек постройки -> чек изменения закона -> изменение прогресса линий
        # таким образом, измененный progress_per_day добавляется в progress в текущий день,
        # но эффект - построен ди объект (по сути, это единственный индикатор эффекта) - проверяется на следующий день,
        # и, таким образом, мы остаемся в согласии с игровой механикой;
        # если рассматривать стартовый день = 1, то изменение progress последним шагом - вообще единственная опция  

        # --------------------------------------------
        # чек постройки объекта - ячейка 0:
        # --------------------------------------------

        if not is_infr_completed(infr_plus_num):
            return_str = check_object_completed(progress, 0, 'infr')

            if is_infr_completed(infr_plus_num): # момент, когда достроили инфраструктуру в ячейке 0
                progress_per_day = get_progress_per_day(infr_initial, infr_plus_num)
                progress[0] = 0 # => переключение и разница не сохраняется
                
        else:
            return_str = check_object_completed(progress, 0, 'fact')

        if return_str and printout:
            print_output(return_str, day, progress, progress_per_day)

        # --------------------------------------------
        # чек постройки объекта - ячейка 1:
        # --------------------------------------------

        return_str = check_object_completed(progress, 1, 'fact')
        if return_str and printout:
            print_output(return_str, day, progress, progress_per_day)

        # --------------------------------------------
        # чек изменения закона:
        # --------------------------------------------

        if day == day_to_change_law - leap_year_count:

            return_str = change_laws_current() 
            day_to_change_law = get_day_to_change_law() # ближайший день изменения закона
            progress_per_day = get_progress_per_day(infr_initial, infr_plus_num)

            if printout: 
                print_output(return_str, day, progress, progress_per_day)

        # --------------------------------------------
        # изменение прогресса ячеек:
        # --------------------------------------------
        
        for cell_num, day_progress in enumerate(progress_per_day):
            progress[cell_num] += day_progress

        # --------------------------------------------
        # выход из цикла:
        # --------------------------------------------

        fact_diff_sum['total'] += fact_diff_sum['actual_fact_diff'] 
        quit_trigger = fact_diff_sum['total'] < 0

        if quit_trigger: 

            if printout: 
                print_output('(final day)', day, progress, progress_per_day)
                print('-----------------------------\nDONE!\n=============================\n')
            else:
                print('\nEquilibrium: day =', day)
                print('Objects were built =', obj_built)
                print('=============================')
            break

        if day == 3000: # замечание: защита от бесконечного цикла
            print('Day =', day)
            print("It looks like there's smth wrong with your simulation ... I'm quit\n")
            break

        # --------------------------------------------

    return (day, obj_built['fact'][0]) # замечание: нужно только для графика

def show_plot(infr_plus_num=1):
    # 2 графика окупаемости строительства инфраструктуры согласно описанию в шапке файла
    # infr_plus_num - количество уровней инфраструктуры, которые будут построены в ячейке 0
    # 0 <= infr_plus_num <= 10

    # --------------------------------------------
    # элементы оформления графика:
    # --------------------------------------------
    x_label = 'Initial infrastructure level'
    y_label_list = ['Days to payback', 'Factories to payback']
    title_list = ['infr_plus_num=%i' %(infr_plus_num), '']
    color_list = ['b', 'r']
    # --------------------------------------------

    fig, ax = plt.subplots(nrows=1, ncols=2)
    fig.set_size_inches(10, 5) # замечание: опционально под параметры монитора
    fig.canvas.set_window_title('HOI4 Infrastructure Efficiency')

    for idx, row in enumerate(ax):
        infr_init_levels = list(range(0, 11 - infr_plus_num)) # замечание: берем такой range, тк infr_initial + infr_plus_num <= 10
        x_coord, y_coord = [infr_init_levels, [equilibrium(infr_level, infr_plus_num)[idx] for infr_level in infr_init_levels]]
        row.plot(x_coord, y_coord, color_list[idx])
        row.set_xlabel(x_label)
        row.set_ylabel(y_label_list[idx])
        row.set_title(title_list[idx])

    plt.show()

# =====================================================
# CLIENT:
# =====================================================

# -----------------------------------------------------
# laws_timeline
# наполнение laws_timeline - [day_to_change_law, [law_1, law_2, ...]]
laws_timeline = [
                 [datetime(1936, 1, 1), ['Только_добровольцы', 'Приоритет_экспорт', 'Гражданская_экономика']], 
                 [datetime(1936, 3, 11), ['Свободная_торговля']], 
                 [datetime(1936, 6, 27), ['Строительство_1']], 
                 [datetime(1937, 4, 22), ['Строительство_2']], 
                 # [datetime(1937, 12, 1), ['Военная_экономика']],
                 # [1200, ['Строительство_3']] 
                ]
# -----------------------------------------------------

printout = False # True
printout = True
infr_init, infr_plus = 5, 2 # infr_init + infr_plus <= 10

# -----------------------------------------------------

equilibrium(infr_init, infr_plus)
# show_plot(infr_plus)

# =====================================================


