import calendar
import datetime
import re
from util import budget_fields

from workalendar.asia import China

from category import filter_input, MonthAndDays
from util import smart_import


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


def get_month_days(yearmonth=None) -> (int, list[MonthAndDays]):
    """获取年份与每月工作状态信息信息
    year,month->year,list[month,dict[dayname,day_count]]
    """
    if yearmonth is None:
        text = filter_input("year&month(YYYYMM):")
    else:
        text = yearmonth
    # 20yr->20+yr 20Q1->20+q1,2011->20+11
    yearmonth = re.search(r"(\d{4})(\d{2}|[qQ][1-4]|[yY][rR])", text)
    assert yearmonth, "输入格式不正确！"

    year = yearmonth.groups()[0]

    # 注意，月份从 1 开始！
    months = get_months(yearmonth.groups()[1])

    month_and_dayses: list[MonthAndDays] = []

    # TODO 调整泛用性
    if len(months) == 1:
        m = months[0]
        result_map={}
        for i in budget_fields:
            if i == 'default':
                continue
            text = filter_input(f'{m}月{i}天数')
            result_map[i]=int(text)

        result_map['default'] = get_months(m)-sum(result_map.values())
        month_and_dayses.append((m, result_map))
    else:
        for m in months:
            ast: list[dict] = smart_import(f"{year}月报/{year[-2:]}{m:02}.md", "md")
            try:
                for _ in ast:
                    if _['type'] == 'paragraph':
                        text = _['children'][0]['raw']
                        break
                else:
                    raise EOFError('输入的文件不正确')
            except KeyError as e:
                pass
            search = re.search(r'本月共 ?(\d+) ?天，其中在校 (\d+) 天，在家 (\d+) 天。', text)
            assert search
            total, zaixiao, zaijia = map(int, search.groups())
            month_and_dayses.append((m, {'default': total - zaixiao - zaijia, '在校': zaixiao, '在家': zaijia}))

    return int(year), month_and_dayses


def get_working_days(year, month, cal=China()):
    """基于 worklender 计算月内的工作日数量"""
    # 获取该月的第一天和最后一天的星期几和天数
    _, days_in_month = calendar.monthrange(year, month)

    # 获取该月的第一天和最后一天
    start_date = datetime.date(year, month, 1)
    end_date = datetime.date(year, month, days_in_month)

    # 计算两个日期之间的工作日数量
    # from workalendar.asia import China
    working_days = cal.get_working_days_delta(start_date, end_date)

    # 返回工作日数量
    return working_days


def get_next(last_month_out_homes: list[MonthAndDays]) -> list[tuple]:
    """预测下一个时间段（月，季，年）在家在校天数"""
    # TODO 调整泛用性

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
