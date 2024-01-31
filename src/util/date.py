import re
import typing

from category import filter_input, MonthAndDays
from util import budget_fields, smart_import


def get_months(s: str) -> list[int]:
    """
    月份从 1 开始。
    'yr'->1,2,3,4,5,6,7,8,9,10,11,12
    'q1'->1,2,3
    '3'->3
    'Q3'->7,8,9
    """
    s = s.lower()
    if s == 'yr':
        months = list(range(1, 13))
    elif s.startswith('q'):
        quarter = int(s[1])
        months = list(range(quarter * 3 - 2, quarter * 3 + 1))
    else:
        months = [int(s)]
    return months


def yearmonth_parser(text) -> (int, list[str]):
    """
    year,month->year,list[month,dict[dayname,day_count]]
     'yr'->1,2,3,4,5,6,7,8,9,10,11,12
    'q1'->1,2,3
    '3'->3
    'Q3'->7,8,9
    """
    # 20yr->20+yr 20Q1->20+q1,2011->20+11
    yearmonth = re.search(r"(\d{4})(\d{2}|q[1-4]|yr)", text)
    assert yearmonth, "输入格式不正确！"
    
    year, smonths = yearmonth.groups()
    
    try:
        if smonths == 'yr':
            months = list(range(1, 13))
        elif smonths.startswith('q'):
            quarter = int(smonths[1])
            months = list(range(quarter * 3 - 2, quarter * 3 + 1))
        else:
            months = [int(smonths)]
    except TypeError:
        raise ValueError(f"输入格式不正确！{smonths}")
    
    return int(year), months


def get_month_days(yearmonth=None, *, _input=filter_input) -> (int, list[MonthAndDays]):
    yearmonth = (yearmonth or _input("year&month(YYYYMM):")).lower()
    year, months = yearmonth_parser(yearmonth)
    
    month_and_dayses: list[MonthAndDays] = []
    if len(months) == 1:
        m = months[0]
        result_map = {}
        if __debug__:
            result_map = {'home': 4, 'out': 27}
        else:
            for i in budget_fields:
                if i == 'default':
                    continue
                text = filter_input(f'{m}月{i}天数')
                result_map[i] = int(text)
        
        _DAYS_IN_MONTHS = (..., 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
        result_map['default'] = _DAYS_IN_MONTHS[m] - sum(result_map.values())
        month_and_dayses.append((m, result_map))
        return int(year), month_and_dayses
    
    # len(months) > 1
    for m in months:
        ast: list[dict] = smart_import(f"{year}月报/{year%100}{m:02}.md", "md")
        try:
            for _ in ast:
                if _['type'] == 'paragraph':
                    text = _['children'][0]['raw']
                    break
            else:
                raise EOFError('输入的文件不正确')
        except KeyError as e:
            raise e
        search = re.search(r'本月共 ?(\d+) ?天，其中在校 (\d+) 天，在家 (\d+) 天。', text)
        assert search
        total, zaixiao, zaijia = map(int, search.groups())
        month_and_dayses.append((m, {'default': total - zaixiao - zaijia, 'out': zaixiao, 'home': zaijia}))
    
    return int(year), month_and_dayses
