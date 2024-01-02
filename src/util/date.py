import re

from category import filter_input, MonthAndDays


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
    yearmonth = re.search(r"(\d{4})(\d{2}|Q[1-4]|YR)", text)
    assert yearmonth, "输入格式不正确！"
    
    year, smonths = yearmonth.groups()[0]
    
    if smonths == 'yr':
        months = list(range(1, 13))
    elif smonths.startswith('q'):
        quarter = int(smonths[1])
        months = list(range(quarter * 3 - 2, quarter * 3 + 1))
    else:
        months = [int(smonths)]
    
    return int(year), months


def get_month_days(yearmonth=None, *, _input=filter_input) -> (int, list[MonthAndDays]):
    yearmonth = yearmonth or _input("year&month(YYYYMM):")
    year, months = yearmonth_parser(yearmonth)
    if len(months) == 1:
        ...
