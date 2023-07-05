from builtins import input
import pytest

from abc import abstractmethod
from decimal import Decimal
from typing import Sequence, TypeAlias, TypeVar

Price = TypeVar("Price", Decimal, float, int)


def filter_input(*args, in_=input, **kwargs) -> str:
    """过滤输入中的空行和井号开头的行。注意空格后带井号不会被过滤。"""
    while (ret := in_(*args, **kwargs)) == ''\
            or ret.startswith('#'):
        pass
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
    # __slots__ = ['name', 'last', 'cost', 'budget', 'next']
    
    def __init__(self, name: str):
        self.name = name
        self.last = None
        self.cost = None
    
    def __format__(self, format_spec='1'):
        ret = f'- {self.name}: {self.cost} | {self.budget()} '\
              f'{self.last:+} = {self.next()}{self.advice(format_spec)}\n'
        
        return ret
    
    @pytest.mark.skipif(reason='abstract placeholder method')
    # 防止 IDE 报 warning
    @abstractmethod
    def budget(self, *args):
        pass
    
    def next(self):
        ret = self.budget() + self.last - self.cost
        # print(f'[DEBUG]{self.name}:{self.budget()=},{self.last=},{self.cost=},{ret=}')
        return ret
    
    def advice(self, spec='1') -> str:
        # 结转绝对值较小;不加下划线 IDE 会 warning
        multiplier = Decimal(spec or '1')
        abs_next_mul = abs(next_ := self.next()) * multiplier
        if abs(next_) < self.cost < abs_next_mul:
            print(f'[DEBUG]catch advice optimize:{self.name}')
        if abs_next_mul <= self.cost:
            return ''
        # 结余不断增长
        if 0 < self.last < next_:
            return ' ↑'
        # 赤字不断增长
        if next_ < self.last < 0:
            return ' ↓'
        if __debug__ and (spec or "1") != '1':
            print(f"[DEBUG]{self.name} situation not met, no advice")
        
        # 在允许范围内的波动
        return ''


# 某个月的月份，以及不同工作条件下对应的日期数量
# 不加 bound 为啥会报错捏？
# MonthOutHome = TypeVar('MonthOutHome', bound=tuple[int, int, int])

MonthAndDays: TypeAlias = tuple[int, dict[str, int]]


# 子类别
class SubCategory(BaseCategory):
    def __init__(self, name, last, rule, cost=None):
        super().__init__(name)
        self.cache = None
        if cost is None:
            price = filter_input(f'{self.name}:\n')
            self.cost = Decimal(f'{Decimal(price):.2f}')
        else:
            self.cost = cost
        self.last = last
        # budget 计算 rule
        self.rule = rule
    
    def __repr__(self):
        return f'<Subcategory {self.name}: {self.cost}|{self.last:+}>'
    
    def budget_by_month(self, data: MonthAndDays):
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        try:
            month, day_map = data
        except TypeError:
            pass
        season = get_season(month)
        
        def dately(rule):
            ret_d = 0
            for k, v in day_map.items():
                try:
                    ret_d += rule[k] * v
                except KeyError:
                    pass
            if 'default' not in day_map:
                default_days = days_in_month[month] - sum(day_map.values())
                assert default_days > 0
                ret_d += rule['default'] * default_days
            
            return ret_d
        
        def seasonal(rule) -> Price:
            # 默认开支与季节有关
            # TODO 感觉这里有点乱 要再理一下
            ret_s = 0
            for k, v in day_map.items():
                if k != 'default':
                    try:
                        ret_s += rule.get(k, 0) * v
                    except KeyError:
                        pass
                    except TypeError:
                        pass
            default_days = day_map.get('default') or days_in_month[month] - sum(day_map.values())
            try:
                ret_s += rule['default'][season] * default_days
            except KeyError:
                ret_s += rule.get('default', 0) * default_days
            return ret_s
        
        # 按四人同住计算，但怎么传入同住人数，目前没想好
        def special(rule, n=4):
            assert False, "暂时弃用"
            # per_day = rule['基础']
            # additional = rule.get(season)
            # if additional:
            #     # additional['算法'] like: 'n+2/n' or '6-n/n', ensured safe
            #     extra = additional['在校'] * eval(additional['算法'], {'n': n})
            #     # print(f'[DEBUG]{self.name}费用：基础：{per_day * out:.2f}，额外:{extra * out:.2f}')
            #     per_day += extra
            # else:
            #     # print(f'[DEBUG]{self.name}费用：基础：{per_day * out:.2f}，额外: 0')
            #     pass
            # return per_day * out
        
        rule_map = {
            '月结': lambda rule: rule['每月'],
            '日结': dately,
            '季节': seasonal,
            '特殊': special
        }
        
        calculator = rule_map[self.rule['类型']]
        try:
            ret = Decimal(f'{calculator(self.rule):.2f}')
        except TypeError:
            pass
        return ret
    
    # @lru_cache
    def budget(self, days: MonthAndDays = None):
        if not days:
            if self.cache is None:
                raise NameError('No cache!')
            else:
                ret = self.cache
                return ret
        
        if isinstance(days, (dict, tuple)):
            days = [days]
        
        ret = sum(self.budget_by_month(day) for day in days)
        self.cache = ret
        
        return ret


# 最后一个 tuple 是给弱智类型检查擦屁股用的
NameLastRuleCo: TypeAlias = tuple[str, Price, dict, Price] | tuple[str, Price, dict]\
                            | tuple


# 大类别
class Category(BaseCategory):
    def __init__(self, name, name_last_rule: Sequence[NameLastRuleCo]):
        super().__init__(name)
        self.subs = [SubCategory(*name_etc) for name_etc in name_last_rule]
        self.last = sum(_.last for _ in self.subs)
    
    def __repr__(self):
        return f'<Category: {self.name}: {[sub.name for sub in self.subs]}>'
    
    def budget(self, *args):
        return sum(_.budget(*args) for _ in self.subs)
    
    # 没用，但是 super.init 必须要初始化 cost 否则 warn
    @property
    def cost(self):
        return sum(_.cost for _ in self.subs)
    
    @cost.setter
    def cost(self, val):
        pass
    
    # def format(self):
    #     return BaseCategory.__format__(self)
    
    def __format__(self, format_spec='1'):
        base_categories: list[BaseCategory] = [self]
        base_categories += self.subs
        # Returns like:
        # '''- xxx
        # \t- sub_xxx1'''
        # \t- sub_xxx2
        # \t- sub_xxx3
        # Pycharm 有 bug，会认为 __format__() 要传入 str
        # return '\n\t'.join(map(BaseCategory.__format__, base_categories))
        ret = '\t'.join(map(lambda x: BaseCategory.__format__(x, format_spec), base_categories))
        return ret
