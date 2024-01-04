from decimal import Decimal

import util
from category import Category, filter_input
from date import get_month_days

year, months_and_days = get_month_days('202312')
last_month = (months_and_days[0][0] - 2) % 12 + 1
last_year = year - int(last_month == 12)

if __debug__:
    last_data = {
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
    cost_data = {
        '吃饭':     Decimal('905.64'),
        '饮料':     Decimal('15684.58'),
        '水果牛奶': Decimal('303.93'),
        '零食冷饮': Decimal('152.94'),
        '耐用品':   Decimal('1002.39'),
        '服装外形': Decimal('511.96'),
        '交通物流': Decimal('782.40'),
        '医疗':     Decimal('228.57'),
        '日用消耗': Decimal('69.41'),
        '赠礼':     Decimal('558.52'),
        '软件服务': Decimal('638.97'),
        '文具资料': Decimal('602.89'),
        '小说':     Decimal('282.10'),
        '视频游戏': Decimal('69.66'),
        '其它娱乐': Decimal('142.22'),
        '主机':     Decimal('3582.95'),
        '配件':     Decimal('131.68'),
        '洗衣':     Decimal('31.30'),
        '电力':     Decimal('1100.50'),
        '其他':     Decimal('56.55'),
        '房租':     Decimal('10000.00')
    }
else:
    last_data = util.get_last(last_year, last_month)
    cost_data = {k: filter_input(k) for k in util.budget_data.keys()}

categories = [Category(k, v) for k, v in util.budget_data.items()]

for c in categories:
    for s in c.subs:
        s.set_last(last_data)
        s.set_cost(cost_data)
        s.budget(months_and_days[0])

total = ','.join(str(sum(j.values())) for i,j in months_and_days)
mul = {1: '1', 3: '1.7', 12: '3.5'}[len(months_and_days)]
budget_text = ''.join(c.__format__( mul) for c in categories)

template = util.get_template("季报表头.md")
head = template.render(
    year=year,
    month='Q4',
    total=total,
    fenxiangzhichu=budget_text,
    categories=categories)
pass
