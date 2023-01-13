import tomllib

from copy import deepcopy

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
        # 上升趋势，结余
        b = deepcopy(base)
        assert format(b) == '- 测试: 123 | 456 +789 = 1122 ↑\n'
        # 波折趋势
        b.cost = 457
        assert format(b) == '- 测试: 457 | 456 +789 = 788\n'
        # 短路趋势,小幅度波动
        b.last = 454
        assert format(b) == '- 测试: 457 | 456 +454 = 453\n'
        # 下降趋势，赤字
        b.last = -500
        assert format(b) == '- 测试: 457 | 456 -500 = -501 ↓\n'


sub = SubCategory('测试', 132, None, 789, )


class TestSub:
    def test_repr(self):
        assert repr(sub) == '<Subcategory 测试: 789|+132>'
        sub.last = -132
        assert repr(sub) == '<Subcategory 测试: 789|-132>'
    
    def test_budget(self):
        with open('budget_test.toml', 'rb') as f:
            main_rule = tomllib.load(f)['预算']
        
        # 日结
        sub.rule = main_rule['饮食']['吃饭']
        assert sub.budget((1, 10, 20)) == 501
        # 月结
        sub.rule = main_rule['生活']['服装外形']
        assert sub.budget((1, 10, 20)) == 180
        # 季度月结
        sub.rule = main_rule['杂费']['洗衣']
        # 冬，春秋，夏
        assert sub.budget((1, 10, 20)) == 9
        assert sub.budget((3, 10, 20)) == 12.5
        assert sub.budget((6, 10, 20)) == 14
        # 电费
        sub.rule = main_rule['杂费']['电力']
        assert sub.budget((1, 10, 20)) == Decimal('44.40')
        assert sub.budget((3, 10, 20)) == Decimal('1.90')
        assert sub.budget((6, 10, 20)) == Decimal('42.40')
        pass