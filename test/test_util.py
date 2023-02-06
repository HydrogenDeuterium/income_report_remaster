import contextlib

import os

import pytest

from src.util import *


@contextlib.contextmanager
def cd_parent():
    cwd = os.getcwd()
    os.chdir('..')
    try:
        yield
    finally:
        os.chdir(cwd)


def test_get_month():
    assert get_months('01') == [1]
    assert get_months('q1') == [1, 2, 3]
    assert get_months('Q1') == [1, 2, 3]
    assert get_months('yr') == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    assert get_months('YR') == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    assert get_months('yR') == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    assert get_months('Yr') == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]


def test_get_month_days():
    with pytest.raises(AssertionError):
        get_month_days('!@#$%^&', test=True)
    assert get_month_days('2022yr', test=True) == (2022, [
        (1, 23, 8), (2, 25, 5), (3, 31, 0), (4, 25, 5),
        (5, 25, 5), (6, 25, 5), (7, 11, 20), (8, 28, 3),
        (9, 25, 5), (10, 31, 0), (11, 25, 5), (12, 26, 5)])


def test_smart_import():
    toml = smart_import('budget_test.toml', 'toml')
    assert toml == {
        'version': 'test',
        '预算':    {
            '饮食': {
                '吃饭':     {'类型': '日结', '在校': 39, '在家': 5.55},
                '饮料':     {'类型': '日结', '在校': 7.1, '在家': 0.2},
                '水果牛奶': {'类型': '日结', '在校': 4, '在家': 3.9},
                '零食冷饮': {'类型': '日结', '在校': 2.1}
            },
            '生活': {
                '耐用品':   {'类型': '日结', '在校': 2.65},
                '服装外形': {'类型': '月结', '每月': 180},
                '交通物流': {'类型': '月结', '每月': 115},
                '医疗':     {'类型': '月结', '每月': 33},
                '日用消耗': {'类型': '月结', '每月': 27},
                '赠礼':     {'类型': '月结', '每月': 20}
            },
            '学习': {'软件服务': {'类型': '月结', '每月': 130}, '文具资料': {'类型': '月结', '每月': 20.5}},
            '娱乐': {
                '小说':     {'类型': '月结', '每月': 78},
                '视频游戏': {'类型': '月结', '每月': 50},
                '其它娱乐': {'类型': '月结', '每月': 30}
            },
            '数码': {'主机': {'类型': '月结', '每月': 330}, '配件': {'类型': '月结', '每月': 23}},
            '杂费': {
                '洗衣': {'类型': '季节', '在校': {'夏季': 1.4, '春秋': 1.25, '冬季': 0.9}},
                '电力': {
                    '类型': '特殊',
                    '基础': 0.19,
                    '夏季': {'在校': 0.9, '算法': 'n+2/n'},
                    '冬季': {'在校': 0.85, '算法': '6-n/n'}
                },
                '其他': {'类型': '月结', '每月': 73}
            }
        }
    }
    md = smart_import('2022月报/2210.md')
    
    with cd_parent():
        md2 = smart_import('2022月报/2210.md')
    assert md == md2


def test_get_last():
    ret = get_last(2022, 10)
    assert ret == {
        '吃饭':     Decimal('-905.64'),
        '饮料':     Decimal('-184.58'),
        '水果牛奶': Decimal('-303.93'),
        '零食冷饮': Decimal('152.94'),
        '耐用品':   Decimal('1002.39'),
        '服装外形': Decimal('-511.96'),
        '交通物流': Decimal('-782.40'),
        '医疗':     Decimal('228.57'),
        '日用消耗': Decimal('-69.41'),
        '赠礼':     Decimal('-558.52'),
        '软件服务': Decimal('-638.97'),
        '文具资料': Decimal('-602.89'),
        '小说':     Decimal('282.10'),
        '视频游戏': Decimal('-69.66'),
        '其它娱乐': Decimal('-142.22'),
        '主机':     Decimal('-3582.95'),
        '配件':     Decimal('131.68'),
        '洗衣':     Decimal('-31.30'),
        '电力':     Decimal('1100.50'),
        '其他':     Decimal('-56.55')
    }


def test_get_struct():
    struct = get_structure(2022, 10, test=True)
    assert repr(struct) == (
        "[<Category: 饮食: ['吃饭', '饮料', '水果牛奶', '零食冷饮']>, "
        "<Category: 生活: ['耐用品', '服装外形', '交通物流', '医疗', '日用消耗', '赠礼']>, "
        "<Category: 学习: ['软件服务', '文具资料']>, "
        "<Category: 娱乐: ['小说', '视频游戏', '其它娱乐']>, "
        "<Category: 数码: ['主机', '配件']>, "
        "<Category: 杂费: ['洗衣', '电力', '其他']>]")


def test_get_template():
    t1 = get_template('下月预算模板.md')
    with cd_parent():
        t2 = get_template('下月预算模板.md')
    assert t1.render() == t2.render()


def test_get_next():
    data = list(zip(range(1, 13), [0] * 12, [0] * 12))
    ret = get_next(data)
    assert ret == [(1, 23, 8), (2, 16, 12), (3, 31, 0), (4, 30, 0),
                   (5, 31, 0), (6, 30, 0), (7, 25, 6), (8, 5, 26),
                   (9, 30, 0), (10, 28, 3), (11, 30, 0), (12, 31, 0)]
