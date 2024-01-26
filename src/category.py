from builtins import input
from decimal import Decimal
from logging import getLogger
from typing import Sequence, TypeAlias, TypeVar

logger = getLogger(__name__)

Price = TypeVar("Price", Decimal, float, int)


def filter_input(*args, in_=input, **kwargs) -> str:
    """过滤输入中的空行和井号开头的行。注意空格后带井号不会被过滤。"""
    while (ret := in_(*args, **kwargs)) == ''\
            or ret.startswith('#'):
        pass
    return ret.strip()


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


MonthAndDays: TypeAlias = tuple[int, dict[str, int]]


# 子类别
class SubCategory:
    def __init__(self, name, rule, last=0, cost=None):
        self.name = name
        self.cache = None
        self.cost = cost
        self.last = last
        
        self.aliases = [self.name]
        if 'alias' in rule:
            self.aliases += rule.pop('alias')
        
        # budget 计算 rule
        self.rule = rule
    
    def __repr__(self):
        return f'<Subcategory {self.name}: {self.cost}|{self.last:+}>'
    
    def set_last(self, last_map):
        for name in self.aliases:
            if name in last_map:
                self.last = last_map[name]
                return
    
    def set_cost(self, cost_map=None):
        if cost_map is None:
            price: str = filter_input(f'{self.name}:\n')
        else:
            for name in self.aliases:
                if name in cost_map:
                    price = cost_map[name]
                    break
            else:
                logger.warning(f'{self.name} with alias {self.aliases} not found in cost_map')
                price = filter_input(f'{self.name}:\n')
        # self.cost = Decimal(f'{Decimal(price):.2f}')
        self.cost = Decimal(price).quantize(Decimal('.01'))
    
    def next(self):
        ret = self.budget() + self.last - self.cost
        # print(f'[DEBUG]{self.name}:{self.budget()=},{self.last=},{self.cost=},{ret=}')
        return ret
    
    def budget_by_month(self, data: MonthAndDays):
        # 月份从 1 开始，不关心闰年
        DAYS_IN_MONTHS = (..., 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
        try:
            month, day_map = data
        except ValueError as e:
            raise e
        
        # for k, v in day_map.items():
        #     day_map[k] = int(v)
        
        season = get_season(month)
        
        def dately(rule):
            value_ = rule['value']
            ret_d = 0
            for k, v in day_map.items():
                # ret_d += rule[k] * v
                try:
                    ret_d += value_.get(k, value_['default']) * v
                except KeyError:
                    print(f'[WARNING]试图请求未设置的默认值：{rule}')
            
            if 'default' not in day_map:
                default_days = DAYS_IN_MONTHS[month] - sum(day_map.values())
                assert default_days >= 0
                # print(f'[WARNING]试图请求未设置的默认值：{rule}')
            
            return ret_d
        
        def seasonal(rule) -> Price:
            # 默认开支与季节有关
            # TODO 感觉这里有点乱 要再理一下
            ret_s = 0
            for k, v in day_map.items():
                if k != 'default':
                    # ret_s += rule.get(k, 0) * v
                    try:
                        # 感觉这里类型标注是有点问题的
                        budget: Price = rule.get(k, 0)
                        if isinstance(budget, dict):
                            budget = budget[season]
                        ret_s += budget * v
                    except KeyError:
                        pass
                    except TypeError:
                        pass
            default_days = day_map.get('default') or DAYS_IN_MONTHS[month] - sum(day_map.values())
            try:
                ret_s += rule['default'][season] * default_days
            except KeyError:
                ret_s += rule.get('default', 0) * default_days
            return ret_s
        
        rule_map = {
            'monthly': lambda rule: rule['value']['default'],
            'daily':   dately,
            'season':  seasonal,
        }
        
        rule = self.rule
        calculator = rule_map[rule['type']]
        try:
            ret = Decimal(f'{calculator(rule):.2f}')
        except TypeError as e:
            print(rule)
            raise e
        return ret
    
    # @lru_cache
    def budget(self, days: MonthAndDays = None):
        if days is None:
            if self.cache is None:
                raise AttributeError('No cache!')
            return self.cache
        
        if isinstance(days, (dict, tuple)):
            days = [days]
        
        # TODO 待调整，现在传给 budget_by_month 的参数有点问题
        ret = sum(self.budget_by_month(day) for day in days)
        self.cache = ret
        
        return ret
    
    def __format__(self, format_spec='1'):
        ret = f'- {self.name}: {self.cost} | {self.budget()} '\
              f'{self.last:+} = {self.next()}{self.advice(format_spec)}\n'
        
        return ret
    
    def advice(self, spec='1') -> str:
        # 结转绝对值较小;不加下划线 IDE 会 warning
        multiplier = Decimal(spec or '1')
        abs_next_mul = abs(next_ := self.next()) * multiplier
        if abs(next_) < self.cost < abs_next_mul:
            print(f'[DEBUG]catch advice optimize:{self.name}')
        if __debug__ and (spec or "1") != '1':
            # print(f"[DEBUG]{self.name} situation not met, no advice")
            pass
        if abs_next_mul <= self.cost or abs(next_) < abs(self.last):
            return ''
        if next_ > 0:
            return ' ↑'
        else:
            return ' ↓'


# 最后一个 tuple 是给弱智类型检查擦屁股用的
NameLastRuleCo: TypeAlias = dict[str, dict[str, str | dict | list]]


# 大类别
class Category:
    def __init__(self, name, name_last_rule: NameLastRuleCo):
        self.name = name
        self.cost = None
        self.subs = [SubCategory(name, value) for name, value in name_last_rule.items()]
    
    def __repr__(self):
        return f'<Category: {self.name}: {[sub.name for sub in self.subs]}>'
    
    def next(self):
        last = sum(_.last for _ in self.subs)
        ret = self.budget() + last - self.cost
        # print(f'[DEBUG]{self.name}:{self.budget()=},{self.last=},{self.cost=},{ret=}')
        return ret
    
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
        base_categories: list[Category | SubCategory] = [self]
        base_categories += self.subs
        # Returns like:
        # '''- xxx
        # \t- sub_xxx1'''
        # \t- sub_xxx2
        # \t- sub_xxx3
        
        last = sum(_.last for _ in self.subs)
        formats = [f'- {self.name}: {self.cost} | {self.budget()} '
                   f'{last:+} = {self.next()}{self.advice(last, format_spec)}\n']
        formats += [format(sub, format_spec) for sub in self.subs]
        ret = '\t'.join(formats)
        return ret
    
    def advice(self, last, spec='1') -> str:
        # 结转绝对值较小;不加下划线 IDE 会 warning
        multiplier = Decimal(spec or '1')
        abs_next_mul = abs(next_ := self.next()) * multiplier
        if abs_next_mul <= self.cost or abs(next_) < abs(last):
            return ''
        if last > 0:
            return ' ↑'
        else:
            return ' ↓'
