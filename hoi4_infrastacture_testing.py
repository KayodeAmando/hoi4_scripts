# тест промышленной эффективности строительства инфраструктуры в HOI4
# =====================================================
# замечания:
    # - рассматривается строительство в 2х изначально одинаковых ячейках - с индексами 0 и 1:
    #     - ячейка 0 - строим некоторое количество инфраструктуры, затем фабрики
    #     - ячейка 1 - сразу строим фабрики 
    # 
    # - для простоты предполагается: 
    #     - изначально в наличии имеется 15 фабрик, т.е. стройка идет на полной производственной мощности
    #     - на протяжении всего времени строительства штрафы/бонусы строительства не изменяются
    # 
    # - в скрипте используются ключи и префиксы:
    #     - 'fact' - от 'factory' (гражданская фабрика)
    #     - 'infr' - от 'infrastructure' (инфраструктура)
    #
# =====================================================
import matplotlib.pyplot as plt

# =====================================================
# константы:

COST_DICT = {'fact':10800, 'infr':3000}

# 'title':[infr_modificator, fact_modificator]
BUILD_MODIFICATORS = {'Обезоруженная_нация':[0, 0],
                      'Только_добровольцы':[0, 0],
                      'Ограниченный_призыв':[0, 0],
                      'Расширенный_призыв':[0, 0],
                      'Обязательная_служба':[-0.1, -0.1],
                      'Все_взрослые':[-0.3, -0.3],
                      'Всех_под_ружье':[-0.4, -0.4],
                      'Свободная_торговля':[0.15, 0.15],
                      'Приоритет_экспорт':[0.1, 0.1],
                      'Ограниченный_экспорт':[0.05, 0.05],
                      'Закрытая_экономика':[0, 0],
                      'Ненарушаемая_изоляция':[0, -0.5],
                      'Изоляция':[0, -0.4],
                      'Гражданская_экономика':[0, -0.3],
                      'Ранняя_мобилизация':[0, -0.1],
                      'Частичная_мобилизация':[0, 0],
                      'Военная_экономика':[0, 0],
                      'Всеобщая_мобилизация':[0, 0],
                      'Строительство_1':[0.1, 0.1],
                      'Строительство_2':[0.2, 0.2],
                      'Строительство_3':[0.3, 0.3],
                      'Строительство_4':[0.4, 0.4],
                      'Строительство_5':[0.5, 0.5],
                      'Капитан_индустрии':[0.1, 0.1],
                      'Новый_курс_(США)':[0.2,0]
                     }

LAW_LIST_START_SOV = ['Только_добровольцы', 'Приоритет_экспорт', 'Гражданская_экономика' ]
LAW_LIST_START_GER = ['Ограниченный_призыв', 'Ограниченный_экспорт', 'Частичная_мобилизация']
LAW_LIST_START_USA = ['Обезоруженная_нация', 'Свободная_торговля', 'Ненарушаемая_изоляция']

# =====================================================
# вспомогательные функции для equilibrium:

def initial_values():

    progress_cell = [0, 0] # количество очков строительства в ячейке
    progress_per_day = {'infr':[0], 'fact':[0, 0]} # изменение количества очков строительства в ячейке в зависимости от объекта
    built_num = {'infr':[0], 'fact':[0, 0]} # количество построенных в ячейках объктов

    day = 0

    return progress_cell, progress_per_day, built_num, day

def get_speed_bonuses(law_list):

    infr_speed_bonus, fact_speed_bonus = 1, 1

    for law in law_list:
        infr_speed_bonus += BUILD_MODIFICATORS[law][0]
        fact_speed_bonus += BUILD_MODIFICATORS[law][1]

    return infr_speed_bonus, fact_speed_bonus  

def get_fact_progress_per_day(infr_initial, fact_speed_bonus):

    infr_level = infr_initial + built_num['infr'][0]
    infr_bonus = (10 + infr_level) / 10
    
    fact_progress_per_day = 15 * 5 * fact_speed_bonus * infr_bonus

    return fact_progress_per_day 

def check_object_completed(cell_num, object_type, printout):

    progress_cell[cell_num] += progress_per_day[object_type][cell_num]

    if progress_cell[cell_num] >= COST_DICT[object_type]:

        progress_cell[cell_num] = 0
        built_num[object_type][cell_num] += 1

        if printout:
            print('Object "%s" #%i is completed in cell %i, day = %i' %(object_type, built_num[object_type][cell_num], cell_num, day))

# =====================================================
def equilibrium(infr_initial, infr_plan_num=1, law_list=[], quit_condition=1, printout=False):

    # --------------------------------------------
    # симуляция строительства в 2х ячейках с изначально одинаковой инфраструктурой = infr_initial:
        # - ячейка 0 - строим infr_plan_num количество инфраструктуры, затем фабрики
        # - ячейка 1 - сразу строим фабрики
    # --------------------------------------------
    # law_list определяет infr_speed_bonus и fact_speed_bonus - бонусы/штрафы строительства для инфраструктуры и фабрик соответственно; 
    # эти бонусы зависят от текущих законов, технологий итд; 
    # в law_list должны быть ключи словаря BUILD_MODIFICATORS; 
    # например, при law_list = ['Гражданская_экономика', 'Приоритет_экспорт', 'Капитан_индустрии']:
        # - infr_speed_bonus -> 1 + (0 + 0.1 + 0.1) = 1.2
        # - fact_speed_bonus -> 1 + (-0.3 + 0.1 + 0.1) = 0.9 
    # --------------------------------------------
    # условия выхода из цикла:
        # - quit_condition = 1 - в ячейке с поднятой инфраструктурой на 1 фабрику больше
        # - quit_condition = 2 - в ячейке с поднятой инфраструктурой на 1 фабрико-день больше
    # --------------------------------------------

    # начальные условия:

    global progress_cell
    global progress_per_day
    global built_num
    global day

    progress_cell, progress_per_day, built_num, day = initial_values()

    infr_speed_bonus, fact_speed_bonus = get_speed_bonuses(law_list)

    progress_per_day['infr'][0] = 15 * 5 * infr_speed_bonus
    progress_per_day['fact'][1] = get_fact_progress_per_day(infr_initial, fact_speed_bonus)
    # --------------------------------------------

    # переменные, используемые для выхода из цикла:

    fact_diff_num = 0 # разница количества построенных фабрик в ячейках
    fact_days_lost = 0 # количество потерянных фабрико-дней в 0й ячейке
    # --------------------------------------------

    if printout:
        print('Initial infrastructure: %i' %infr_initial)
        print('=============================\nSTART SIMULATION...\n-----------------------------')

    while True:

        day += 1

        # --------------------------------------------
        # cell 0 building

        if built_num['infr'][0] < infr_plan_num:
            check_object_completed(0, 'infr', printout)

            if built_num['infr'][0] == infr_plan_num:
                progress_per_day['fact'][0] = get_fact_progress_per_day(infr_initial, fact_speed_bonus)
                
        else:
            check_object_completed(0, 'fact', printout)
                
        # --------------------------------------------
        # cell 1 building

        check_object_completed(1, 'fact', printout)

        # --------------------------------------------
        # exit from the loop

        fact_diff_num = built_num['fact'][1] - built_num['fact'][0] # не обязательно проверять каждый день, но так нагляднее
        fact_days_lost += fact_diff_num
        
        quit_trigger_1 = quit_condition == 1 and fact_diff_num < 0
        quit_trigger_2 = quit_condition == 2 and fact_days_lost < 0

        if quit_trigger_1 or quit_trigger_2:
            if printout: print('-----------------------------\nDONE!\n=============================')
            break

        # --------------------------------------------

    return (built_num['fact'][0], day, fact_days_lost)

def show_plot(infr_plan_num=1, law_list=[], quit_condition=1):

    # --------------------------------------------
    # 2 графика окупаемости строительства инфраструктуры: 
        # - количество фабрик, 
        # - количество дней строительства,
    # необходимых для окупаемости строительства инфраструктуры при данных параметрах, 
    # и в зависимости от начального уровня инфраструктуры
    # --------------------------------------------

    infr_speed_bonus, fact_speed_bonus = get_speed_bonuses(law_list)

    # --------------------------------------------
    color_list = ['b', 'r']
    x_label = 'Initial infrastructure level'
    y_label_list = ['Factories to payback', 'Days to payback']
    # title_list = [',\n'.join(law_list), 'infr_speed_bonus=%.2f, fact_speed_bonus=%.2f,\n infr_plan_num=%i, quit_condition=%i' %(infr_speed_bonus, fact_speed_bonus, infr_plan_num, quit_condition)]
    title_list = ['infr_speed_bonus=%.2f, fact_speed_bonus=%.2f,\n infr_plan_num=%i, quit_condition=%i' %(infr_speed_bonus, fact_speed_bonus, infr_plan_num, quit_condition), '']
    # --------------------------------------------

    fig, ax = plt.subplots(nrows=1, ncols=2)
    fig.set_size_inches(10, 5)
    fig.canvas.set_window_title('HOI4 Infrastructure Efficiency')

    for idx, row in enumerate(ax):
        infr_init_levels = list(range(0, 11 - infr_plan_num)) # начальный уровень + планируемая застройка не может превышать 10 
        x_coord, y_coord = [infr_init_levels, [equilibrium(infr_level, infr_plan_num, law_list, quit_condition)[idx] for infr_level in infr_init_levels]]
        row.plot(x_coord, y_coord, color_list[idx])
        row.set_xlabel(x_label)
        row.set_ylabel(y_label_list[idx])
        row.set_title(title_list[idx])

    plt.show()

# =====================================================
def testing():

    infr_initial, infr_plan_num = 5, 1
    # law_list = LAW_LIST_START_GER
    # law_list = LAW_LIST_START_SOV
    law_list = LAW_LIST_START_USA
    quit_condition = 2

    equilibrium(infr_initial, infr_plan_num, law_list, quit_condition, printout=True)

    show_plot(infr_plan_num, law_list, quit_condition)

testing()

# =====================================================



