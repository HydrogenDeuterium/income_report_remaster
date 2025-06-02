import csv
import decimal
from collections import defaultdict
import os
from decimal import Decimal
from pathlib import Path, PosixPath

fixed_categories = ['吃喝',
                    '饮料',
                    '水果牛奶',
                    '零食冷饮',
                    ['房租押金', '房租'],
                    '服装外形',
                    '耐用品',
                    '交通物流',
                    '医疗',
                    '日用消耗',
                    '赠礼',
                    '软件服务',
                    '文具资料',
                    '小说',
                    '电子游戏',
                    ['其它娱乐', '其他'],
                    ['主机', '主体 '],
                    '配件',
                    ['水费', '洗衣'],
                    '电力',
                    ['通讯', '网络通讯'], ]


def analyze_csv(file_path, output_path):
    # 创建一个默认值为0的字典来存储分类汇总
    
    # 打开并读取CSV文件
    with open(file_path, 'r', encoding='utf-8-sig') as csvfile:  # 使用utf-8-sig编码去除BOM字符
        reader = csv.DictReader(csvfile)
        
        categories = get_category_value(reader)
    
    # 获取输入文件的基本名称（不带扩展名）
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    
    # 创建输出文件路径
    latest_date = get_yearmonth(file_path)
    if latest_date.endswith('YR'):
        output_path = os.path.join(output_path, 'input_year.txt')
    elif (latest_date.endswith('Q1') or latest_date.endswith('Q2')
          or latest_date.endswith('Q3') or latest_date.endswith('Q4')):
        output_path = os.path.join(output_path, 'input_quarter.txt')
    else:
        output_path = os.path.join(output_path, 'input_month.txt')
    
    # 写入输出文件
    with open(output_path, 'w', encoding='utf-8') as outfile:
        # 写入年月信息
        outfile.write('#year&month(YYYYMM):\n')
        outfile.write(f'{latest_date}\n\n')
        
        # 写入分类数据
        for category in fixed_categories:
            # 只写入支出（负值）和收入（正值）
            if isinstance(category, list):
                amount = categories[category[1]]
                category = category[0]
            elif isinstance(category, str):
                amount = categories[category]
            
            outfile.write(
                (
                    f'#{category}:\n{amount}\n'
                ))
    
    return output_path


def get_yearmonth(file_path):
    # 这里假设所有交易都在同一个月份
    # 找出最新的交易日期来确定年月
    with open(file_path, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        dates = {row['时间'].replace('-', '')[:6] for row in reader}
        if len(dates) == 1:
            return list(dates)[0]
        elif len(dates) == 3:
            latest_date = max(dates)
            return latest_date[:4] + f'Q{int(latest_date[4:]) // 3}'
        elif len(dates) == 12:
            latest_date = max(dates)[:4] + 'YR'
            return latest_date
        else:
            raise ValueError()


def get_category_value(reader):
    categories = defaultdict(decimal.Decimal)
    # 遍历每一行记录
    for row in reader:
        category = row['二级分类'] or row['分类']
        amount = Decimal(row['金额'])
        transaction_type = row['类型']
        
        # 只处理支出和收入
        if transaction_type not in ['支出', '退款']:
            continue
        
        if transaction_type == '退款':
            amount = -amount
        
        # 汇总分类数据
        categories[category] += amount
    return categories


if __name__ == '__main__':
    # 使用示例文件路径
    input_root = Path(r'C:\Users\Deu\OneDrive\Projects\Python\income_report_data')
    reletive_path = Path(r'2025月报/QianJi_日常生活_2025-06-02_204621.csv')
    file_path = input_root / reletive_path
    output_file = analyze_csv(file_path, input_root)
    print(f'分析完成，结果已保存至：{output_file}')
