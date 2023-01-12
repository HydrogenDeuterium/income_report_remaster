from abc import abstractmethod
from decimal import Decimal
from typing import TypeVar

sys_input = input

Price = TypeVar("Price", Decimal, float, int)


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
    
    @abstractmethod
    def format(self):
        return f'- {self.name}: {self.cost} | {self.budget()} '\
               f'{self.last:+} = {self.next()}{self.advice()}\n'
    
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
    
    # 防止 IDE 报 warning
    @abstractmethod
    def next(self):
        pass
    
    @abstractmethod
    def budget(self):
        pass
