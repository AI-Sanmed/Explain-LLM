import os
from tqdm import tqdm
import numpy as np
import pandas as pd
import pickle
import os
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.preprocessing import LabelEncoder

from CAC_CTAI_decision_tree import MedicalDecisionTree

from langchain_ollama.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


#CAC: <3; 3-8; >9
#CTAI: <0.6; 0.6-0.85; >0.85
#Nodule size: <6mm; 6-8mm; >8mm
#Follow-up: first, smaller, larger, stable
def predict_result(model, cac:int, ctai:float,nodule_size:float, followup_compare:int):
    data = {
        'CAC': [cac],
        'CTAI': [ctai],
        'Nodule_Size': [nodule_size],
        'FollowUp': [followup_compare]
    }
    df = pd.DataFrame(data)
    #predict
    pred = model.predict(df)
    return pred

def explain_llm():
    # CAC = info['CAC']
    # CTAI = info['CTAI']
    # Nodule_Size = info['Nodule_Size']
    # FollowUp = info['FollowUp']
    #
    # Risk = info['Risk']
    # Followup_advice = info['FollowUp_advice']

    system_prompt = """
        你是一个替医生写报告的AI，请根据患者的检查，和医生提供的风险等级和随访建议，写一份简单的报告。报告格式如下：
        循环异常细胞（CAC）有 个，属于 风险等级，
        智能影像分析之（CTAI）为 ，属于 风险等级，
        肺结节大小为 mm
        综合以上信息：
        该患者的综合风险评估为 风险，
        建议患者 进行随访。 
    """


    output_parser = StrOutputParser()
    llm = ChatOllama(model='qwen2.5:14b', temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "CAC:{CAC}, CTAI:{CTAI}, 结节大小:{结节大小}, 随访记录:{随访记录}, 综合风险评估:{综合风险评估}, 随访建议:{随访建议}"),
    ])
    chain = prompt | llm | output_parser

    print(chain.invoke({"CAC": "8", "CTAI": "85%", "结节大小": "6.74", "随访记录": "相比上次增大", "综合风险评估": "高", "随访建议": "3个月"}))

    pass


if __name__ == '__main__':
    model = MedicalDecisionTree.load_model('/data/zhenyu/Program/Explain_LLM/data/explain_pred_model.pkl')
    result = predict_result(model, 20, 90, 4, 0)
    risk = result['Risk'].values[0]
    followup_advice = result['FollowUp_advice'].values[0]
    print(result)
    # explain_llm()
    pass