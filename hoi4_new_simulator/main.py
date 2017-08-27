# =====================================================
# универсальный симулятор строительства в HOI4 
# (Python 3.x + matplotlib) 
# =====================================================
# repl.it:
    # - https://repl.it/KMF4/162
    # - https://repl.it/KYaO/154
    # - https://repl.it/K2Jy/0

# источники при составлении:
    # - HOI4, версия: 1.4.x (x=0,1,2)
    # - http://www.hoi4wiki.com
# =====================================================

from simulator import Cell, BuildSimulator, BuildSimMaxMilitary, BuildSimInfrEfficiency

# =====================================================
# ИНФОРМАЦИЯ ДЛЯ ПОЛЬЗОВАТЕЛЯ:
# =====================================================

# BuildSimulator.printout = True # подробная печать событий в приложениях build_sim
# BuildSimulator.printout = False # краткая печать событий (установлена по умолчанию)

# =====================================================

country_list = ['СССР', 'ГЕРМАНИЯ', 'ЯПОНИЯ', 'ИТАЛИЯ', 'ФРАНЦИЯ', 'США', 'ВБ']

# =====================================================
# TEST CASES:
# =====================================================

def example_0():
    pass

def example_1():
    ussr_sim = BuildSimMaxMilitary('СССР')
    
    civ_num_to_build_list = [0, 10, 20, 30] # список количества фабрик для постройки
    
    infr_av = 6 # средняя инфраструктура
    civ_trade_av = 10 # среднее количество фабрик от торговли
    date_end = (1941,1,1)
    
    laws_timeline = [ # формат laws_timeline для определенной страны - из country_list - см *замечание
                      [(1936, 3, 11), ['Свободная_торговля']], 
                      [(1936, 6, 27), ['Строительство_1']], 
                      [(1937, 4, 22), ['Строительство_2']], 
                      [(1937, 12, 1), ['Военная_экономика']],
                      [(1939, 4, 15), ['Строительство_3']] 
                    ]
    
    ussr_sim.visualize_efficiency(civ_num_to_build_list, infr_av, laws_timeline, civ_trade_av, date_end)

def example_2():
    ussr_sim = BuildSimMaxMilitary('СССР')

    infr_av = 6 # средняя инфраструктура
    civ_trade_av = 10 # среднее количество фабрик от торговли
    date_end = (1941,1,1)
    
    laws_timeline = [ # формат laws_timeline для определенной страны - из country_list - см *замечание
                      [(1936, 3, 11), ['Свободная_торговля']], 
                      [(1936, 6, 27), ['Строительство_1']], 
                      [(1937, 4, 22), ['Строительство_2']], 
                      [(1937, 12, 1), ['Военная_экономика']],
                      [(1939, 4, 15), ['Строительство_3']] 
                    ]
    
    ussr_sim.find_mil_extremum(infr_av, laws_timeline, civ_trade_av, date_end)

def example_3():
    ger_sim = BuildSimInfrEfficiency('ГЕРМАНИЯ')

    infr_up = 1 # поднятие уровня инфраструктуры, относительно которого оцениваем окупаемость
    civ_trade_av = 5 # среднее количество фабрик от торговли
    
    laws_timeline = [ # формат laws_timeline для определенной страны - из country_list - см *замечание
                      [(1936, 3, 11), ['Свободная_торговля']], 
                      [(1936, 6, 27), ['Строительство_1']], 
                      [(1937, 4, 22), ['Строительство_2']], 
                      [(1937, 12, 1), ['Военная_экономика']],
                      [(1939, 4, 15), ['Строительство_3']] 
                    ]
    
    ger_sim.visualize_equilibrium(infr_up, laws_timeline, civ_trade_av)

def example_4():
    
    new_sim = BuildSimInfrEfficiency()
    new_cell = Cell('Мозель', infrastructure=7, obj_available=11, country='ГЕРМАНИЯ')
    infr_up = 1 # поднятие уровня инфраструктуры, относительно которого оцениваем окупаемость
    civ_trade_av = 5 # среднее количество фабрик от торговли
    
    laws_timeline = [ # формат laws_timeline для неопределенной страны - см *замечание
                      [(1936, 1, 1), ['Ограниченный_призыв', 'Ограниченный_экспорт', 'Частичная_мобилизация']],
                      [(1936, 3, 11), ['Свободная_торговля']], 
                      [(1936, 6, 27), ['Строительство_1']], 
                      [(1937, 4, 22), ['Строительство_2']], 
                      [(1937, 12, 1), ['Военная_экономика']],
                      [(1939, 4, 15), ['Строительство_3']] 
                    ]
    
    new_sim.is_cell_profitable(new_cell, infr_up, laws_timeline, civ_trade_av)  

def example_5():

    ger_sim = BuildSimInfrEfficiency('ГЕРМАНИЯ')
    
    infr_up = 1 # поднятие уровня инфраструктуры, относительно которого оцениваем окупаемость
    civ_trade_av = 5 # среднее количество фабрик от торговли
    
    laws_timeline = [ # формат laws_timeline для определенной страны - из country_list - см *замечание
                      [(1936, 3, 11), ['Свободная_торговля']], 
                      [(1936, 6, 27), ['Строительство_1']], 
                      [(1937, 4, 22), ['Строительство_2']], 
                      [(1937, 12, 1), ['Военная_экономика']],
                      [(1939, 4, 15), ['Строительство_3']] 
                    ]
    
    ger_sim.is_any_cell_profitable(infr_up, laws_timeline, civ_trade_av)

def example_6():
    
    BuildSimulator.printout = True
    
    ussr_sim = BuildSimulator('СССР')
    
    civ_trade_av = 10
    laws_timeline = [ # формат laws_timeline для определенной страны - из country_list - см *замечание
                      [(1936, 3, 11), ['Свободная_торговля']], 
                      [(1936, 6, 27), ['Строительство_1']], 
                      [(1937, 4, 22), ['Строительство_2']], 
                      [(1937, 12, 1), ['Военная_экономика']],
                      [(1939, 4, 15), ['Строительство_3']] 
                    ]
    
    build_order = [['Москва', 'infr', 2], ['Харьков', 'civ', 3], ['Винтерфелл', 'mil', 4]] 
    
    ussr_sim.build_sim(build_order, laws_timeline, civ_trade_av)

example_6()




