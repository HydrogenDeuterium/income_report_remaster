from date import get_month_days
import util

year, months_and_days = get_month_days()
last_month = (months_and_days[0][0] - 2) % 12 + 1
last_year = year - int(last_month == 12)

categories = util.get_structure(last_year, last_month)
for i in categories:
    i.budget(months_and_days)