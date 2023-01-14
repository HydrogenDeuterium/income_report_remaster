import tomllib

import jinja2
import mistune
import re
from decimal import Decimal

from src.category import Category, filter_input, MonthOutHome


def get_months(s: str) -> list[int]:
    """
    'yr'->1,2,3,4,5,6,7,8,9,10,11,12
    'q1'->1,2,3
    '3'->3
    'Q3'->7,8,9
    """
    if s.startswith(('yr', 'YR', 'yR', 'Yr')):
        months = list(range(1, 13))
    elif s.startswith(('q', 'Q')):
        quarter = int(s[1])
        months = list(range(quarter * 3 - 2, quarter * 3 + 1))
    else:
        months = [int(s)]
    return months


def get_month_days(yearmonth=None, *, test=False) -> (int, list[MonthOutHome]):
    """获取年份与每月外出在家信息"""
    if yearmonth is None:
        text = filter_input("year&month(YYYYMM):")
    else:
        text = yearmonth
    # 20yr->20+yr 20Q1->20+q1,2011->20+11
    yearmonth = re.search(r"(\d{4})(\d{2}|[qQ][1-4]|[yY][rR])", text)
    assert yearmonth, "输入格式不正确！"
    
    year = yearmonth.groups()[0]
    months = get_months(yearmonth.groups()[1])
    
    month_out_homes: list[MonthOutHome] = []
    for m in months:
        if test:
            text = '25 5'
        else:
            text = filter_input(f'{m}月出门或在校天数 {m}月在家天数:')
        search = re.search(r"(\d{1,2}) (\d{1,2})", text)
        assert search, "输入格式不正确！"
        out, home = search.groups()
        month_out_homes.append((m, int(out), int(home)))
    return int(year), month_out_homes


def get_last(last_year: int, last_month) -> dict[str, Decimal]:
    """依赖上月月报格式获取各子项上月结余"""
    filename = f'{last_year}月报/{last_year % 100}{last_month :0>2}.md'
    data_ = smart_import(filename)
    
    markdown = mistune.create_markdown(renderer='ast')
    
    s = markdown(data_)[-1]['children']
    subs = []
    for i in s[:-1]:
        subs += i['children'][1]['children']
    
    a = [sub['children'][0]['children'][0]['text'] for sub in subs]
    ret = {}
    for s in a:
        k, v = s.split(':')
        ret[k] = Decimal(v)
    return ret


def smart_import(filename, ext=None):
    match ext:
        case 'toml':
            try:
                with open('../' + filename, 'rb') as f:
                    return tomllib.load(f)
            except FileNotFoundError:
                with open(filename, 'rb') as f:
                    return tomllib.load(f)
        case _:
            try:
                with open('../' + filename, encoding="utf-8") as f:
                    data_ = f.read()
            except FileNotFoundError:
                with open(filename, encoding="utf-8") as f:
                    data_ = f.read()
            return data_


def get_structure(last_year: int, last_month: int, toml='./budget.toml', *, test=False) -> list[Category]:
    """生成结构，写入上月结余和预算规则"""
    items_budgets: dict[str, dict[str, dict]] = smart_import(toml, ext='toml')['预算']
    last_data = get_last(last_year, last_month)
    
    categories = []
    for category_name, dict_subcategory in items_budgets.items():
        name_last_rule_cos = [(name, last_data[name], rule,)
                              for name, rule in dict_subcategory.items()]
        # 写给测试用
        if test:
            name_last_rule_cos = [
                (x + (Decimal('10'),)) for x in name_last_rule_cos]
        
        cat = Category(category_name, name_last_rule_cos)
        categories.append(cat)
        
    return categories


def get_template(filename):
    try:
        return jinja2.Environment(loader=jinja2.FileSystemLoader(
            "./template")).get_template(filename)
    except jinja2.exceptions.TemplateNotFound:
        return jinja2.Environment(loader=jinja2.FileSystemLoader(
            "../template")).get_template(filename)


def get_next(last_month_out_homes: list[MonthOutHome]) -> list[tuple]:
    """预测下一个时间段（月，季，年）在家在校天数"""
    out_map: dict[int, tuple[int, int]] = {
        1: (23, 8), 2: (16, 12), 3: (31, 0), 4: (30, 0), 5: (31, 0), 6: (30, 0),
        7: (25, 6), 8: (5, 26), 9: (30, 0), 10: (28, 3), 11: (30, 0), 12: (31, 0),
    }
    ret = []
    last_month_ = last_month_out_homes[-1][0]
    for i, j in enumerate(last_month_out_homes):
        new_month = (last_month_ + i) % 12 + 1
        # ret.append(tuple([new_month] + out_map[new_month]))
        ret.append((new_month, *out_map[new_month]))
    return ret
