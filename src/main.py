import shutil
from copy import deepcopy

from date import get_month_days, get_next
import util

year, months_and_days = get_month_days()

last_month = (months_and_days[0][0] - 2) % 12 + 1
last_year = year - int(last_month == 12)

categories = util.get_structure(last_year, last_month)
for i in categories:
    i.budget(months_and_days)

import warnings

if __name__ == '__main__':
    warnings.warn('USING A OLD VERSION!!!')
    print(flush=True)
    pass
    # import viztracer
    
    # with viztracer.VizTracer():
    
    # 周期长度的平方根
    mul = {1: '1', 3: '1.7', 12: '3.5'}[len(months_and_days)]
    budget_text = ''.join(format(c, mul) for c in categories)
    
    match len(months_and_days):
        case 1:
            cycle_name = months_and_days[0][0]
            template = util.get_template("月报表头.md")
        case 3:
            cycle_name = f'Q{months_and_days[-1][0] // 3}'
            template = util.get_template("季报表头.md")
        case 12:
            cycle_name = 'YR'
            template = util.get_template("年报表头.md")
        case _:
            raise AssertionError
    
    # 各月总日期
    total = ','.join(str(i[1]['在家'] + i[1]['在校']) for i in months_and_days)
    # 各月外出日期
    out = ','.join(str(i[1]['在校']) for i in months_and_days)
    # 各月回家日期
    home = ','.join(str(i[1]['在家']) for i in months_and_days)
    
    head = template.render(
        year=year,
        month=cycle_name,
        total=total,
        out=out,
        home=home,
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
    _, outs, homes = zip(*next_month_out_home)
    match len(months_and_days):
        case 1:
            template = util.get_template('月报表尾.md')
        case 3:
            template = util.get_template('季报表尾.md')
        case 12:
            template = util.get_template('年报表尾.md')
        case _:
            raise AssertionError
    tail = template.render(
        days=sum(outs) + sum(homes),
        out=sum(outs),
        home=sum(homes),
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
    
    opj = util.os.path.join
    path = opj(util.file_dir, f'{year}月报')
    if not util.os.path.exists(path):
        util.os.mkdir(path)
    
    target = opj(path, f'{year % 100}{cycle_name:02}.md')
    print(target)
    shutil.move(tmp, target)
