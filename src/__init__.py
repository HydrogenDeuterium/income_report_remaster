import argparse
import os
import shutil
from copy import deepcopy
from decimal import Decimal
from os.path import join as opj

import util
from category import Category, filter_input
from date import get_next
from util.date import get_month_days

parser = argparse.ArgumentParser()
parser.add_argument('--file', '-f', metavar='FILENAME', type=str,
                    default=None, required=False)
file = parser.parse_args().file
# if sys.argv[1] == 'file':
#     pass

# TODO 根据参数从文件或 stdin 读取
if file is not None:
    data = util.smart_import(file)
    lines = [line for line in data.splitlines() if not line.startswith('#')]
    line_iter = iter(lines)
    
    yearmonth = next(line_iter)
    year, months_and_days = get_month_days(yearmonth)
    
    days = next(line_iter)
    cost_data = {}
    for v in util.budget_data.values():
        cost_data |= {k: Decimal(next(line_iter)) for k in v.keys()}
else:
    yearmonth = filter_input()
    cost_data = {}
    for v in util.budget_data.values():
        cost_data |= {k: Decimal(filter_input(k)) for k in v.keys()}
        
year, months_and_days = get_month_days(yearmonth)
last_month = (months_and_days[0][0] - 2) % 12 + 1
last_year = year - int(last_month == 12)

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

if len(months_and_days) == 1:
    template = util.get_template("月报表头.md")
elif len(months_and_days) == 3:
    template = util.get_template("季报表头.md")
elif len(months_and_days) == 12:
    template = util.get_template("年报表头.md")
else:
    raise ValueError("len(months_and_days) must be 1, 3 or 12")

head = template.render(
    year=year,
    month=yearmonth[-2:],
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
