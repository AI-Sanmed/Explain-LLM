import itertools
import pandas as pd
import numpy as np

# 定义变量的分类及其对应的随机数生成范围
CAC_CATEGORIES = {
    '[0, 3)': (0, 3),  # 0到2.99
    '[3, 8]': (3, 8),  # 3到8
    '[9, 20]': (9, 20)  # 9到20
}

CTAI_CATEGORIES = {
    '[0%, 65%]': (0, 65),  # 0%到65%
    '[65%, 85%]': (65, 85),  # 65%到85%
    '[85%, 99%]': (85, 99)  # 85%到99%
}

NODULE_SIZE_CATEGORIES = {
    '[0, 5]': (0, 5),  # 0到5 mm
    '[5, 8]': (5, 8),  # 5到8 mm
    '[9, 30]': (9, 30)  # 9到30 mm
}

FOLLOW_UP_CATEGORIES = [
    '首次',  # 首次
    '增大',  # 增大
    '变小',  # 变小
    '无明显变化'  # 无明显变化
]


def random_value_in_range(range_tuple):
    """
    在给定范围内生成随机浮点数

    Args:
    - range_tuple (tuple): 包含最小值和最大值的元组

    Returns:
    - float: 范围内的随机数
    """
    min_val, max_val = range_tuple
    return np.random.uniform(min_val, max_val)


def generate_combinations(num_samples=108):
    """
    生成指定数量的变量排列组合

    Args:
    - num_samples (int): 生成的组合数量

    Returns:
    - pandas.DataFrame: 包含随机组合的数据框
    """
    # 设置随机数种子以便结果可复现
    np.random.seed(42)

    # 存储组合的列表
    combinations = []

    # 生成指定数量的随机组合
    for _ in range(num_samples):
        # 对每个分类随机选择一个类别和对应的随机数
        cac_category = np.random.choice(list(CAC_CATEGORIES.keys()))
        ctai_category = np.random.choice(list(CTAI_CATEGORIES.keys()))
        nodule_category = np.random.choice(list(NODULE_SIZE_CATEGORIES.keys()))
        follow_up_category = np.random.choice(FOLLOW_UP_CATEGORIES)

        # 生成该类别对应区间的随机数
        cac_value = random_value_in_range(CAC_CATEGORIES[cac_category])
        ctai_value = random_value_in_range(CTAI_CATEGORIES[ctai_category])
        nodule_value = random_value_in_range(NODULE_SIZE_CATEGORIES[nodule_category])

        # 创建一个组合
        combination = {
            'CAC值': round(cac_value, 0),
            'CTAI值': round(ctai_value, 0),
            '结节大小值': round(nodule_value, 2),
            '随访对比': follow_up_category
        }
        combinations.append(combination)

    # 创建DataFrame
    df = pd.DataFrame(combinations)

    # 添加索引列，从1开始
    df.insert(0, '编号', range(1, len(df) + 1))

    return df


# 生成并保存结果
result = generate_combinations()
print(f"总组合数：{len(result)}种")
print("\n前10种组合预览：")
print(result.head(10).to_string(index=False))

# 保存到CSV文件
result.to_csv('variable_random_combinations.csv', index=False, encoding='utf-8-sig')
print("\n完整结果已保存到 variable_random_combinations.csv")


# 计算统计信息
def print_stats():
    print("\n统计信息：")
    print(f"1. CAC分类数：{len(CAC_CATEGORIES)}")
    print(f"2. CTAI分类数：{len(CTAI_CATEGORIES)}")
    print(f"3. 结节大小分类数：{len(NODULE_SIZE_CATEGORIES)}")
    print(f"4. 随访对比分类数：{len(FOLLOW_UP_CATEGORIES)}")
    print("\n各分类随机数范围：")
    print("CAC范围：")
    for category, (min_val, max_val) in CAC_CATEGORIES.items():
        print(f"  {category}: {min_val} - {max_val}")
    print("CTAI范围（%）：")
    for category, (min_val, max_val) in CTAI_CATEGORIES.items():
        print(f"  {category}: {min_val} - {max_val}")
    print("结节大小范围（mm）：")
    for category, (min_val, max_val) in NODULE_SIZE_CATEGORIES.items():
        print(f"  {category}: {min_val} - {max_val}")


print_stats()