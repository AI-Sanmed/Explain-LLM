import os
import torch
from threading import Thread
from transformers import AutoTokenizer, StoppingCriteria, StoppingCriteriaList, TextIteratorStreamer, AutoModel
import logging
import sys
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import ServerSentEvent, EventSourceResponse
import uvicorn
import json
from openai import OpenAI
# class LLM_Explain():
#     def __init__(self, gpu_id) -> None:
#         logger.info("Start initialize model...")
#         self.tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True, encode_special_tokens=True)
#         self.model = AutoModel.from_pretrained(MODEL_PATH, trust_remote_code=True, device_map='auto').eval()
#         self.gpu_id = gpu_id
#         logger.info("Model initialized successfully.")
#
#     class StopOnTokens(StoppingCriteria):
#         def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
#             stop_ids = self.model.config.eos_token_id
#             for stop_id in stop_ids:
#                 if input_ids[0][-1] == stop_id:
#                     return True
#             return False
#
#     def predict_stream(self,messages):
#         stop = self.StopOnTokens()
#         model_inputs = self.tokenizer.apply_chat_template(messages,
#                                                      add_generation_prompt=True,
#                                                      tokenize=True,
#                                                      return_tensors="pt").to(next(self.model.parameters()).device)
#         streamer = TextIteratorStreamer(self.tokenizer, timeout=60, skip_prompt=True, skip_special_tokens=True)
#         generate_kwargs = {
#             "input_ids": model_inputs,
#             "streamer": streamer,
#             "max_new_tokens": 512,
#             "do_sample": False,
#             "top_p": 1,
#             "temperature": 0,
#             "stopping_criteria": StoppingCriteriaList([stop]),
#             "repetition_penalty": 1,
#             "eos_token_id": self.model.config.eos_token_id,
#         }
#         t = Thread(target=self.model.generate, kwargs=generate_kwargs)
#         t.start()
#         result = ''
#         for new_token in streamer:
#             yield {"response": new_token, "finished": False}
#             result += new_token
#         logging.info('Answer - {}'.format(result))
#         yield {"response": result, "finished": True}

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

logger = getLogger('Chat_API', 'Chat_API.log')

def suggest_generate(CAC_num:int, CTAI_score:float):
    suggest_info = None
    if CAC_num > 9 and CTAI_score >= 0.85:
        suggest_info = """CAC > 9, CTAI 结节风险 > 85%：分析解读参考 “CAC、CTAI均在高风险区间，应选择积极治疗，特别是结节大小≥8mm，手术干预指征更强。如果结节＜8mm，或患者拒绝手术治疗时，可选择密切观察（每3个月复查胸部CT），随访过程中如有结节增大、密度增高、实性成分增加等，需再次建议患者积极治疗（手术切除）。当然，尽管CAC大于9，CTAI＞85%，提示肺结节恶性风险高危，但手术切除后病理依然存在良性结节的可能，虽然这种可能性比较小。” """
    elif CAC_num > 9 and CTAI_score < 0.85:
        suggest_info = """CAC > 9, CTAI 结节风险 < 85%：分析解读参考 ”CAC高风险区间，CTAI未达高风险区间，建议抗炎治疗（两周）后3个月复查胸部CT，同时进行CTAI随访对比。如有结节增大、密度增高、实性成分增加等，可建议积极治疗，如果没有结节增大、密度增高、实性成分增加等，应对患者进行密切随访，每3个月复查胸部CT，连续3-4次，随访观察过程中出现结节恶性倾向增大（结节增大、密度增高、实性成分增加或出现下列征象一项以上时：结节分叶、毛刺、胸膜牵拉、血管集束、空泡征等，建议积极治疗。“"""
    elif 3 <= CAC_num <= 9 and CTAI_score >= 0.85:
        suggest_info = """3 ≤ CAC ≤ 9, CTAI 结节风险 > 85%：分析解读参考 “CAC中高风险区间，CTAI高风险区间，应选择积极治疗。特别是结节大小≥8mm，手术干预指征更强，如果结节＜8mm，或患者拒绝手术治疗时，可选择密切观察（每3个月复查胸部CT），随访过程中如有结节增大、密度增高、实性成分增加等，需再次建议患者积极治疗（手术切除）。” """
    elif 3 <= CAC_num <= 9 and CTAI_score < 0.85:
        suggest_info = """3 ≤ CAC ≤ 9, CTAI 结节风险 < 85%：分析解读参考 “CAC中高风险区间，CTAI未达高风险区间，应对患者进行定期随访，3-6个月复查胸部CT，同时CTAI进行随访对比分析。”"""
    elif CAC_num < 3 and CTAI_score >= 0.85:
        suggest_info = """CAC < 3, CTAI 结节风险 > 85%：分析解读参考 “CAC低风险区间，CTAI高风险区间，建议密切随访观察。每3个月复查胸部CT，同时进行CTAI随访对比，如有结节增大、密度增高、实性成分增加等，可建议积极治疗；如果没有结节增大、密度增高、实性成分增加等，应继续对患者进行密切随访，每3个月复查胸部CT，连续3-4次，随访观察过程中出现结节恶性倾向增大（结节增大、密度增高、实性成分增加或出现下列征象一项以上时：结节分叶、毛刺、胸膜牵拉、血管集束、空泡征等，建议积极治疗。” """
    elif CAC_num < 3 and CTAI_score < 0.85:
        suggest_info = """CAC < 3, CTAI 结节风险 < 85%：分析解读参考 “良性结节的可能性较大，建议年度体检，12个月复查胸部CT。如果结节大于15mm，或患者焦虑明显、要求治疗意愿明显，可考虑手术干预，但术后病理良性结节概率较高。”"""
    return suggest_info


def ctai_generate(CTAI_score: float):
    ctai_info = None
    if CTAI_score >= 0.85:
        ctai_info = """结节风险预测 > 85%: 高风险结节；"""
    elif 0.65 <= CTAI_score < 0.85:
        ctai_info = """65% < 结节风险预测 < 85%: 中高风险结节；"""
    elif 0.4 <= CTAI_score < 0.65:
        ctai_info = """40% < 结节风险预测 < 65%: 中风险结节；"""
    elif CTAI_score < 0.4:
        ctai_info = """结节风险预测 < 40%: 低风险结节；"""
    return ctai_info

def prompt_generate(patient_info):
    prompt = """你是一个圣美生物有限公司一名经验丰富的呼吸科医生。患者已经做过了CAC（循环染色体异常细胞检测）与CTAI（肺部CT扫描与肺结节风险评估）检测。
请先根据患者提供的CAC检测报告与CTAI检测报告，综合两份检测报告和以下参考信息，对每个结节进行分析解读。
最后给出整体建议。【注意，不要使用肯定词汇，例如：立即，必须，应该等词汇。应考虑结节大小给出随访或积极治疗建议。】
```参考信息：
"""
    CAC_nums = int(patient_info['CAC'])
    if CAC_nums > 9:
        CAC_info = "CAC > 9：高风险区间；"
    elif CAC_nums < 3:
        CAC_info = "CAC < 3: 低风险区间；"
    else:
        CAC_info = "3 ≤ CAC ≤ 9: 中高风险区间；"

    CTAI_nums = len(patient_info['CTAI'])
    CTAI_info_list = set()
    suggest_info_list = set()
    for i in range(CTAI_nums):
        nodule_info = patient_info['CTAI'][f"item{i+1}"]
        nodule_score = nodule_info['NoduleScore']
        ctai_info = ctai_generate(nodule_score)
        CTAI_info_list.add(ctai_info)
        suggest_info = suggest_generate(CAC_nums, nodule_score)
        suggest_info_list.add(suggest_info)
    CAC_info_last = f"""患者姓名：{patient_info['Name']}
CAC：
    {CAC_info}
    """
    CTAI_info_last = """
结节风险预测:
    """
    for i in CTAI_info_list:
        CTAI_info_last += f"{i}\n   "

    suggest_info_last = """
建议：
    """
    for i in suggest_info_list:
        suggest_info_last += f"{i}\n    "
    prompt += CAC_info_last + CTAI_info_last + suggest_info_last + "\n```"
    return prompt

def user_content_generate(patient_info):
    user_name = patient_info['Name']
    CAC_nums = int(patient_info['CAC'])
    CTAI_nums = len(patient_info['CTAI'])
    ctai_info_list = []
    for i in range(CTAI_nums):
        nodule_info = patient_info['CTAI'][f"item{i+1}"]
        nodule_score = nodule_info['NoduleScore']
        nodule_type = nodule_info['NoduleType']
        nodule_size = nodule_info['NoduleSize']
        nodule_density = nodule_info['NoduleDensity']
        nodule_location = nodule_info['NoduleLocation']
        nodule_info = f"""{i+1}号结节 结节风险预测：{nodule_score*100}%; 结节类型：{nodule_type}; 结节大小：{nodule_size}mm; 结节密度：{nodule_density}HU; 结节位置：{nodule_location}"""
        ctai_info_list.append(nodule_info)
    nodule_info_last = "\n".join(ctai_info_list)
    user_content = f"""患者姓名：{user_name}
CAC：{CAC_nums}    
结节信息：
{nodule_info_last}
    """
    return user_content
    pass

base_url = "http://127.0.0.1:8000/v1/"
client = OpenAI(api_key="EMPTY", base_url=base_url)
def explain_predict(messages):
    response = client.chat.completions.create(
        model="glm-4",
        messages=messages,
        stream=True,
        max_tokens=512,
        temperature=0,
        presence_penalty=1.2,
        top_p=1,
    )
    if response:
        for chunk in response:
            content = chunk.choices[0].delta.content
            finish_reason = chunk.choices[0].finish_reason
            yield {"response": content, "finished": finish_reason == 'stop'}
    else:
        yield 'Error'

def start_server(http_address:str, port:int):
    app = FastAPI()
    app.add_middleware(CORSMiddleware,
                       allow_origins=["*"],
                       allow_credentials=True,
                       allow_methods=["*"],
                       allow_headers=["*"]
                       )

    @app.post("/explain_chat")
    async def explain_chat(patient_info:dict, response: Response):
        response.headers['Content-Type'] = 'text/event-stream'
        response.headers['Cache-Control'] = 'no-cache'
        ID = patient_info['ID']
        async def decorate(messages):
            if messages is None:
                yield json.dumps({"ID": ID, "response": "", "finished":True, "success": False}, ensure_ascii=False)
            result = ''
            for i, item in enumerate(explain_predict(messages)):
                result += item['response']
                if item['finished']:
                    logger.info('ID--', ID, 'LLM_Response--', result)
                yield json.dumps({
                    "ID":ID,
                    "response": item['response'],
                    "finished": item['finished'],
                    "success": True,
                }, ensure_ascii=False)


        try:
            prompt = prompt_generate(patient_info)
            user_content = user_content_generate(patient_info)
            logger.info('ID--', ID,'user_content--', user_content)
            messages = [
                {
                    "role":"system",
                    "content":prompt
                },
                {
                    "role":"user",
                    "content":user_content
                }
            ]
            print(messages)
            return EventSourceResponse(decorate(messages))
        except:
            return EventSourceResponse(decorate(None))

    uvicorn.run(app=app, host=http_address, port=port, workers=1)


if __name__ == '__main__':
    # json_path = "demo.json"
    # import json
    # with open(json_path, 'r', encoding='utf-8') as f:
    #     patient_info = json.load(f)
    # # print(prompt_generate(patient_info))
    # print(user_content_generate(patient_info))
    # pass
    #只允许使用这个端口做这个事儿。

    start_server(http_address='172.16.43.57', port=8005)