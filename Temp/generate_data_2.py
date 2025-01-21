import pandas as pd
def check_data():
    tuma_result_path = '/data/zhenyu/DataSets/LLM_FollowUp/Qingdao/SecondData/tuma_json_results.csv'

    tuma_result = pd.read_csv(tuma_result_path, encoding='gbk')

    patient_ids = tuma_result['PatientID']
    patient_ids = patient_ids.drop_duplicates()
    patient_id_list = []
    patient_nodule_size_list = []
    patinet_nodule_score_list = []
    for patient_id in patient_ids:
        patient_data = tuma_result[tuma_result['PatientID'] == patient_id]
        max_score = patient_data['OrigDetMaligScore'].max()
        max_data = patient_data[patient_data['OrigDetMaligScore'] == max_score]
        nodule_size = max_data['majorDiameter2D'].values[0]
        patient_id_list.append(patient_id)
        patient_nodule_size_list.append(nodule_size)
        patinet_nodule_score_list.append(max_score)

    result = pd.DataFrame({'PatientID': patient_id_list, 'NoduleSize': patient_nodule_size_list, 'NoduleScore': patinet_nodule_score_list})
    result.to_csv('/data/zhenyu/DataSets/LLM_FollowUp/Qingdao/SecondData/tuma_maxScoreNodule_results.csv', index=False)

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


if __name__ == '__main__':
    check_data()