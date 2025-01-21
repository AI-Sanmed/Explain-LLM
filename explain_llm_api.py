import pandas as pd
from CAC_CTAI_decision_tree import MedicalDecisionTree
from openai import OpenAI
import uvicorn
import logging
import sys
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

followup_compare_map = {
    '首次': 0,
    '增大': 1,
    '变小': 2,
    '无明显变化': 3
}

risk_label_map = {
    0: '低风险',
    1: '中低风险',
    2: '中风险',
    3: '中高风险',
    4: '高风险'
}

followup_advice_map = {
    0: '3个月',
    1: '6个月',
    2: '12个月'
}


def getLogger(name, file_name, use_formatter=True):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s  %(message)s')
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    if file_name:
        handler = logging.FileHandler(file_name, encoding='utf8')
        handler.setLevel(logging.INFO)
        if use_formatter:
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
            handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


logger = getLogger('Explain_LLM_API', 'Explain_LLM_API.log')


def prompt_generate(CAC_num: int, CTAI_score: float):
    base_prompt = """
    你是一个经验丰富的呼吸科医生。患者已经做过了CAC（循环染色体异常细胞检测）与CTAI（肺部CT扫描与肺结节风险评估）检测。
    请根据患者的检查结果，给出综合风险评估与随访时间建议报告。
    报告格式为：
    "本次检出循环异常细胞xx个，提示xx风险。CTAI评估结节风险为xx，提示xx风险。结节大小为xx，该结节为首次发现/较上次对比xx变化。
    综合以上信息，该患者综合风险为xx风险，建议密切观察，xx月复查胸部CT对比随访/建议积极治疗（如手术切除）/建议抗炎治疗（两周）后复查胸部CT随访对比。
    以下为参考信息：
"""
    suggest_info = None
    if CAC_num > 9 and CTAI_score >= 85:
        suggest_info = """CAC > 9, CTAI 结节风险 > 85%：分析解读参考 “CAC、CTAI均在高风险区间，应选择积极治疗，特别是结节大小≥8mm，手术干预指征更强。如果结节＜8mm，或患者拒绝手术治疗时，可选择密切观察（每3个月复查胸部CT），随访过程中如有结节增大、密度增高、实性成分增加等，需再次建议患者积极治疗（手术切除）。当然，尽管CAC大于9，CTAI＞85%，提示肺结节恶性风险高危，但手术切除后病理依然存在良性结节的可能，虽然这种可能性比较小。” """
    elif CAC_num > 9 and CTAI_score < 85:
        suggest_info = """CAC > 9, CTAI 结节风险 < 85%：分析解读参考 ”CAC高风险区间，CTAI未达高风险区间，建议抗炎治疗（两周）后3个月复查胸部CT，同时进行CTAI随访对比。如有结节增大、密度增高、实性成分增加等，可建议积极治疗，如果没有结节增大、密度增高、实性成分增加等，应对患者进行密切随访，每3个月复查胸部CT，连续3-4次，随访观察过程中出现结节恶性倾向增大（结节增大、密度增高、实性成分增加或出现下列征象一项以上时：结节分叶、毛刺、胸膜牵拉、血管集束、空泡征等，建议积极治疗。“"""
    elif 3 <= CAC_num <= 9 and CTAI_score >= 85:
        suggest_info = """3 ≤ CAC ≤ 9, CTAI 结节风险 > 85%：分析解读参考 “CAC中高风险区间，CTAI高风险区间，应选择积极治疗。特别是结节大小≥8mm，手术干预指征更强，如果结节＜8mm，或患者拒绝手术治疗时，可选择密切观察（每3个月复查胸部CT），随访过程中如有结节增大、密度增高、实性成分增加等，需再次建议患者积极治疗（手术切除）。” """
    elif 3 <= CAC_num <= 9 and CTAI_score < 85:
        suggest_info = """3 ≤ CAC ≤ 9, CTAI 结节风险 < 85%：分析解读参考 “CAC中高风险区间，CTAI未达高风险区间，应对患者进行定期随访，3-6个月复查胸部CT，同时CTAI进行随访对比分析。”"""
    elif CAC_num < 3 and CTAI_score >= 85:
        suggest_info = """CAC < 3, CTAI 结节风险 > 85%：分析解读参考 “CAC低风险区间，CTAI高风险区间，建议密切随访观察。每3个月复查胸部CT，同时进行CTAI随访对比，如有结节增大、密度增高、实性成分增加等，可建议积极治疗；如果没有结节增大、密度增高、实性成分增加等，应继续对患者进行密切随访，每3个月复查胸部CT，连续3-4次，随访观察过程中出现结节恶性倾向增大（结节增大、密度增高、实性成分增加或出现下列征象一项以上时：结节分叶、毛刺、胸膜牵拉、血管集束、空泡征等，建议积极治疗。” """
    elif CAC_num < 3 and CTAI_score < 85:
        suggest_info = """CAC < 3, CTAI 结节风险 < 85%：分析解读参考 “良性结节的可能性较大，建议年度体检，12个月复查胸部CT。如果结节大于15mm，或患者焦虑明显、要求治疗意愿明显，可考虑手术干预，但术后病理良性结节概率较高。”"""

    prompt = base_prompt + suggest_info
    return prompt


def user_context_generate(patient_info: dict):
    CAC_nums = int(patient_info['CAC'])
    CTAI = patient_info['CTAI']
    nodule_size = patient_info['NoduleSize']
    followup_compare = patient_info['FollowUpCompare']
    followup_compare_id = followup_compare_map[followup_compare]

    data = {
        'CAC': [CAC_nums],
        'CTAI': [CTAI],
        'Nodule_Size': [nodule_size],
        'FollowUp': [followup_compare_id]
    }
    df = pd.DataFrame(data)
    model = MedicalDecisionTree().load_model('/data/zhenyu/Program/Explain_LLM/data/explain_pred_model.pkl')
    pred = model.predict(df)
    risk = risk_label_map[pred['Risk'].values[0]]
    followup_advice = followup_advice_map[pred['FollowUp_advice'].values[0]]

    if CAC_nums >= 9:
        CAC_lavel = '高风险'
    elif 3 <= CAC_nums < 9:
        CAC_lavel = '中风险'
    else:
        CAC_lavel = '低风险'

    if CTAI >= 85:
        CTAI_lavel = '高风险'
    elif 65 <= CTAI < 85:
        CTAI_lavel = '中风险'
    else:
        CTAI_lavel = '低风险'

    user_content = f"""
    CAC:{CAC_nums}个；
    CAC风险等级：{CAC_lavel}；
    CTAI：{CTAI}%；
    CTAI风险等级：{CTAI_lavel}；
    结节尺寸：{nodule_size}mm；
    随访变化：{followup_compare}；
    综合风险评估：{risk}；
    随访建议：{followup_advice}；
"""
    return user_content

def explain_predict(messages):
    base_url = "http://127.0.0.1:8000/v1/"
    client = OpenAI(api_key="EMPTY", base_url=base_url)
    try:
        response = client.chat.completions.create(
            model="glm-4",
            messages=messages,
            stream=False,  # 改为非流式响应
            max_tokens=512,
            temperature=0,
            presence_penalty=1.2,
            top_p=1,
        )

        if response and response.choices:
            return {
                "response": response.choices[0].message.content,
                "success": True
            }
        else:
            logger.error("No response received from LLM service")
            return {
                "response": "Error: No response from LLM",
                "success": False
            }
    except Exception as e:
        error_msg = f"Error in explain_predict: {str(e)}\nFull error: {repr(e)}"
        logger.error(error_msg)
        return {
            "response": f"Error: {str(e)}",
            "success": False
        }


def start_server(http_address: str, port: int):
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    @app.get("/")
    async def root():
        return {"message": "Hello World"}

    @app.get("/health")
    async def health_check():
        try:
            response = client.chat.completions.create(
                model="glm-4",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5,
                stream=False
            )
            return {"status": "healthy", "llm_service": "connected"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    @app.post("/explain_llm")
    async def explain_llm(patient_info: dict):
        ID = patient_info['ID']
        try:
            prompt = prompt_generate(patient_info['CAC'], patient_info['CTAI'])
            user_content = user_context_generate(patient_info)
            logger.info(f'ID: {ID} - user_content: {user_content}')

            messages = [
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": user_content
                }
            ]

            result = explain_predict(messages)
            print(result)
            logger.info(f'ID: {ID} - Answer: {result["response"]}')

            return {
                "ID": ID,
                "response": result["response"],
                "success": result["success"]
            }

        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            logger.error(f"ID: {ID} - {error_msg}")
            return {
                "ID": ID,
                "response": error_msg,
                "success": False
            }

    uvicorn.run(app, host=http_address, port=port)


if __name__ == '__main__':
    start_server(http_address='172.16.43.57', port=8005)