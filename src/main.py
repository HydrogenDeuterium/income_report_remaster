import shutil

from util import *

year, month_out_homes = get_month_days()

last_month = (month_out_homes[0][0] - 2) % 12 + 1
last_year = year - int(last_month == 12)

categories = get_structure(last_year, last_month)

if __name__ == '__main__':
    pass
    # import viztracer
    
    # with viztracer.VizTracer():
    for i in categories:
        i.budget(month_out_homes)
    
    # 周期长度的平方根
    mul = {1: '1', 3: '1.7', 12: '3.5'}[len(month_out_homes)]
    budget_text = ''.join(format(c, mul) for c in categories)
    
    match len(month_out_homes):
        case 1:
            cycle_name = month_out_homes[0][0]
            template = get_template("月报表头.md")
        case 3:
            cycle_name = f'Q{month_out_homes[-1][0] // 3}'
            template = get_template("季报表头.md")
        case 12:
            cycle_name = 'YR'
            template = get_template("年报表头.md")
        case _:
            raise AssertionError
    
    # 各月总日期
    total = ','.join(str(i[1] + i[2]) for i in month_out_homes)
    # 各月外出日期
    out = ','.join(str(i[1]) for i in month_out_homes)
    # 各月回家日期
    home = ','.join(str(i[2]) for i in month_out_homes)
    
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
    
    input('修改好了就回车继续')
    next_month_out_home = get_next(month_out_homes)
    for cat in categories:
        for sub in cat.subs:
            # update cache
            sub.budget(next_month_out_home)
    outs: tuple
    homes: tuple
    _, outs, homes = zip(*next_month_out_home)
    match len(month_out_homes):
        case 1:
            template = get_template('月报表尾.md')
        case 3:
            template = get_template('季报表尾.md')
        case 12:
            template = get_template('年报表尾.md')
        case _:
            raise AssertionError
    tail = template.render(
        days=sum(outs) + sum(homes),
        out=sum(outs),
        home=sum(homes),
        categories=categories,
        total_budget=sum(i.budget() for i in categories),
        total_next=sum(i.next() for i in categories),
    )
    
    with open(tmp, 'a', encoding="utf-8") as f:
        f.write(tail)
    
    try:
        input('确认完成 移动文件')
    except EOFError:
        pass

    opj = os.path.join
    path = opj(file_dir, f'{year}月报')
    if not os.path.exists(path):
        os.mkdir(path)
    
    target = opj(path, f'{year % 100}{cycle_name:02}.md')
    print(target)
    shutil.move(tmp, target)
