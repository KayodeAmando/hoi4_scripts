import matplotlib.pyplot as plt
import math
import itertools
from copy import deepcopy

from datetime_my import get_days_diff, add_days

# -----------------------------------------------------
# блокирование функции печати:
# -----------------------------------------------------

import sys, os

def disable_printout(): # полностью блокирует печать в консоль
    sys.stdout = open(os.devnull, 'w') 

def enable_printout(): # разблокирует печать
    sys.stdout = sys.__stdout__ 

# =====================================================
# КОНСТАНТЫ:

    # здесь и далее: ключи и префиксы = 'infr', 'civ', 'mil' соответствуют:
    # 'infr' - от 'infrastructure' (инфраструктура)
    # 'civ' - от 'civilian factory' (гражданская фабрика)
    # 'mil' - от 'military factory' (военный завод)
# =====================================================

# OBJ_COST - стоимость постройки объектов 
OBJ_COST = {'infr':3000, 'civ':10800, 'mil':7200}

# LAWS_MODIFICATORS - модификаторы скорости строительства и штрафа ТНП в зависимости от законов, технологий и советников
# формат LAWS_MODIFICATORS - law_title:{{модификаторы_строительства}, 'tag':law_tag, 'cons_goods_penalty':штраф_ТНП (опционально)}

LAWS_MODIFICATORS = {

                      'Обезоруженная_нация':{'infr':0, 'civ':0, 'mil':0, 'tag':'army'},  
                      'Только_добровольцы':{'infr':0, 'civ':0, 'mil':0, 'tag':'army'},
                      'Ограниченный_призыв':{'infr':0, 'civ':0, 'mil':0, 'tag':'army'},
                      'Расширенный_призыв':{'infr':0, 'civ':0, 'mil':0, 'tag':'army'},
                      'Обязательная_служба':{'infr':-0.1, 'civ':-0.1, 'mil':-0.1, 'tag':'army'},
                      'Все_взрослые':{'infr':-0.3, 'civ':-0.3, 'mil':-0.3, 'tag':'army'},
                      'Всех_под_ружье':{'infr':-0.4, 'civ':-0.4, 'mil':-0.4, 'tag':'army'},                      

                      'Свободная_торговля':{'infr':0.15, 'civ':0.15, 'mil':0.15, 'tag':'trade'},
                      'Приоритет_экспорт':{'infr':0.1, 'civ':0.1, 'mil':0.1, 'tag':'trade'},
                      'Ограниченный_экспорт':{'infr':0.05, 'civ':0.05, 'mil':0.05, 'tag':'trade'},
                      'Закрытая_экономика':{'infr':0, 'civ':0, 'mil':0, 'tag':'trade'},

                      'Ненарушаемая_изоляция':{'infr':0, 'civ':-0.5, 'mil':-0.5, 'tag':'econ', 'cons_goods_penalty':0.4},
                      'Изоляция':{'infr':0, 'civ':-0.4, 'mil':-0.4, 'tag':'econ', 'cons_goods_penalty':0.35},
                      'Гражданская_экономика':{'infr':0, 'civ':-0.3, 'mil':-0.3, 'tag':'econ', 'cons_goods_penalty':0.3},
                      'Ранняя_мобилизация':{'infr':0, 'civ':-0.1, 'mil':-0.1, 'tag':'econ', 'cons_goods_penalty':0.25},
                      'Частичная_мобилизация':{'infr':0, 'civ':0, 'mil':0.1, 'tag':'econ', 'cons_goods_penalty':0.2},
                      'Военная_экономика':{'infr':0, 'civ':0, 'mil':0.2, 'tag':'econ', 'cons_goods_penalty':0.15},
                      'Всеобщая_мобилизация':{'infr':0, 'civ':0, 'mil':0.3, 'tag':'econ', 'cons_goods_penalty':0.1},

                      'Строительство_1':{'infr':0.1, 'civ':0.1, 'mil':0.1, 'tag':'tech'},
                      'Строительство_2':{'infr':0.2, 'civ':0.2, 'mil':0.2, 'tag':'tech'},
                      'Строительство_3':{'infr':0.3, 'civ':0.3, 'mil':0.3, 'tag':'tech'},
                      'Строительство_4':{'infr':0.4, 'civ':0.4, 'mil':0.4, 'tag':'tech'},
                      'Строительство_5':{'infr':0.5, 'civ':0.5, 'mil':0.5, 'tag':'tech'},

                      'Капитан_индустрии':{'infr':0.1, 'civ':0.1, 'mil':0, 'tag':'civ_adv'},
                      'Капитан_индустрии_уволен':{'infr':0, 'civ':0, 'mil':0, 'tag':'civ_adv'},

                      'Военный_магнат':{'infr':0, 'civ':0, 'mil':0.1, 'tag':'mil_adv'},
                      'Военный_магнат_уволен':{'infr':0, 'civ':0, 'mil':0, 'tag':'mil_adv'},

                      # замечание: 
                      # для добавления новых модификаторов можно использовать произвольные law_title и law_tag из незанятых, например:
                      
                      # 'Новый_курс_США':{'infr':0.2, 'civ':0, 'mil':0, 'tag':'new_tag'},
                      # 'Новый_курс_США_убран':{'infr':0, 'civ':0, 'mil':0, 'tag':'new_tag'}, 

                     }  

# CONDITIONS_START - стартовые характеристики стран: фабрики, заводы и набор законов 
# формат CONDITIONS_START - country_tag:{'obj_start':{количество_фабрик_и_заводов_на_старте}}, 'laws_start':{набор_законов_на_старте}
# доступные страны: 'СССР', 'ГЕРМАНИЯ', 'ЯПОНИЯ', 'ИТАЛИЯ', 'ФРАНЦИЯ', 'США', 'ВБ'

CONDITIONS_START = {
  
                     'СССР':{'obj_start':{'civ':42, 'mil':36}, 'laws_start':[[(1936, 1, 1), ['Только_добровольцы', 'Приоритет_экспорт', 'Гражданская_экономика']]]},
                     'ГЕРМАНИЯ':{'obj_start':{'civ':31, 'mil':40}, 'laws_start':[[(1936, 1, 1), ['Ограниченный_призыв', 'Ограниченный_экспорт', 'Частичная_мобилизация']]]},
                     'ИТАЛИЯ':{'obj_start':{'civ':20, 'mil':19}, 'laws_start':[[(1936, 1, 1), ['Ограниченный_призыв', 'Ограниченный_экспорт', 'Частичная_мобилизация']]]},
                     'ЯПОНИЯ':{'obj_start':{'civ':23, 'mil':20}, 'laws_start':[[(1936, 1, 1), ['Ограниченный_призыв', 'Ограниченный_экспорт', 'Частичная_мобилизация']]]},
                     'ФРАНЦИЯ':{'obj_start':{'civ':35, 'mil':6}, 'laws_start':[[(1936, 1, 1), ['Ограниченный_призыв', 'Приоритет_экспорт', 'Гражданская_экономика']]]},
                     'США':{'obj_start':{'civ':128, 'mil':10}, 'laws_start':[[(1936, 1, 1), ['Обезоруженная_нация', 'Свободная_торговля', 'Ненарушаемая_изоляция']]]},
                     'ВБ':{'obj_start':{'civ':33, 'mil':14}, 'laws_start':[[(1936, 1, 1), ['Только_добровольцы', 'Приоритет_экспорт', 'Гражданская_экономика']]]},
                    
                     # замечание: 
                     # для добавления новых стран можно использовать произвольный country_tag из незанятых, например:
                    
                     # ...
                
                    }

# CELLS_DICT - словарь с параметрами для ячеек строительства (см класс Cell)
# формат CELLS_DICT - cell_name:[infrastructure, obj_available, country]

CELLS_DICT = {   
                  
               # замечание:
               # количество параметров может быть неполным, но порядок должен быть таким же, как при инициализации ячейки 
               # то есть: [infrastructure, obj_available, country])
              
               'Москва': [8, 5, 'СССР'], 
               'Харьков': [7, 5], 
               'Сталинград': [7], 
               
               # замечание: 
               # для добавления новых ячеек, можно использовать произвольное cell_name из незанятых*, например:
               # (* кроме имен, начинающихся с Cell.GENERIC_NAME_BASE - такие имена отведены под generic-ячейки)
              
               # 'Винтерфелл': [3, 5, 'Королевство_Севера'], # зима близко
               
              }  

# GAME_START - дата, от которой ведется отсчет игрового дня => (1936,1,1) - 1й день игры
# здесь и далее формат даты: (год, месяц, день)
# замечание: 
# такой подход позволяет быть последовательным и точным в операциях с датами на протяжении всей симуляции 
GAME_START = (1935,12,31)

# INFINITE_LOOP_BREAKER - значение по умолчанию для даты, когда симуляция принудительно завершится 
# (если это не произошло ранее)
INFINITE_LOOP_BREAKER = (1945,1,1) 

# COUNTRY_DEFAULT - значение по умолчанию для поля страны экземпляров классов ячейки и симуляции
COUNTRY_DEFAULT = 'Undefined'

# =====================================================
# КЛАССЫ:
# =====================================================

# =====================================================
# класс Cell - ячейки строительства:

    # аргументы для инициализации: (все именованные => имеют значения по умолчанию)
    # - name - имя ячейки (str, не начинается с Cell.GENERIC_NAME_BASE)
    # - infrastructure - инфраструктура ячейки (int от 0 до 10)
    # - obj_available - количество доступных клеток для строительства в ячейке (int >= 0)
    # - country - страна ячейки (str)
# =====================================================

class Cell():

    # -----------------------------------------------------  
    # поля класса: 
    # -----------------------------------------------------
    
    # поле INFRASTR_DEFAULT - служебная константа: 
    # значение по умолчанию для инфраструктуры ячейки 
    INFRASTR_DEFAULT = 5
    
    # поле GENERIC_NAME_BASE - служебная константа: 
    # базовое значение для имени generic-ячейки
    GENERIC_NAME_BASE = 'generic_'
    
    # поле GENERIC_NUMBER - служебная константа: 
    # значение-счетчик для дополнения базовой части имени generic-ячейки => обеспечивает уникальное имя
    GENERIC_NUMBER = 1 
    
    # -----------------------------------------------------
    # инициализация класса:
    # -----------------------------------------------------
    
    def __init__(self, name=None, infrastructure=None, obj_available=sys.maxsize, country=COUNTRY_DEFAULT): 
        # замечание: можно было использовать obj_available=float('inf'), 
        # но ч/з sys.maxsize мы остаемся последовательными, тк всю дорогу int 
        
        # замечание: infrastructure=INFRASTR_DEFAULT не работает, тк default-значения 
        # именованных аргументов определяются 1 раз - в момент определения функции 
        # => при таком подходе не сможем поменять default-значение для infrastructure, что неприемлемо 
        # подробнее здесь:
        # https://stackoverflow.com/questions/5555449/using-self-xxxx-as-default-parameter-python/5555470#5555470

        if name is None:
            self.name = Cell.GENERIC_NAME_BASE + str(Cell.GENERIC_NUMBER) # имя ячейки 
            Cell.GENERIC_NUMBER += 1
        elif isinstance(name, str) and not name.startswith(Cell.GENERIC_NAME_BASE): 
            # замечание: на всякий случай запрещено использовать name, начинающийся с Cell.GENERIC_NAME_BASE 
            self.name = name 
        else:
            raise ValueError("%s - некорректное значение для имени ячейки!" %name)

        if infrastructure is None and Cell.INFRASTR_DEFAULT in range(11):
            self.infrastructure = Cell.INFRASTR_DEFAULT # инфраструктура ячейки
        elif isinstance(infrastructure, int) and infrastructure in range(11): # замечание: 4.0 (=> float) in range(11) => True 
            self.infrastructure = infrastructure
        else:
            raise ValueError("%s - некорректное значение для инфраструктуры ячейки!" %infrastructure)
        
        if isinstance(obj_available, int) and obj_available >= 0:
            self.obj_available = obj_available # количество доступных клеток для строительства в ячейке
        else:
            raise ValueError("%s - некорректное значение для количества доступных клеток строительства!" %obj_available)
        
        if isinstance(country, str):
            self.country = country # страна ячейки
        else:
            raise ValueError("%s - некорректное значение для страны ячейки!" %country)
            
    # -----------------------------------------------------
    # печать и get-методы:
    # -----------------------------------------------------
    
    def __str__(self): 
        
        to_print_tuple = (self.get_name(), self.get_infrastructure(), self.get_obj_available(), self.get_country())
        return 'Name: %s, Infrastructure: %i, Objects available: %.g, Country: %s' %to_print_tuple
        
        # замечание: %.g - general format, подробнее здесь:
        # https://www.python.org/dev/peps/pep-3101/

    def get_name(self):
        return self.name

    def get_infrastructure(self):
        return self.infrastructure

    def get_obj_available(self):
        return self.obj_available
        
    def get_country(self):
        return self.country

    # -----------------------------------------------------
    # изменение полей экземпляра класса:
    # -----------------------------------------------------
    
    def infrastructure_up(self):
        if self.infrastructure < 10:
            self.infrastructure += 1

    def obj_available_down(self):
        if self.obj_available > 0:
            self.obj_available -= 1

# =====================================================
# основной класс BuildSimulator - симулятор строительства:

    # - рассматривается произвольная схема строительства - по заданной очереди строительства
    # - завершение симуляции: 
        # - либо по достижении некоторой даты 
        # - либо, когда все объекты из очереди строительства построены 
        
    # --------------------------------------------
    # - ФУНКЦИОНАЛ ДЛЯ ПОЛЬЗОВАТЕЛЯ:
    # --------------------------------------------
    
        # - симуляция строительства по заданным параметрам: метод build_sim()
        # (с краткой или подробной печатью событий симуляции)

    # --------------------------------------------
    # - параметры приложений симуляции, которые задаются пользователем:
    
        # - для создания класса:
            # - country_start: 
                # - либо тэг игровой страны (доступные тэги: 'СССР', 'ГЕРМАНИЯ', 'ЯПОНИЯ', 'ИТАЛИЯ', 'ФРАНЦИЯ', 'США', 'ВБ')
                # - либо количество гражданских фабрик и военных заводов на старте 
                
        # - для основного метода класса - build_sim():
            # - очередь строительства - build_order 
            # - динамика изменения законов, влияющих на модификаторы строительства и ТНП - laws_timeline (опционально)
            # - средняя разница фабрик от торговли - civ_trade_av (опционально)
            # - дата принудительного завершения симуляции - date_end (опционально)
# =====================================================    

class BuildSimulator():

    # -----------------------------------------------------  
    # поля класса: 
    # -----------------------------------------------------

    # разделители для удобства печати:
    str_1 = '============================================'
    str_2 = '--------------------------------------------'
    
    # переключатель краткой/подробной печати: 
    printout = False
    
    # вариант:
        # поле INFINITE_LOOP_BREAKER - служебная константа: 
        # значение по умолчанию для дня от начала симуляции, когда она принудительно завершится (если это не произошло ранее)
        # INFINITE_LOOP_BREAKER = 365*10
        # INFINITE_LOOP_BREAKER = (1945,1,1) 

    # -----------------------------------------------------
    # инициализация класса и reset-методы:
    # -----------------------------------------------------

    def __init__(self, country_start):

        self.reset() # на всякий случай, хотя - вообще говоря, reset() есть на старте каждой симуляции
        
        if isinstance(country_start, str) and country_start in CONDITIONS_START: # CONDITIONS_START.get(country_start):
            self.country = country_start # страна симуляции
            self.obj_start = CONDITIONS_START[country_start]['obj_start'] # количество гражданских фабрик и военных заводов на старте
        
        elif isinstance(country_start, dict): 
          
            # вариант: 
                # набросок для более тщательной проверки country_start на валидность (можно доделать)
                # for obj in self.obj_built:
                #     num = country_start.get(obj) 
                #     error_condition_1 = num is None and obj != 'infr' # ?? 'infr' не нужно добавлять в country_start
                #     error_condition_2 = not isinstance(num, int) or num < 0
                #     if error_condition_1 or error_condition_2:
                #         raise ValueError("Некорректное значение для стартовых условий!")
                    
            self.country = COUNTRY_DEFAULT
            self.obj_start = country_start

        else:
            raise ValueError("Некорректное значение для стартовых условий!")

    def reset(self):
        self.reset_obj_built()
        self.progress = [] # прогресс линий строительства
        self.laws_current = {} # набор действующих законов
        
        self.laws_timeline = [] # актуальное состояние очереди законов на изменение
        self.build_order = [] # актуальное состояние очереди строительства

        self.cells_dict = {} # актуальное состояние ячеек строительства
        for cell_name, value in CELLS_DICT.items():
          self.cells_dict[cell_name] = Cell(cell_name, *value)
        
    def reset_obj_built(self): # сделано отдельно - под классы-наследники - с другой структурой self.obj_built
        self.obj_built = {'infr':0, 'civ':0, 'mil':0} # количество построенных в симуляции объектов

    # -----------------------------------------------------
    # бонусы строительства:
    # -----------------------------------------------------

    def get_build_bonus(self): 
        # build_bonus - бонус скорости строительства объектов, зависящий от законов, технологий и советников 
        # build_bonus изменяется при изменении закона

        laws_current = self.laws_current.values()

        if not len(laws_current):
            raise ValueError('Упс! В наборе действующих законов нет ни одного закона!')
            
        build_bonus = {}

        for obj_type in self.obj_built:
          
            build_bonus[obj_type] = 1 
            for law in laws_current:
                 build_bonus[obj_type] += LAWS_MODIFICATORS[law][obj_type] # исходя из change_laws_current, краша быть не может:
                                                                           # laws_current заполняется только корректными законами - из LAWS_MODIFICATORS     
        return build_bonus

    # -----------------------------------------------------
    # штраф ТНП и фабрики, доступные для строительства:
    # -----------------------------------------------------

    def get_cons_goods_penalty(self): 
        # cons_goods_penalty - штраф ТНП
        # cons_goods_penalty изменяется при изменении закона, если закон - на изменение ТНП, т.е с law_tag == 'econ' 

        cons_goods_law = self.laws_current.get('econ') # => None, если такого закона нет 
                                                       # (можно ввести константу: CONS_GOODS_TAG = 'econ', но и так сойдет)
        if cons_goods_law is None:
            raise ValueError('Упс! В наборе действующих законов нет закона на ТНП!') 

        cons_goods_penalty = LAWS_MODIFICATORS[cons_goods_law]['cons_goods_penalty'] # исходя из change_laws_current, краша быть не может
        return cons_goods_penalty 
            

    def get_civ_available(self, cons_goods_penalty, civ_trade_av):
        # сiv_available - количество доступных для строительства фабрики - тех, которые миновали штраф ТНП
        # civ_available изменяется при изменении закона, влияющего на ТНП, а также при постройке объекта - не инфраструктуры
        # метод используется как вспомогательный для get_civ_for_lines()

        civ_total_num = self.obj_start['civ'] + self.obj_built['civ'] + civ_trade_av
        mil_total_num = self.obj_start['mil'] + self.obj_built['mil'] 
        all_total_num = civ_total_num + mil_total_num

        civ_cons_goods_required = math.ceil(all_total_num * (cons_goods_penalty))
        civ_available = civ_total_num - civ_cons_goods_required

        return civ_available

    def get_civ_for_lines(self, cons_goods_penalty, civ_trade_av): 
        # civ_for_lines - доступные для строительства фабрики, распределенные по линиям производства
        # civ_for_lines изменяется при изменении закона, влияющего на ТНП, а также при постройке объекта - не инфраструктуры
        # метод используется как вспомогательный для progress_change_lines_num()
        
        # замечание: 
        # change_lines_num() также возвращает civ_for_lines => есть 2 способа получить civ_for_lines, 
        # но в основном цикле мы используем только способ ч/з change_lines_num()
        
        civ_available = self.get_civ_available(cons_goods_penalty, civ_trade_av)
        civ_for_lines = [15 for item in range(civ_available // 15)]
        if civ_available % 15:
            civ_for_lines.append(civ_available % 15)

        return civ_for_lines

    # -----------------------------------------------------
    # изменение законов:
    # -----------------------------------------------------

    def get_day_to_change_law(self): 
        # day_to_change_law - ближайший из дней изменения закона - от начала симуляции
        # day_to_change_law инициализируется на старте симуляции, а затем изменяется при изменении закона

        if len(self.laws_timeline):
            date_to_change_law = self.laws_timeline[0][0]
            day_to_change_law = get_days_diff(GAME_START, date_to_change_law)
        else:
            day_to_change_law = -1 # индикатор: self.laws_timeline пуст, законов на смену не осталось
        return day_to_change_law

    def change_laws_current(self):
        # изменение действующего набора законов self.laws_current и очереди законов на изменение self.laws_timeline
        # метод используется при изменении закона

        laws_to_change = self.laws_timeline.pop(0)[1]
        
        # is_cons_goods_law_changed - флаг: был ли изменен закон на изменение ТНП, т.е с law_tag = 'econ' 
        is_cons_goods_law_changed, optional_str = False, ''

        for law in laws_to_change:

            law_tag = LAWS_MODIFICATORS.get(law, {}).get('tag')
            
            if law_tag is None:
                raise ValueError('%s - некорректное имя закона! Закон не из LAWS_MODIFICATORS!' %law) 
            
            # --------------------------------------------
            if self.printout:
                law_old = self.laws_current.get(law_tag, 'None (1е изменение)')
                optional_str += 'Закон был изменен: %s -> %s (%s)\n' %(law_old, law, law_tag)
            # --------------------------------------------

            self.laws_current[law_tag] = law

            if law_tag == 'econ':
                is_cons_goods_law_changed = True

        # --------------------------------------------
        if self.printout:
            optional_str += self.str_2 + '\n' 
            optional_str += 'Действующие законы:\n'
            for law_tag, law in self.laws_current.items():
                optional_str += '%s: %s\n' %(law_tag, law)
        # --------------------------------------------
        
        return is_cons_goods_law_changed, optional_str

    # -----------------------------------------------------
    # изменение прогресса линий:
    # -----------------------------------------------------
    
    def progress_add_new_line(self): 
        # добавление новой линии в конец self.progress
        # метод используется как вспомогательный для progress_shift_lines() и progress_change_lines_num()

        if self.build_order: 
            self.progress.append([self.build_order.pop(0), 0])
            
    def progress_shift_lines(self, line_data): 
        # удаление линии self.progress с данными line_data и добавление новой линии в конец - согласно механике игры
        # метод используется, когда в некоторой ячейке заканчивается очередь строительства

        self.progress.remove(line_data)
        self.progress_add_new_line()  
 
    def progress_change_lines_num(self, cons_goods_penalty, civ_trade_av): 
        # перераспределение линий self.progress - добавление новых или удаление имеющихся
        # метод используется при изменении числа линий civ_for_lines - линий, доступных для стройки,  
        # т.е, при изменении закона, влияющего на ТНП, а также при постройке объекта - не инфраструктуры

        civ_for_lines = self.get_civ_for_lines(cons_goods_penalty, civ_trade_av)
        lines_num_diff = len(civ_for_lines) - len(self.progress)
        
        if lines_num_diff < 0: # сценарий уменьшения числа линий 
            for __ in range(abs(lines_num_diff)):
                self.build_order.insert(0, self.progress.pop()[0])

        elif lines_num_diff > 0: # сценарий увеличения числа линий
            for __ in range(lines_num_diff):
                self.progress_add_new_line()  

        return civ_for_lines

    # -----------------------------------------------------
    # чек постройки объектов:
    # -----------------------------------------------------

    def change_obj_built(self, *args):
        # изменение self.obj_built при постройке объекта
        # метод используется при постройке объекта - как вспомогательный для check_all_objects_completed()
        # метод добавлен для использования в классах-наследниках - с другой структурой self.obj_built
        
        # obj_type, *__ = args
        obj_type = args[0]
        
        self.obj_built[obj_type] += 1
    
    def get_obj_completed_str(self, *args):
        # возвращает строку с описанием постройки объекта
        # метод используется при постройке объекта - как вспомогательный для check_all_objects_completed()
        # метод добавлен для использования в классах-наследниках - с другой структурой self.obj_built
        
        # cell_name, obj_type, *__ = args
        cell_name, obj_type = args[:2]
        
        return 'Объект "%s" #%i построен в ячейке: %s\n' %(obj_type, self.obj_built[obj_type], cell_name) 
    
    def check_all_objects_completed(self): 
        # проверка по каждой из линий производства self.progress - завершено ли строительство объекта на данной линии
        # метод используется каждый день основного цикла

        is_not_infr_completed, optional_str = False, ''
        build_log_today = [] # список объектов, построенных в данный день
        lines_to_remove = [] # линии строительства для удаления

        for line_idx, line_data in enumerate(deepcopy(self.progress)): # deepcopy на всякий случай - тк в цикле можем менять self.progress
                                                                       # и вообще - в таких ситуациях это хорошая привычка 
            cell_name, obj_type, num_to_build = line_data[0]
            build_points = line_data[1]
            cell = self.cells_dict[cell_name] # краша быть не может
            
            object_cost = OBJ_COST[obj_type]
            is_object_completed = build_points >= object_cost
            
            if is_object_completed:
              
                self.change_obj_built(obj_type, line_idx) # line_idx - под класс-наследник  

                # --------------------------------------------
                if self.printout:
                    if not build_log_today: # уникальный - единственный случай за день, когда объект уже построен, 
                                            # но build_log_today еще пуст => используем как флаг 
                        optional_str = self.get_progress_str() # подняли наверх, чтобы печатать ДО обновления num_to_build, 
                                                               # как задумано в формате печати
                        optional_str += self.str_1 + '\n'
                    optional_str_inner = self.get_obj_completed_str(cell_name, obj_type, line_idx) # line_idx - под класс-наследник    
                    optional_str += optional_str_inner
                # --------------------------------------------
                
                num_to_build -= 1
                self.progress[line_idx][0][-1] = num_to_build

                if num_to_build == 0: # => изначальный num_to_build < 0 = бесконечная стройка на данной линии
                    # lines_to_remove.append(line_data) # здесь тонко: надо понимать, что из себя представляет line_data
                    lines_to_remove.append(self.progress[line_idx]) # лучше так => указывает на ТОТ ЖЕ список, что внутри self.progress => он гарантированно будет присутствовать при удалении
                else:
                    self.progress[line_idx][1] -= object_cost # согласно механике игры: 
                                                              # на незавершенной очереди в ячейке - сохраняем остаток прогресса 
                if obj_type == 'infr':
                    cell.infrastructure_up()
                else:
                    is_not_infr_completed = True
                    cell.obj_available_down()

                build_log_today.append(obj_type) 

        for line_data in lines_to_remove: 
            # print(line_data)
            # print(self.progress)
            self.progress_shift_lines(line_data)
                
        return is_not_infr_completed, optional_str, build_log_today
    
    # -----------------------------------------------------
    # вспомогательные функции:
    # -----------------------------------------------------

    def quit_trigger(self): 
        # настраиваемый триггер выхода из основного цикла, построенный на полях экземпляра класса 
        # помимо непосредственно триггера возвращает его описание, которое используется при печати
        
        # замечание:
        # в данном случае: quit_trigger => конец строительства build_order => нет смысла продолжать симуляцию  
        
        quit_trigger = not (len(self.build_order) + len(self.progress)) 
        quit_trigger_title = '(все стройки завершены)' 
        
        return quit_trigger, quit_trigger_title 
        
    def everyday_optional_stuff(self):
        # метод, предназначенный для некоторой работы над полями экземляра класса внутри основного цикла
        # метод добавлен для использования в классах-наследниках
        pass
      
    def print_cell_dict_debug(self): 
        # служебная функция - для дебага
        # отображает текущее состояние self.cells_dict

        for cell in self.cells_dict.values():
            print(cell)
      
    # -----------------------------------------------------
    # дополнительные методы:
    # -----------------------------------------------------
    
    def expand_cells_dict(self, build_order): 
        # метод расширяет self.cells_dict по принципу: 
        # если в build_order есть имя ячейки не из self.cells_dict, 
        # то добавляем в self.cells_dict ячейку с данным именем и параметрами по умолчанию
        # метод используется на старте симуляции
        
        # замечание:
        # таким образом, страхуемся от краша по KeyError в self.cells_dict в процессе выполнения симуляции
        
        # изначальный вариант:
            # for cell_name, *__ in build_order: 
            #     if cell_name not in self.cells_dict:
            #         self.cells_dict[cell_name] = Cell(cell_name)
        
            # оказалось, что изначальный вариант плох, тк 
            # в случае необходимости создать generic-ячейку (BuildSimMaxMilitary, например):
            # - либо создавалась ячейка с именем None,
            # - либо из-за ограничения на параметры инициализации имени ячейки, происходил краш при попытке создать ячейку с именем "generic_..."
            # все это - из-за примитивного подхода и обязательного условия механики симуляции: 
            # имени ячейки из build_order должна соответствовать ячейка в self.cells_dict c таким же именем 
            
            # вариант ниже позволяет создавать ячейки корректно, выполняя при этом условие выше 
        
        for idx, data in enumerate(deepcopy(build_order)): # deepcopy на всякий случай - тк в цикле можем менять build_order
        
            cell_name = data[0]
            
            if cell_name not in self.cells_dict: # ?in CELLS_DICT - нет, 
                                                 # тк мы можем строить повторно в ТОЙ ЖЕ ячейке => ее не нужно пересоздавать
                new_cell = Cell(cell_name) # новые ячейки должны создаваться ТОЛЬКО здесь
            
                if cell_name is None: # => имя ячейки поменяется => нужно обновить build_order
                    cell_name = new_cell.get_name()
                    build_order[idx][0] = cell_name
                
                self.cells_dict[cell_name] = new_cell
                
    def check_build_order(self, build_order):
        # "fail_fast" метод: проверяет build_order на корректность
        # метод используется на старте симуляции
        
        is_correct, error_message = True, ''

        for line_data in build_order: 

            cell_name, obj_type, num_to_build = line_data
            cell = self.cells_dict[cell_name] # краша быть не может
            cell_infrastructure = cell.get_infrastructure()
            cell_obj_available = cell.get_obj_available()
            
            # print(cell)

            if obj_type not in self.obj_built: # некорректный obj_type
                is_correct = False
                error_message = "\nЯчейка: %s. Тип постройки '%s' - некорректное значение!" %(cell_name, obj_type)

            if not isinstance(num_to_build, int) or not num_to_build: # элементы build_order с нецелочисленным и нулевым num_to_build
                is_correct = False
                error_message = "\nЯчейка: %s. Количество объектов = %s - некорректное значение!" %(cell_name, num_to_build)

            elif obj_type == 'infr': 
                
                if cell_infrastructure + num_to_build > 10: # дан заказ на постройку инфраструктуры выше 10го уровня
                    is_correct = False
                    error_message = "\nЯчейка: %s. Инфраструктура: %s. Ты пытаешься построить еще %s уровней => выше 10го уровня!" %(cell_name, cell_infrastructure, num_to_build)

                if num_to_build < 0: # бесконечная очередь строительства инфраструктуры в ячейке
                    is_correct = False
                    error_message = "\nЯчейка: %s. Ты пытаешься построить бесконечное количество инфраструктуры!" %cell_name

            else: # => obj_type == 'civ'/'mil'

                if num_to_build > cell_obj_available:
                    is_correct = False
                    error_message = "\nЯчейка: %s. Доступно строек: %s. Ты пытаешься построить %s объектов!" %(cell_name, cell_obj_available, num_to_build)

        if not is_correct:
            raise ValueError('Упс! Очередь строительства некорректна!' + error_message)
    
    def check_default_args(self, laws_timeline, civ_trade_av, date_end): # (как вариант)
        # "fail_fast" метод: проверяет default-аргументы build_sim на корректность
        # метод используется на старте симуляции
        pass
            
    # -----------------------------------------------------
    # функции и методы печати:
    # -----------------------------------------------------

    def print_header(self):
        # печать сообщения при начале симуляции (всегда)

        header_str = self.str_1
        header_str += '\nСТАРТ СИМУЛЯЦИИ ...'
        header_str += '\n(произвольная очередь строительства)'
        header_str += '\n' + self.str_2
        header_str += '\nСтрана: %s' %self.country
        header_str += '\nОбъекты на старте: %s' %self.obj_start
        header_str += '\n' + self.str_2
        header_str += '\n' + self.get_build_order_str().rstrip()
        header_str += '\n' + self.str_2

        print(header_str)

    def print_aftermath(self, day):
        # печать сообщения при выходе из симуляции (всегда)
        
        actual_date = add_days(GAME_START, day)
        
        quit_trigger, quit_trigger_title = self.quit_trigger()
        quit_str = {True:('по триггеру ' + quit_trigger_title), False:'по дате'}[quit_trigger] 
        
        if self.printout: 
            # print('\n\n' + self.str_2)
            print('\n' + self.str_2)
          
        aftermath_str = 'ГОТОВО! День = %i ' %day + '(%s-%s-%s)' %actual_date 
        aftermath_str += '\nЗАВЕРШЕНИИЕ СИМУЛЯЦИИ: %s' %quit_str
        aftermath_str += '\nПостроенные объекты: %s' %self.obj_built
        # aftermath_str += '\n' + self.str_1 + '\n'
        aftermath_str += '\n' + self.str_1 + '\n\n'

        print(aftermath_str)
        
    def get_progress_str(self, build_bonus=None, civ_for_lines=None):
        # составление строки, отражающей текущее состояние прогресса линий self.progress 
        # метод доступен в 2х версиях - версия с более подробной печатью требует задания аргументов build_bonus и civ_for_lines
        # метод используется как вспомогательный для print_output() 

        progress_str = 'Прогресс линий строительства:' + '\n' 

        for line_idx, line_data in enumerate(self.progress): 
            cell_name, obj_type, num_to_build = line_data[0]
            build_points = line_data[1]
            
            if num_to_build < 0:num_to_build = '∞'
            
            str_1 = '- ячейка: %s' %cell_name
            str_2 = ", заказанный_объект: '%s' (количество = %s), прогресс: %.2f" %(obj_type, num_to_build, build_points)
            
            add_str_1, add_str_2 = '', ''
            if build_bonus and civ_for_lines:
              
                cell = self.cells_dict[cell_name]
                cell_infrastructure = cell.get_infrastructure()
              
                infr_bonus = {True:1, False:(10 + cell_infrastructure) / 10}[obj_type == 'infr']
                progress_per_day = 5 * build_bonus[obj_type] * infr_bonus * civ_for_lines[line_idx] 
                add_str_1 = ' (infr = %i)' %cell_infrastructure
                add_str_2 = ', прогресс_в_день: %.2f (фабрики = %i)' %(progress_per_day, civ_for_lines[line_idx])
            
            progress_str += str_1 + add_str_1 + str_2 + add_str_2 + '\n'
        
        return progress_str

    def get_build_order_str(self):
        # составление строки, отражающей текущее состояние очереди строительства self.build_order
        # метод используется как вспомогательный для print_output() 

        build_order_str = 'Очередь строительства:' + '\n' 

        for line_data in self.build_order: 
            cell_name, obj_type, num_to_build = line_data
            cell = self.cells_dict[cell_name]
            cell_infrastructure = cell.get_infrastructure()
            
            if num_to_build < 0:num_to_build = '∞'
            
            build_order_str += "- ячейка: %s (infr = %i), заказанный_объект: '%s' (количество = %s)\n" %(cell_name, cell_infrastructure, obj_type, num_to_build) 

        return build_order_str

    def print_output(self, optional_str, day, build_bonus, cons_goods_penalty, civ_for_lines, law_flag): # law_flag - день изменения закона или нет
        # печать сообщения в день события - при изменении закона или постройке объекта

        # замечание:
        # сообщение описывает текущее состояния параметров симуляции и использует опциональную входящую строку optional_str
        # метод вызывается только при подробной версии печати (self.printout == True)
        
        for obj_type in build_bonus:
            build_bonus[obj_type] = round(build_bonus[obj_type], 2)

        actual_date = add_days(GAME_START, day)

        output_str = '\n\n'
        output_str += 'День = %i ' %day + '(%s-%s-%s)' %actual_date + '\n'
        output_str += self.str_2 + '\n'
        output_str += optional_str
        output_str += {True:self.str_2, False:self.str_1}[law_flag] + '\n'
        output_str += 'Бонусы строительства: %s' %build_bonus + '\n'
        output_str += 'Штраф ТНП: %s' %cons_goods_penalty + '\n'
        output_str += 'Распределение фабрик по линиям строительства: %s' %civ_for_lines + '\n'
        output_str += self.str_2 + '\n'
        output_str += {True:'Прогресс линий строительства: EMPTY\n', False:self.get_progress_str(build_bonus, civ_for_lines)}[not self.progress]
        output_str += self.str_2 + '\n'
        output_str += {True:'Очередь строительства: EMPTY\n', False:self.get_build_order_str()}[not self.build_order]
        output_str += self.str_2 + '\n'
        output_str += 'Построенные объекты: %s' %self.obj_built

        print(output_str)

    # =====================================================
    # ОСНОВНОЙ МЕТОД - СИМУЛЯТОР СТРОИТЕЛЬСТВА:
    # =====================================================

    def build_sim(self, build_order, laws_timeline='no_changes', civ_trade_av=0, date_end=INFINITE_LOOP_BREAKER):
        # симулятор строительства по заданным: 
        # - очереди строительства build_order 
        # - таймингам принятия законов laws_timeline
        # - среднему количеству дополнительных фабрик от торговли civ_trade_av
        
        self.reset()

        # --------------------------------------------
        # коррекция значений default-аргументов симуляции:
        # --------------------------------------------
        
        if laws_timeline == 'no_changes': 
            laws_timeline = [] # ставить [] в default-значение 'опасно' (уууууу - вот насколько это опасно)
            
        date_end_exception = ValueError('Упс! {0} - некорректное значение для даты завершения симуляции!'.format(date_end)) 
        
        try:
            day_end = get_days_diff(GAME_START, date_end)
            if not isinstance(day_end, int) or day_end <= 0:
                raise date_end_exception
        except:
            raise date_end_exception 
        
        # вариант (устарело - теперь новый формат date_end):
            # (см также check_default_args())
            # # --------------------------------------------
            # if not isinstance(civ_trade_av, int):
            #     raise ValueError('Упс! {0} - некорректное значение для средней разницы фабрик от торговли!'.format(civ_trade_av))
            
            # # --------------------------------------------
            # if date_end == 'default':
            #     date_end = add_days(GAME_START, BuildSimulator.INFINITE_LOOP_BREAKER) # чтобы не делать работу функции add_days заранее:
            #                                                                           # в момент определения метода build_sim() - то есть, при импорте BuildSimulator
            
            # date_end_exception = ValueError('Упс! {0} - некорректное значение для даты завершения симуляции!'.format(date_end)) 
            
            # try:
            #     day_end = get_days_diff(GAME_START, date_end)
            #     if not isinstance(day_end, int) or day_end <= 0:
            #         raise date_end_exception
            # except:
            #     raise date_end_exception 
            # # --------------------------------------------    
            
        # --------------------------------------------
        # предварительная работа с очередью строительства:
        # --------------------------------------------  
        
        self.expand_cells_dict(build_order)
        self.check_build_order(build_order)

        # --------------------------------------------
        # доопределение набора стартовых значений параметров симуляции:
        # --------------------------------------------    
        
        country_condition = (self.country != COUNTRY_DEFAULT)
        
        if country_condition:
            laws_start = CONDITIONS_START[self.country]['laws_start'] # краша быть не может
            self.laws_timeline += laws_start
            # self.laws_timeline += deepcopy(laws_start) # deepcopy не нужно
        
        self.build_order += deepcopy(build_order) # актуальное состояние очереди строительства
        # --------------------------------------------
        # блок *16346 (см main.py): 
        # тест не использования deepcopy для self.build_order       
        # self.build_order += build_order # => краш при 2й симуляции по той же очереди строительства
        # --------------------------------------------
        
        self.laws_timeline += laws_timeline
        # self.laws_timeline += deepcopy(laws_timeline) # deepcopy не нужно 
        # print("\nCHECK\n", self.laws_timeline)
        # --------------------------------------------
        # блок *78345 (см main.py): 
        # тест изменения внутренней стр-ры laws_timeline при изменении self.laws_timeline
        # self.laws_timeline[-1][-1] = 'Ненарушаемая_изоляция' 
        # --------------------------------------------
        
        day_to_change_law = self.get_day_to_change_law() # ближайший день изменения закона
        # print(day_to_change_law)
        if day_to_change_law != 1:
            raise ValueError('Упс! Стартовые законы не определены!')
            
        build_log = [] # лог построенных объектов: (день постройки, тип постройки) - используется для графиков

        self.print_header() # переместили вниз, тк используем self.build_order
        
        # --------------------------------------------
        # непосредственно симуляция строительства:
        # --------------------------------------------        
        
        for day in itertools.count(1):

            # --------------------------------------------
            # чек изменения закона:
            # --------------------------------------------

            if day == day_to_change_law:
              
                # print("HERE")

                is_cons_goods_was_changed, optional_str = self.change_laws_current()      
                if is_cons_goods_was_changed: # закон на ТНП был изменен

                    cons_goods_penalty = self.get_cons_goods_penalty()
                    civ_for_lines = self.progress_change_lines_num(cons_goods_penalty, civ_trade_av)

                build_bonus = self.get_build_bonus()
                day_to_change_law = self.get_day_to_change_law() 

                # --------------------------------------------
                if self.printout:
                    self.print_output(optional_str, day, build_bonus, cons_goods_penalty, civ_for_lines, law_flag=True)
                # --------------------------------------------

                # if country_condition:
                #     print('\n', CONDITIONS_START[self.country]['laws_start'])
                # print('\n', laws_timeline)
                # print('\n', self.laws_timeline)
                
            # --------------------------------------------
            # чек постройки объектов:
            # --------------------------------------------

            is_not_infr_completed, optional_str, build_log_today = self.check_all_objects_completed()

            if is_not_infr_completed:
                civ_for_lines = self.progress_change_lines_num(cons_goods_penalty, civ_trade_av)

            for obj_type in build_log_today:
                build_log.append((day, obj_type))

            # --------------------------------------------
            if build_log_today: 
                if self.printout:
                    self.print_output(optional_str, day, build_bonus, cons_goods_penalty, civ_for_lines, law_flag=False)
            # --------------------------------------------

            # --------------------------------------------
            # опциональная часть и выход из цикла:
            # --------------------------------------------

            self.everyday_optional_stuff()
            quit_trigger, __ = self.quit_trigger()
        
            if quit_trigger or day == day_end: # у триггера приоритет над выходом по дате
                self.print_aftermath(day)
                break
              
            # замечание: условие day == day_end можно рассматривать как 'quit_trigger по умолчанию':
            # выход из цикла в запланированный день;
            # а quit_trigger - как настраиваемый триггер

            # --------------------------------------------
            # изменение прогресса ячеек:
            # --------------------------------------------

            progress_len = len(self.progress)
            for line_idx, civ_num in enumerate(civ_for_lines):
                if line_idx < progress_len: 
                  
                    cell_name, obj_type, __ = self.progress[line_idx][0]
                    cell = self.cells_dict[cell_name]
                    cell_infrastructure = cell.get_infrastructure()
    
                    infr_bonus = {True:1, False:(10 + cell_infrastructure) / 10}[obj_type == 'infr']
                    progress_per_day = 5 * build_bonus[obj_type] * infr_bonus * civ_num                               
                    self.progress[line_idx][1] += progress_per_day 

        build_log.append((day, 'end')) # может понадобиться для некоторых графиков 
        return build_log 

# =====================================================
# класс BuildSimMaxMilitary - симулятор строительства: 

    # - рассматривается следующая схема строительства:
        # - сначала строится некоторое количество гражданских фабрик
        # - затем строятся военные заводы
  
    # - завершение симуляции: 
        # - по достижении заданной даты 
  
    # --------------------------------------------
    # - ФУНКЦИОНАЛ ДЛЯ ПОЛЬЗОВАТЕЛЯ:
    # --------------------------------------------
    
        # - симуляция строительства по заданным параметрам: метод build_sim()
        # (с краткой или подробной печатью событий симуляции)
        
        # - расчет количества построенных заводов по различному числу построенных фабрик: метод visualize_efficiency()
        # (с визуализацией в виде графика)

        # - поиск экстремума количества построенных заводов по числу построенных фабрик к определенной дате: метод find_mil_extremum()
        # (с визуализацией в виде графика)
        
    # --------------------------------------------
    # - параметры приложений симуляции, которые задаются пользователем:
  
        # - для создания класса:
            # - country_start: 
                # - либо тэг игровой страны (доступные тэги: 'СССР', 'ГЕРМАНИЯ', 'ЯПОНИЯ', 'ИТАЛИЯ', 'ФРАНЦИЯ', 'США', 'ВБ')
                # - либо количество гражданских фабрик и военных заводов на старте 
                
        # - для основного метода класса - build_sim():
            # - количество фабрик для постройки - civ_num_to_build
            # - средняя инфраструктура ячеек, по которым ведется строительство - infr_av
            # - динамика изменения законов, влияющих на модификаторы строительства и ТНП - laws_timeline (опционально)
            # - средняя разница фабрик от торговли - civ_trade_av (опционально)
            # - дата принудительного завершения симуляции - date_end (опционально; но предполагается, что ... )
          
        # - для метода visualize_efficiency():
            # - список количества фабрик для постройки - civ_num_to_build_list
            # ... (остальные аргументы такие же, как в build_sim() - см выше)
       
        # - для метода find_mil_extremum():
            # ... (аргументы такие же, как в build_sim() - см выше)
# =====================================================

class BuildSimMaxMilitary(BuildSimulator):

    def reset_obj_built(self):
        self.obj_built = {'civ':0, 'mil':0} # в данной симуляции не строим инфраструктуру

    # -----------------------------------------------------
    # новый header - в соответствии с параметрами симуляции:
    # -----------------------------------------------------

    def print_header(self):
        pass

    def print_new_header(self, civ_num_to_build, infr_av, date_end): 
        
        header_str = self.str_1
        header_str += '\nСТАРТ СИМУЛЯЦИИ ...'
        header_str += '\n(максимизация военных заводов)'
        header_str += '\n' + self.str_2
        header_str += '\nСтрана: %s' %self.country
        header_str += '\nОбъекты на старте: %s' %self.obj_start
        header_str += '\n' + self.str_2
        header_str += '\nКоличество гражданских фабрик для постройки: %s' %civ_num_to_build 
        header_str += '\nСредняя инфраструктура ячеек строительства: %s' %infr_av 
        header_str += '\nДата завершения симуляции: (%i-%i-%i)' %date_end
        header_str += '\n' + self.str_2

        print(header_str)

    # -----------------------------------------------------
    # новый порядок добавления линий - в соответствии со схемой строительства:
    # -----------------------------------------------------

    def progress_add_new_line(self): 
        super().progress_add_new_line()
        if not self.build_order: # в данной симуляции при постройке всех заказанных фабрик добавляем воензаводы до бесконечности
            
            # вариант:
                # ниже происходит то, что уже реализовано в expand_cells_dict
                # new_cell = Cell() 
                # cell_name = new_cell.get_name()
                # self.cells_dict[cell_name] = new_cell
                # self.build_order.append([cell_name, 'mil', 1])
            
            self.build_order.append([None, 'mil', 1])
            self.expand_cells_dict(self.build_order)
            
    # -----------------------------------------------------
    # новый build_sim:
    # -----------------------------------------------------
    
    def build_sim(self, civ_num_to_build, infr_av, laws_timeline='no_changes', civ_trade_av=0, date_end=INFINITE_LOOP_BREAKER): 
        # в данной симуляции выход из цикла должен быть всегда по date_end
        self.print_new_header(civ_num_to_build, infr_av, date_end)
        
        Cell.INFRASTR_DEFAULT = infr_av
        
        # варианты:
        
            # 1)
            # ниже происходит то, что уже реализовано в expand_cells_dict
            # build_order = []
            # for __ in range(civ_num_to_build):
            #     new_cell = Cell()
            #     cell_name = new_cell.get_name()
            #     self.cells_dict[cell_name] = new_cell
            #     build_order.append([cell_name, 'civ', 1])
            
            # 2)
            # build_order = [[Cell().get_name(), 'civ', 1] for __ in range(civ_num_to_build)] # не работает, тк name = 'generic_...'
        
        build_order = [[None, 'civ', 1] for __ in range(civ_num_to_build)]
        return super().build_sim(build_order, laws_timeline, civ_trade_av, date_end)
        
    # -----------------------------------------------------
    # методы визуализации:
    # -----------------------------------------------------
    
    def visualize_efficiency(self, civ_num_to_build_list, infr_av, laws_timeline, civ_trade_av, date_end):
        # ?какой график ты строишь - определись
        for civ_num_to_build in civ_num_to_build_list:

            build_log = self.build_sim(civ_num_to_build, infr_av, laws_timeline, civ_trade_av, date_end)
            
            mil_built_day = [day for day, obj in build_log if obj == 'mil']
            mil_built_total = len(mil_built_day)
            mil_built_num = list(range(1, mil_built_total + 1)) 
            
            # варианты:
                # https://stackoverflow.com/questions/9304408/how-to-add-an-integer-to-each-element-in-a-list
                # new_list = [x+1 for x in my_list]
                # map(lambda x:x+1, [1,2,3])
    
            # график с 1го дня: (можно лучше)
                # prefix_part = [(day, 0) for day in range(1, built_mil_day[0])]
                # prefix_part_day, prefix_part_num = zip(*prefix_part)
                # built_mil_day = list(prefix_part_day) + mil_built_day
                # built_mil_num = list(prefix_part_num) + mil_built_num

            plt.plot(mil_built_day, mil_built_num, label='civ_built: %i => mil_built: %i' %(civ_num_to_build, mil_built_total))

        # fig = plt.gcf() # для версии на ПК
        # fig.canvas.set_window_title('HOI4 Infrastructure Efficiency') # для версии на ПК
        
        plt.title('Building Efficiency to the date: {0}'.format(date_end))
        plt.xlabel('Days')
        plt.ylabel('Military factories were built')
        plt.legend()
        
        plt.savefig('graph.png')
        # plt.show() # для версии на ПК

    def find_mil_extremum(self, infr_av, laws_timeline, civ_trade_av, date_end, mil_built_stop=10):
    
        mil_built_max, mil_built_1st_day, civ_num_to_build_optimum = 0, 0, 0
        x_coord, y_coord = [], []
        
        for civ_num_to_build in itertools.count(1): 

            build_log = self.build_sim(civ_num_to_build, infr_av, laws_timeline, civ_trade_av, date_end)
            
            mil_built_day = [day for day, obj in build_log if obj == 'mil']
            mil_built_total = len(mil_built_day)
            # mil_built_num = list(range(1, len(mil_built_day) + 1)) 

            if mil_built_total < mil_built_stop: # не делаем лишнюю работу, когда результат и так уже понятен
                break

            x_coord.append(civ_num_to_build)
            y_coord.append(mil_built_total)

            if mil_built_total >= mil_built_max: # при >= найдет последнее - те, макс число фабрик при макс числе воензав
                mil_built_max, mil_built_1st_day, civ_num_to_build_optimum = mil_built_total, mil_built_day[0], civ_num_to_build

        mil_built_1st_date = add_days(GAME_START, mil_built_1st_day)

        print('Optimum: %i civilian_f built => %i military_f built\nDate of the 1st military_f built: %s\n' %(civ_num_to_build_optimum, mil_built_max, mil_built_1st_date))
        
        # fig = plt.gcf() # для версии на ПК
        # fig.canvas.set_window_title(self.country) # для версии на ПК 

        plt.plot(x_coord, y_coord, '.', label = 'Optimum to the date: %s\n+%i civ factories => +%i mil factories\nDate of the 1st military_f built: %s' %(date_end, civ_num_to_build_optimum, mil_built_max, mil_built_1st_date))
        plt.title('Finding the max num of the military_f built')
        plt.xlabel('Number civilian_f built')
        plt.ylabel('Number military_f built')
        plt.legend()

        plt.savefig('graph.png')
        # plt.show() # для версии на ПК
        
# =====================================================
# класс BuildSimInfrEfficiency - симулятор строительства: 

  # - рассматривается следующая схема строительства:
  # - сравниваем строительство по 2м ячейкам (с равными начальными условиями):
      # - ячейка 1: сначала строим некоторое количество инфраструктуры, затем - фабрики
      # - ячейка 2: сразу строим фабрики

  # - завершение симуляции: 
      # - по достижении "точки равновесия":
      # когда строительство инфраструктуры в ячейке 1 окупится с экономической точки зрения
  
  # --------------------------------------------
  # - ФУНКЦИОНАЛ ДЛЯ ПОЛЬЗОВАТЕЛЯ:
    
        # - симуляция строительства по заданным параметрам: метод build_sim()
        # (с краткой или подробной печатью событий симуляции)
        
        # - расчет границы окупаемости строительства инфраструктуры по всевозможным набору стартовой инфраструктуры: метод visualize_equilibrium()
        # (с визуализацией в виде графика)

        # - определение - окупается ли строительство инфраструктуры в данной конкретной ячейке: метод is_cell_profitable()
        
        # - определение - окупается ли строительство инфраструктуры для какой-любо из ячеек в данной стране: метод is_any_cell_profitable() # (beta)


        # def build_sim(self, infr_initial, infr_up, laws_timeline='no_changes', civ_trade_av=0, date_end='default'): 
        # def visualize_equilibrium(self, laws_timeline, infr_up=1, civ_trade_av=0, add_dots_country=False):
        # def is_cell_profitable(self, cell, laws_timeline, infr_up=1):
        # def is_any_cell_profitable(self, laws_timeline, infr_up=1): # (beta)
  # --------------------------------------------
  
  # - параметры симуляции, которые задаются пользователем:
        # - для создания класса:
            # - country_start: 
                # - тэг игровой страны (опционально; доступные тэги: 'СССР', 'ГЕРМАНИЯ', 'ЯПОНИЯ', 'ИТАЛИЯ', 'ФРАНЦИЯ', 'США', 'ВБ')
                
        # - для основного метода класса - build_sim():
            # - изначальная инфраструктура ячеек 1 и 2 - infr_initial
            # - количество уровней инфраструктуры для постройки в ячейке 1 - infr_up
            # - динамика изменения законов, влияющих на модификаторы строительства и ТНП - laws_timeline (опционально)
            # - средняя разница фабрик от торговли - civ_trade_av (опционально)
            # - дата принудительного завершения симуляции - date_end (опционально; но предполагается, что ... )
            
        # - для метода vizualize_equilibrium():
            # ... (аргументы такие же, как в build_sim() - см выше)  
       
        # - для метода is_cell_profitable():
            # ... (аргументы такие же, как в build_sim() - см выше) 
            
        # - для метода is_any_cell_profitable(): # (beta)
            # ... (аргументы такие же, как в build_sim() - см выше) 
# =====================================================

# =====================================================
CELLS_DICT_DEMO = {
    
                   # ---------------------------------
                   # ячейки ниже - под демонстрационные примеры в BuildSimInfrEfficiency:  
                   # регионы Германии в условиях изучения конц промышленности 1937 (2й ур = +40% слотов стр-ва)
                   
                   'Нижняя_Бавария': [6, 8, 'ГЕРМАНИЯ'],
                   'Верхняя_Бавария': [7, 4, 'ГЕРМАНИЯ'],
                   'Вюртемберг': [8, 3, 'ГЕРМАНИЯ'],
                   'Франкония': [7, 5, 'ГЕРМАНИЯ'],
                   'Гессен': [7, 7, 'ГЕРМАНИЯ'],
                   'Мозель': [7, 11, 'ГЕРМАНИЯ'],
                   'Рейн': [8, 8, 'ГЕРМАНИЯ'],
                   'Вестфалия': [8, 6, 'ГЕРМАНИЯ'],
                   'Везер_Эмс': [6, 4, 'ГЕРМАНИЯ'],
                   'Саксония': [7, 4, 'ГЕРМАНИЯ'],
                   'Тюрингия': [6, 9, 'ГЕРМАНИЯ'],
                   'Ганновер': [7, 6, 'ГЕРМАНИЯ'],
                   'Бранденбург': [8, 5, 'ГЕРМАНИЯ'],
                   'Мекленбург': [6, 2, 'ГЕРМАНИЯ'],
                   'Шлезвиг': [6, 3, 'ГЕРМАНИЯ'],
                   'Верхняя_Силезия': [6, 8, 'ГЕРМАНИЯ'],
                   'Нижняя_Силезия': [6, 9, 'ГЕРМАНИЯ'],
                   'Восточная_марка': [6, 7, 'ГЕРМАНИЯ'],
                   'Померания': [6, 4, 'ГЕРМАНИЯ'],
                   'Передняя_Померания': [6, 5, 'ГЕРМАНИЯ'],
                   'Восточная_Пруссия': [6, 9, 'ГЕРМАНИЯ'],
                   # ---------------------------------
              
                  }  
# =====================================================

class BuildSimInfrEfficiency(BuildSimulator):
    
    # -----------------------------------------------------
    def __init__(self, country_start=COUNTRY_DEFAULT): # упрощенная симуляция => self.obj_start не нужен

        self.reset()
        
        if CONDITIONS_START.get(country_start) or country_start == COUNTRY_DEFAULT: 
        # предполагается, что country_start здесь всегда str
            self.country = country_start # страна симуляции
        else:
            raise ValueError("Некорректное значение для стартовых условий!")

    def reset(self):
        super().reset()
        self.civ_diff = {'civ_days_diff_total': 0, 'civ_diff_actual': 0} # дополнительное поле, индикатор выхода из цикла
        
        # self.civ_diff - трек потерянных фабрико-дней - словарь с 2мя ключами = ~'total' и ~'actual' 
        
    def reset_obj_built(self):
        self.obj_built = {'infr':[0,0], 'civ':[0,0]} 
        # в данной симуляции не строим воензаводы и ведем учет построек отдельно но каждой из 2х линий
  
    # -----------------------------------------------------
    # изменение civ_diff:
    # -----------------------------------------------------
    
    # 1)-3) цепочка 3 функции - изменение 'civ_diff_actual' части:


    def get_civ_built_available(self, cons_goods_penalty):

        civ_built_list = self.obj_built['civ']
        civ_built_available = [built - math.ceil(built * cons_goods_penalty) for built in civ_built_list]
        # можем себе позволить за счет дистрибутивности ...
        return civ_built_available 

    def change_civ_diff(self, cons_goods_penalty):
    # функция изменяет 'actual' часть словаря civ_diff
    # функция используется при постройке фабрики, а также при изменении закона, влияющего на ТНП

        civ_built_available = self.get_civ_built_available(cons_goods_penalty)
        self.civ_diff['civ_diff_actual'] = civ_built_available[1] - civ_built_available[0] 

    def get_civ_for_lines(self, *args): 
      # когда cons_goods_law и когда построена не инфр, а в данном частном примере "неинфр" = "фабрика" (воензав не строим)
      # => всегда, когда get_civ_for_lines => change_civ_diff           
        
        cons_goods_penalty = args[0]
        self.change_civ_diff(cons_goods_penalty)
        return [15, 15]
    
    # 4) ежедневное изменение 'total' части:

    def everyday_optional_stuff(self):
        self.civ_diff['civ_days_diff_total'] += self.civ_diff['civ_diff_actual'] 
    
    # -----------------------------------------------------
    # новый quit_trigger:
    # -----------------------------------------------------

    def quit_trigger(self):
      
        quit_trigger = self.civ_diff['civ_days_diff_total'] < 0 # достигнута точка равновесия, согласно описанию   
        quit_trigger_title = '(equilibrium)'  
        return quit_trigger, quit_trigger_title  
        
    # -----------------------------------------------------
    # прочие методы:
    # -----------------------------------------------------
   
    def progress_shift_lines(self, line_data): 
        self.progress[0] = [self.build_order.pop(0), 0] 
        # убрали шифт - исключительно для наглядности: 
        # строительство 0й ячейки продолжается по 0й линии, хотя по большому счету без разницы
    
    # -----------------------------------------------------

    def change_obj_built(self, *args): # из-за другой структуры self.obj_built приходится кой-чего поменять
        obj_type, line_idx = args
        self.obj_built[obj_type][line_idx] += 1
    
    def get_obj_completed_str(self, *args): # из-за другой структуры self.obj_built приходится кой-чего поменять
        cell_name, obj_type, line_idx = args
        return 'Объект "%s" #%i построен в ячейке: %s\n' %(obj_type, self.obj_built[obj_type][line_idx], cell_name) 

    # -----------------------------------------------------
    # печать:
    # -----------------------------------------------------
    
    def print_header(self):
        pass

    def print_new_header(self, infr_initial, infr_up): 

        header_str = self.str_1
        header_str += '\nСТАРТ СИМУЛЯЦИИ ...'
        header_str += '\n(промышленная эффективность инфраструктуры)'
        header_str += '\n' + self.str_2
        header_str += '\nСтрана: %s' %self.country
        header_str += '\n' + self.str_2
        header_str += '\nНачальная инфраструктура ячеек: %s' %infr_initial 
        header_str += '\nКоличество инфраструктуры для постройки в ячейке_1: %s' %infr_up
        # header_str += '\n' + self.str_2
        # header_str += '\n' + self.get_build_order_str().rstrip()
        header_str += '\n' + self.str_2

        print(header_str)
            
    def print_output(self, optional_str, day, build_bonus, cons_goods_penalty, civ_for_lines, law_flag):
        super().print_output(optional_str, day, build_bonus, cons_goods_penalty, civ_for_lines, law_flag)
        print('Построенные фабрики доступны:', self.get_civ_built_available(cons_goods_penalty))
        print('Разница фабрико-дней:', self.civ_diff) 
    
    # -----------------------------------------------------
    # новый build_sim:
    # -----------------------------------------------------
    
    def build_sim(self, infr_initial, infr_up, laws_timeline='no_changes', civ_trade_av=0, date_end=INFINITE_LOOP_BREAKER): 
        
        Cell.INFRASTR_DEFAULT = infr_initial
        
        cell_name_0 = 'cell_0'
        cell_name_1 = 'cell_1'
        
        build_order = [[cell_name_0, 'infr', infr_up], [cell_name_1, 'civ', -1], [cell_name_0, 'civ', -1]] 
        # -1 => бесконечная очередь на той же линии
        
        self.print_new_header(infr_initial, infr_up)
        return super().build_sim(build_order, laws_timeline, civ_trade_av, date_end) 
        # предполагается, что date_end ~неограничен - мы хотим достичь точки равновесия 
        # => должен принимать значение по умолчанию = INFINITE_LOOP_BREAKER

    # -----------------------------------------------------

    def visualize_equilibrium(self, laws_timeline, infr_up=1, civ_trade_av=0, add_dots_country=False):
        # 2 графика окупаемости строительства инфраструктуры согласно описанию в шапке файла
        # infr_up - количество уровней инфраструктуры, которые будут построены в ячейке 0
        # 0 <= infr_up <= 10
        
        disable_printout()
        
        # --------------------------------------------
        # элементы оформления графика:
        # --------------------------------------------
        x_label = 'Initial infrastructure level'
        y_label_list = ['Days to payback', 'Factories to payback']
        title_list = ['infr_up=%i' %(infr_up), '']
        color_list = ['b', 'r']
        # --------------------------------------------

        fig, ax = plt.subplots(nrows=1, ncols=2)
        fig.set_size_inches(10, 5) # замечание: опционально под параметры монитора
        # fig.canvas.set_window_title('HOI4 Infrastructure Efficiency') # для версии на ПК
        
        infr_init_levels = list(range(0, 11 - infr_up)) # замечание: берем такой range, тк infr_initial + infr_up <= 10
        x_coord = infr_init_levels
        y_coord = [[],[]]
        
        for infr_level in infr_init_levels:
            day_end_sim = self.build_sim(infr_level, infr_up, laws_timeline, civ_trade_av)[-1][0]
            civ_built_num_cell_0 = self.obj_built['civ'][0]
            
            y_coord[0].append(day_end_sim)
            y_coord[1].append(civ_built_num_cell_0)


        for idx, row in enumerate(ax):
        
            row.plot(x_coord, y_coord[idx], color_list[idx])
            row.set_xlabel(x_label)
            row.set_ylabel(y_label_list[idx])
            row.set_title(title_list[idx])

            if idx == 1: # координаты 2го графика (по слотам для стройки)
                # payback_line = tuple(zip(coord_x, coord_y[idx])) # граница окупаемости по слотам строительства
                
                if add_dots_country: # (beta)
                    
                    # варианты:
                        # cells_country_list = [cell for cell in self.cells_dict.values() if cell.get_country() == self.country and self.country != COUNTRY_DEFAULT]
                        # cells_country_list = [Cell(cell, *value) for cell, value in CELLS_DICT_DEMO.items() if value[-1] == self.country]
                        
                        # if len(cells_country_list):
                            # dots_country = [(cell.get_infrastructure(), cell.get_obj_available()) for cell in cells_country_list]
                        
                    dots_country = [(value[0], value[1]) for value in CELLS_DICT_DEMO.values() if value[2] == self.country]
                    dots_country_x, dots_country_y = zip(*dots_country)
                    row.plot(dots_country_x, dots_country_y, 'og', label='Регионы: {0}\n(демонстрационный пример)'.format(self.country))
                    plt.legend()

        # plt.show() # для версии на ПК
        plt.savefig('graph.png')
        
        enable_printout()
        # print('Payback Line (infr_to_up=%i):\n%s\n' %(infr_up, payback_line))
        
        # return payback_line
    # -----------------------------------------------------

    def is_cell_profitable(self, cell, laws_timeline, infr_up=1):
      
        disable_printout()
        
        self.reset()
        
        if isinstance(cell, str) and cell in self.cells_dict: # здесь cell - строка, имя существующей ячейки
           cell = self.cells_dict[cell] 
        
        if not isinstance(cell, Cell):
            raise ValueError('{0} - некорректное значение для ячейки!'.format(cell))
            
        cell_infrastructure = cell.get_infrastructure()
        cell_obj_available = cell.get_obj_available()
        
        self.build_sim(cell_infrastructure, infr_up, laws_timeline)
        civ_built_num_cell_0 = self.obj_built['civ'][0]

        condition =  cell_obj_available >= civ_built_num_cell_0
        verdict = {True:'YEAHHHH!', False:'NOOOOO!'}[condition]
        
        enable_printout()
        
        print(self.str_1)
        print(cell)
        print('Is the cell profitable?? ' + verdict)
        print(self.str_1)
        print()
        
        return condition
        
    def is_any_cell_profitable(self, laws_timeline, infr_up=1): # (beta)

        self.reset()
        
        cells_country_list = [cell for cell in self.cells_dict.values() if cell.get_country() == self.country and self.country != COUNTRY_DEFAULT]
        if not len(cells_country_list):
            print('Нет ячеек для данной страны!')
            return
        
        cells_profitable = []
        for cell in cells_country_list:
            print(cell)
            cell_name = cell.get_name()
            if self.is_cell_profitable(cell_name, laws_timeline, infr_up):
                cells_profitable.append(cell_name)
        
        return cells_profitable
        
# =====================================================
def testing():
    pass

if __name__ == '__main__':
    testing()
# =====================================================

