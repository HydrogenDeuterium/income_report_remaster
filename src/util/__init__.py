import contextlib
import os
import tomllib
from collections import defaultdict
from decimal import Decimal
from typing import Any, Type

import jinja2
import mistune

from category import Category

file_dir = r"C:\Users\Deu\OneDrive\Projects\Python\income_report_data"


def get_last(last_year: int, last_month) -> defaultdict[Any, Type[Decimal]] | dict[Any, Decimal]:
    """依赖上月月报格式获取各子项上月结余"""
    filename = f'{last_year}月报/{last_year % 100}{last_month :0>2}.md'
    try:
        data_ = smart_import(filename, 'md')
    except FileNotFoundError:
        return defaultdict(Decimal)

    s: list = data_[-1]['children']
    subs = []
    for i in s[:-1]:
        subs += i['children'][1]['children']

    a = [sub['children'][0]['children'][0]['raw'] for sub in subs]
    ret = defaultdict(Decimal)
    for ss in a:
        k, v = ss.split(':')
        ret[k] = Decimal(v)
    return ret


def smart_import(filename, ext=None) -> str | dict | list[dict]:
    """
    ext to return data structure map:
        toml -> structure data
        md/markdown -> markdown ast
        None/other -> plain text
    """
    if ext is None and len(filename.split('.')) == 2:
        ext = filename.split('.')[-1]

    @contextlib.contextmanager
    def smart_open(filename_, *args, **kwargs):
        prefixes = file_dir, "../", "", 'test/'
        for prefix in prefixes:
            try:
                file_path = os.path.join(prefix, filename_)
                f_ = open(file_path, *args, **kwargs)
                break
            except FileNotFoundError:
                pass
        else:
            raise FileNotFoundError(filename_)
        yield f_
        f_.close()

    match ext:
        case 'toml':
            with smart_open(filename, 'rb') as f:
                return tomllib.load(f)
        case 'md' | "markdown":
            parser = mistune.create_markdown(renderer='ast')
            with smart_open(filename, encoding='utf-8') as f:
                return parser(f.read())
        case _:
            with open(filename, encoding="utf-8") as f:
                data_ = f.read()
            return data_


def get_structure(last_year: int, last_month: int, toml='./budget.toml', *, test=False) -> list[Category]:
    """生成结构，写入上月结余和预算规则"""
    try:
        items_budgets: dict[str, dict[str, dict]] = smart_import(toml, ext='toml')['预算']
    except FileNotFoundError:
        items_budgets: dict[str, dict[str, dict]] = smart_import('budget/budget.toml', ext='toml')['预算']

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


budget_data = smart_import('./budget.toml', ext='toml')
budget_version = budget_data.pop('__version')
budget_fields = budget_data.pop('__fields')
