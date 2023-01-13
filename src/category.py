from abc import abstractmethod
from decimal import Decimal
from functools import lru_cache
from typing import Sequence, TypeVar

Price = TypeVar("Price", Decimal, float, int)
sys_input = input


def filter_input(*args, **kwargs) -> str:
    """过滤输入中的空行和井号开头的行。注意空格后带井号不会被过滤。"""
    while ret := sys_input(*args, **kwargs):
        if not ret.startswith('#'):
            return ret


def get_season(month: int) -> str:
    match month:
        case 6 | 7 | 8 | 9:
            return '夏季'
        case 10 | 3 | 4 | 5:
            return '春秋'
        case 11 | 12 | 1 | 2:
            return '冬季'
        case _:
            raise AssertionError(f'月份错误:{month=},应为1-12!')


class BaseCategory:
    # 类别名称，上月结转，本月花费，本月预算，（至）下月结转
    __slots__ = ['name', 'last', 'cost', 'budget', 'next']
    
    def __init__(self, name: str):
        self.name = name
    
    def __format__(self, format_spec=''):
        return f'- {self.name}: {self.cost} | {self.budget()} '\
               f'{self.last:+} = {self.next()}{self.advice()}\n'
    
    # 防止 IDE 报 warning
    @abstractmethod
    def budget(self, *args):
        pass
    
    def next(self):
        return self.budget() + self.last - self.cost
    
    def advice(self) -> str:
        # 结转绝对值较小;不加下划线 IDE 会 warning
        if abs(next_ := self.next()) <= self.cost:
            return ''
        # 结余不断增长
        if 0 < self.last < next_:
            return ' ↑'
        # 赤字不断增长
        if next_ < self.last < 0:
            return ' ↓'
        return ''


# 某个月的月份，外出或在校天数，在家天数
# 不加 bound 为啥会报错捏？
MonthOutHome = TypeVar('MonthOutHome', bound=tuple[int, int, int])


# 子类别
class SubCategory(BaseCategory):
    def __init__(self, name, last, rule):
        super().__init__(name)
        price = input(f'{self.name}:\n')
        self.cost = Decimal(f'{price:.2f}')
        self.last = last
        # budget 计算 rule
        self.rule = rule
    
    def __repr__(self):
        return f'<Subcategory: {self.name}: {self.cost} | {self.last:+} >'
    
    @lru_cache
    def budget(self, day: MonthOutHome):
        month, out, home = day
        season = get_season(month)
        
        def special(rule, n=4):
            per_day = rule['基础']
            additional = rule.get(season)
            if additional:
                # additional['算法'] like: 'n+2/n' or '6-n/n', ensured safe
                extra = additional['在校'] * eval(additional['算法'], {'n': n})
                # print(f'[DEBUG]{self.name}费用：基础：{per_day}，额外:{extra}')
                per_day += extra
            return per_day * out
        
        rule_map = {
            '月结': lambda rule: rule['每月'],
            '日结': lambda rule: rule['在校'] * out + rule.get('在家', 0) * home,
            '季节': lambda rule: rule['在校'][season] * out + rule.get('在家', 0) * home,
            '特殊': special
        }
        
        calculator = rule_map[self.rule['类型']]
        ret = Decimal(f'{calculator(self.rule):.2f}')
        return ret


# 大类别
class Category(BaseCategory):
    def __init__(self, name, name_last_rule: Sequence[tuple[str, Price, dict]]):
        super().__init__(name)
        self.subs = [SubCategory(name, last, rule) for name, last, rule in name_last_rule]
    
    def __repr__(self):
        return f'<Category: {self.name}: {[sub.name for sub in self.subs]}>'
    
    def budget(self, *args):
        return sum(_.budget for _ in self.subs)
    
    @property
    def cost(self):
        return sum(_.cost for _ in self.subs)
    
    def format(self):
        return BaseCategory.__format__(self)
    
    def __format__(self, format_spec=''):
        base_categories: list[BaseCategory] = [self]
        base_categories += self.subs
        # Returns like:
        # '''- xxx
        # \t- sub_xxx1'''
        # \t- sub_xxx2
        # \t- sub_xxx3
        # Pycharm 有 bug，会认为 __format__() 要传入 str
        # return '\n\t'.join(map(BaseCategory.__format__, base_categories))
        return '\n\t'.join(map(lambda x: BaseCategory.__format__(x), base_categories))
