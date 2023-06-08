from src.category import *
from src.util import get_template
from test_category import main_rule

template = get_template('test')

assert True

cat = Category('测试', [
    ('日结', 10, main_rule['饮食']['吃饭'], 10),
    ('月结', 20, main_rule['生活']['服装外形'], 30),
    ('季度月结', 30, main_rule['杂费']['洗衣'], 50),
    ('特殊', 40, main_rule['杂费']['电力'], 57)], )

for s in cat.subs:
    s.budget((1, 10, 20))


def test_data():
    assert [format(s, '1') for s in cat.subs] == [
        '- 日结: 10 | 501.00 +10 = 501.00 ↑\n',
        '- 月结: 30 | 180.00 +20 = 170.00 ↑\n',
        '- 季度月结: 50 | 9.00 +30 = -11.00\n',
        '- 特殊: 57 | 44.40 +40 = 27.40\n']


def test_callmethod():
    assert [f'{subcat.name}: {subcat.next()}' for subcat in cat.subs] == [
        '日结: 501.00', '月结: 170.00', '季度月结: -11.00', '特殊: 27.40']


def test_output():
    tail = template.render(
        category=cat
    )
    # print(tail)
    assert tail == '- 测试: 687.40\n' \
                   '  - 日结: 501.00\n' \
                   '  - 月结: 170.00\n' \
                   '  - 季度月结: -11.00\n' \
                   '  - 特殊: 27.40'
