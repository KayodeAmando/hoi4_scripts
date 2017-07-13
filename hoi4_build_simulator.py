import matplotlib.pyplot as plt
import math
import itertools
from datetime import datetime, timedelta

# =====================================================
# CONSTANTS:
# =====================================================


COST_DICT = {'infr':3000, 'civ':10800, 'mil':7200}

GAME_START = datetime(1935,12,31)

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

                    'Капитан_индустрии':{'infr':0.1, 'civ':0.1, 'mil':0, 'tag':'capt'},
                    'Капитан_индустрии_уволен':{'infr':0, 'civ':0, 'mil':0, 'tag':'capt'},

                    'Военный_магнат':{'infr':0, 'civ':0, 'mil':0.1, 'tag':'magnat'},
                    'Военный_магнат_уволен':{'infr':0, 'civ':0, 'mil':0, 'tag':'magnat'},

                     }  

# =====================================================

class BuildSimulator():

    def __init__(self):
        pass

        # self.build_order = build_order

    def reset(self):
        self.obj_built = {'infr':0, 'civ':0, 'mil':0}
        self.laws_current = {}
        self.progress = []

        self.laws_timeline = laws_timeline[:][:]
        
    # -----------------------------------------------------

    def get_day_to_change_law(self): 

        if len(self.laws_timeline):
            day_to_change_law_datetime = self.laws_timeline[0][0]
            day_to_change_law = (day_to_change_law_datetime - GAME_START).days
        else:
            day_to_change_law = -1
        return day_to_change_law

    def laws_current_change(self):

        laws_to_change = self.laws_timeline[0][1]
        
        is_cons_goods_were_changed, optional_str = False, ''
        for law in laws_to_change:

            tag = LAWS_MODIFICATORS[law]['tag']

            law_old = self.laws_current.get(tag, 'None (1st change)')
            optional_str += 'Law was changed: %s -> %s\n' %(law_old, law)

            self.laws_current[tag] = law

            if tag == 'econ':
                is_cons_goods_were_changed = True

        self.laws_timeline.pop(0) 

        return is_cons_goods_were_changed, optional_str.rstrip()

    # -----------------------------------------------------
    
    def progress_add_new_line(self):
        if len(self.build_order): 
            self.progress.append([self.build_order.pop(0), 0])
            
            if not len(self.build_order): # частный случай симуляции - максимизация воензаводов
                self.build_order.append('mil')

    def progress_change_lines_num(self, civ_for_lines): # из-за изменения закона ТНП или постройки нового объекта изменилось число линий, доступных для стройки

        lines_num_diff = len(civ_for_lines) - len(self.progress)
        # print('Here', civ_for_lines)
        
        if lines_num_diff < 0: # сценарий уменьшения числа линий (по каким-то причинам)
            for __ in range(abs(lines_num_diff)):
                self.build_order.insert(0, self.progress.pop()[0])

        elif lines_num_diff > 0: # сценарий увеличения числа линий
            for __ in range(lines_num_diff):
                self.progress_add_new_line()  

    def progress_shift_lines(self, line_idx): # закончилось строительство в линии line_idx
        self.progress.pop(line_idx)
        self.progress_add_new_line()  

    # -----------------------------------------------------

    def get_cons_goods_penalty(self): # нужно менять только при is_cons_goods_law_changed

        cons_goods_law = self.laws_current.get('econ', 'There is no ConsGoods law in laws_current!')
        cons_goods_penalty =  LAWS_MODIFICATORS[cons_goods_law]['cons_goods_penalty']
        return cons_goods_penalty 

    def get_civ_available(self, cons_goods_penalty):

        civ_total_num = obj_start['civ'] + self.obj_built['civ'] + civ_trade_av
        mil_total_num = obj_start['mil'] + self.obj_built['mil'] 
        all_total_num = civ_total_num + mil_total_num

        civ_cons_goods_required = math.ceil(all_total_num * (cons_goods_penalty))
        civ_available = civ_total_num - civ_cons_goods_required

        return civ_available

    def get_civ_for_lines(self, cons_goods_penalty):

        civ_available = self.get_civ_available(cons_goods_penalty)
        civ_for_lines = [15 for item in range(civ_available // 15)]
        if civ_available % 15: 
            civ_for_lines.append(civ_available % 15)

        return civ_for_lines
  
    # -----------------------------------------------------

    def get_build_bonus(self): 

        build_bonus = {'infr':1, 'civ':1, 'mil':1}

        for key in build_bonus:
            for value in self.laws_current.values():
                build_bonus[key] += LAWS_MODIFICATORS[value][key]
            build_bonus[key] = round(build_bonus[key], 3)

        return build_bonus

    def get_progress_per_day(self): # по сути синоним с build_bonus

        progress_per_day = {'infr':0, 'civ':0, 'mil':1}
        build_bonus = self.get_build_bonus()

        for obj_type, bonus in build_bonus.items():
            progress_per_day[obj_type] = 5 * bonus 
            if obj_type != 'infr':
                progress_per_day[obj_type] *= INFR_BONUS_AV
            progress_per_day[obj_type] = round(progress_per_day[obj_type], 3)

        return progress_per_day
    
    # -----------------------------------------------------

    def check_object_completed(self, line_idx, line_data):

        obj_type, build_points = line_data
        is_object_completed, optional_str = False, ''

        if build_points >= COST_DICT[obj_type]:
            self.obj_built[obj_type] += 1
            
            optional_str = 'Progress: %s' %self.progress
            optional_str += '\nObject "%s" #%i is completed in cell %i' %(obj_type, self.obj_built[obj_type], line_idx)
            is_object_completed = True

        return is_object_completed, optional_str
            
    # -----------------------------------------------------

    def printout(self, optional_str, day, day_to_change_law, cons_goods_penalty, progress_per_day, civ_for_lines):
        print('\nDay', day)
        print(optional_str)
    
        print('CurrentLaws', self.laws_current)
        # print('LawsTimeline', self.laws_timeline) 
        print('Day2ChangeLaw', day_to_change_law)

        print('ConsGoods', cons_goods_penalty)

        print('BuildBonuses', self.get_build_bonus())
        print('ProgrPerDay', progress_per_day)

        print('Civ4Lines', civ_for_lines)
        print('Progress', self.progress)

        print('ObjBuilt', self.obj_built)
        print('BuildOrder', self.build_order)

    # -----------------------------------------------------

    # def quit_trigger(self, *args):
    #     return args[0] > 365 * 5
    # if self.quit_trigger(day): 

    def build_sim(self, build_order, day_end=None):

        self.reset()
        self.build_order = build_order
        day_to_change_law = self.get_day_to_change_law() 

        # print(self.build_order)
        # print(self.laws_timeline)

        x_coord, y_coord = [], []

        for day in itertools.count(1): 

            # --------------------------------------------
            # чек изменения закона:
            # --------------------------------------------

            if day == day_to_change_law:

                is_cons_goods_were_changed, optional_str = self.laws_current_change()      
                if is_cons_goods_were_changed: # закон на ТНП был изменен

                    cons_goods_penalty = self.get_cons_goods_penalty()
                    civ_for_lines = self.get_civ_for_lines(cons_goods_penalty)
                    self.progress_change_lines_num(civ_for_lines)

                progress_per_day = self.get_progress_per_day() 
                day_to_change_law = self.get_day_to_change_law() 

                # self.printout(optional_str, day, day_to_change_law, cons_goods_penalty, progress_per_day, civ_for_lines)

            # if day == 1:
            #     assert 'cons_goods_penalty' in locals(), 'В 1й день должен быть определен штраф ТНП!' 

            # --------------------------------------------
            # чек постройки объектов
            # --------------------------------------------

            for line_idx, line_data in enumerate(self.progress):

                is_object_completed, optional_str = self.check_object_completed(line_idx, line_data)
                if is_object_completed:

                    self.progress_shift_lines(line_idx)
                    civ_for_lines = self.get_civ_for_lines(cons_goods_penalty)
                    self.progress_change_lines_num(civ_for_lines)

                    # self.printout(optional_str, day, day_to_change_law, cons_goods_penalty, progress_per_day, civ_for_lines)


                    if line_data[0] == 'mil':
                        x_coord.append(day)
                        y_coord.append(self.obj_built['mil'])

            # --------------------------------------------
            # изменение прогресса ячеек:
            # --------------------------------------------

            for line_idx, line in enumerate(civ_for_lines):
                if len(self.progress) > line_idx: # при исчерпании build_order могут быть лишнии линни civ_for_lines относительно progress
                    obj_type = self.progress[line_idx][0]
                    self.progress[line_idx][1] += progress_per_day[obj_type] * line

                    self.progress[line_idx][1] = round(self.progress[line_idx][1], 3)

            # --------------------------------------------
            # выход из цикла:
            # --------------------------------------------

            if day_end:
                quit_trigger = day == day_end # выход в обозначенный день

            else:
                quit_trigger = not(len(self.build_order)) and not len(self.progress) # конец строительства build_order
                
            if quit_trigger:
                return x_coord, y_coord
                # print(day)


    def vizualize_efficiency(self, num_factories_list, day_end):

        for num_factories in num_factories_list:

            build_order = ['civ' for __ in range(num_factories)]
            x_coord, y_coord = self.build_sim(build_order, day_end)

            plt.plot(x_coord, y_coord, label = 'factories_build: %i' %num_factories)

        plt.title('Building Efficiency')
        plt.xlabel('Days')
        plt.ylabel('Military factories number')
        plt.legend()
        plt.show()


    def find_mil_extremum(self, day_end, mil_built_shift=25):
    
        mil_built_max, civ_built_optimum, day_1st_mil = 0, 0, 0
        x_coord, y_coord = [], []
        
        for civ_built in itertools.count(1): 

            build_order = ['civ' for __ in range(civ_built)]
            x_coord_temp, y_coord_temp = self.build_sim(build_order, day_end)

            if len(y_coord_temp) < mil_built_shift: # не делаем лишнюю работу, когда результат и так уже понятен
                break

            mil_built = y_coord_temp[-1]
            x_coord.append(civ_built)
            y_coord.append(mil_built)

            if mil_built > mil_built_max:
                mil_built_max, civ_built_optimum, day_1st_mil = mil_built, civ_built, x_coord_temp[0]

        print('Optimum: %i factories_build in %i days => %i day_military_f_1st => %i military_f_build' %(civ_built_optimum, day_end, day_1st_mil, mil_built_max))
        end_date = (GAME_START + timedelta(days=day_end)).date()
        plt.plot(x_coord, y_coord, '.', label = 'Optimum to the day: %s\n%i factories => %i military' %(end_date, civ_built_optimum, mil_built_max))
        plt.title('Finding max num of builded military')
        plt.xlabel('Day of 1st built military factory')
        plt.ylabel('Number of builded military factories')
        plt.legend()
        plt.show()
        # plt.savefig('graph.png')

# =====================================================
# CLIENT
# =====================================================
laws_timeline = [
                 [datetime(1936, 1, 1), ['Только_добровольцы', 'Приоритет_экспорт', 'Гражданская_экономика']], 
                 [datetime(1936, 3, 11), ['Свободная_торговля']], 
                 [datetime(1936, 6, 27), ['Строительство_1']], 
                 [datetime(1937, 4, 22), ['Строительство_2']], 
                 [datetime(1937, 12, 1), ['Военная_экономика']],
                 # [1200, ['Строительство_3']] 
                ]

INFR_BONUS_AV = 1.5

obj_start = {'civ':42, 'mil':36}
civ_trade_av = 10 
infrastacture_av = 1.6

# fact_num = 15
# build_order = ['civ' for __ in range(fact_num)]

day_end = 365*5
a = BuildSimulator()
# a.build_sim(['civ' for __ in range(10)])
# a.vizualize_efficiency([10,30,50], day_end)
a.find_mil_extremum(day_end)

# b = BuildSimulator()
# print(b.laws_current)
# print(b.progress)
# =====================================================
