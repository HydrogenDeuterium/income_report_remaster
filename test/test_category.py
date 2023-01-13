from copy import deepcopy

import pytest

from src.category import *


def test_filter():
    # 带多行输入的测试怎么写啊
    pass


def test_season():
    assert get_season(6) == '夏季'
    assert get_season(3) == '春秋'
    assert get_season(1) == '冬季'
    with pytest.raises(AssertionError):
        get_season(0)


base = BaseCategory('测试')
base.last = 789
base.cost = 123
base.budget = lambda: 456


class TestBase:
    
    def test_next(self):
        assert base.next() == 456 + 789 - 123
    
    def test_format(self):
        # 上升趋势
        b = deepcopy(base)
        assert format(b) == '- 测试: 123 | 456 +789 = 1122 ↑\n'
        # 波折趋势
        b.cost = 457
        assert format(b) == '- 测试: 457 | 456 +789 = 788\n'
        # 短路趋势
        b.last = 454
        assert format(b) == '- 测试: 457 | 456 +454 = 453\n'
        # 下降趋势
        b.last = -500
        assert format(b) == '- 测试: 457 | 456 -500 = -501 ↓\n'
