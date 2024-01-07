import os
import shutil
from os.path import join as opj
from copy import deepcopy
from decimal import Decimal

import util
from category import Category, filter_input
from date import get_next
from util.date import get_month_days

import sys

if sys.argv[1] == 'file':
    pass

year, months_and_days = get_month_days('2023Q4')
last_month = (months_and_days[0][0] - 2) % 12 + 1
last_year = year - int(last_month == 12)

# TODO 根据参数从文件或 stdin 读取
if __debug__:
    cost_data = {
        '吃饭':     Decimal('3050.80'),
        '饮料':     Decimal('388.13'),
        '水果牛奶': Decimal('251.97'),
        '零食冷饮': Decimal('270.23'),
        
        '耐用品':   Decimal('1722.31'),
        '服装外形': Decimal('1401.70'),
        '交通物流': Decimal('793.94'),
        '医疗':     Decimal('215'),
        '日用消耗': Decimal('120.9'),
        '赠礼':     Decimal('904'),
        '房租':     Decimal('293.33'),
        
        '软件服务': Decimal('257.1'),
        '文具资料': Decimal('1'),
        
        '小说':     Decimal('258'),
        '视频游戏': Decimal('445.5'),
        '其它娱乐': Decimal('671.32'),
        
        '主机':     Decimal('4506.89'),
        '配件':     Decimal('17.8'),
        
        '洗衣':     Decimal('0'),
        '电力':     Decimal('346.19'),
        '其他':     Decimal('264.59'),
    }
else:
    cost_data = {k: filter_input(k) for k in util.budget_data.keys()}

last_data = util.get_last(last_year, last_month)
categories = [Category(k, v) for k, v in util.budget_data.items()]

for c in categories:
    for s in c.subs:
        s.set_last(last_data)
        s.set_cost(cost_data)
        s.budget(months_and_days)

total = ','.join(str(sum(j.values())) for i, j in months_and_days)
mul = {1: '1', 3: '1.7', 12: '3.5'}[len(months_and_days)]
budget_text = ''.join(c.__format__(mul) for c in categories)

template = util.get_template("季报表头.md")
head = template.render(
    year=year,
    month='Q4',
    total=total,
    fenxiangzhichu=budget_text,
    categories=categories)

with open(tmp := './temp.md', 'w', encoding="utf-8") as f:
    f.write(head)

try:
    input('修改好了就回车继续')
except EOFError:
    pass
next_month_out_home = get_next(months_and_days)
next_categories = deepcopy(categories)
for cat in next_categories:
    for sub in cat.subs:
        # update cache
        sub.budget(next_month_out_home)
outs: tuple
homes: tuple
# _, outs, homes = zip(*next_month_out_home)
match len(months_and_days):
    case 1:
        cycle_name = months_and_days[0][0]
        template = util.get_template('月报表尾.md')
    case 3:
        cycle_name = f'Q{months_and_days[-1][0] // 3}'
        template = util.get_template('季报表尾.md')
    case 12:
        cycle_name = 'YR'
        template = util.get_template('年报表尾.md')
    case _:
        raise AssertionError
tail = template.render(
    # days=sum(outs) + sum(homes),
    # out=sum(outs),
    # home=sum(homes),
    categories=categories,
    next_categories=next_categories,
    total_budget=sum(i.budget() for i in categories),
    total_next=sum(i.next() for i in categories),
)

with open(tmp, 'a', encoding="utf-8") as f:
    f.write(tail)

try:
    input('确认完成 移动文件')
except EOFError:
    pass

path = opj(util.file_dir, f'{year}月报')
if not os.path.exists(path):
    os.mkdir(path)

target = opj(path, f'{year % 100}{cycle_name:02}.md')
print(target)
shutil.move(tmp, target)
