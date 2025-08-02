from fastapi import FastAPI, Body
from pydantic import BaseModel
from google import genai
from google.genai import types
import json

app = FastAPI()
genai = genai.Client()

class ApiRequest(BaseModel):
    ideal: str
    afraid: str
    current: str

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/api")
async def gemini_api(request: ApiRequest):
    response = genai.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt.format(
            ideal=request.ideal,
            afraid=request.afraid,
            current=request.current
        ) + prompt_json,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0) # Disables thinking
        ),
    )
    print(response.text)
    return json.loads(response.text)


prompt = """
너는 한국어로 대답하는 GPT 모델이며, 사용자의 입력을 바탕으로 세 가지 출력을 JSON 형식으로 생성해야 합니다.

입력은 다음 세 가지 요소로 구성됩니다:
1. 사용자가 이루고자 하는 미래(목표 또는 꿈)
2. 그것을 가로막고 있는 두려움(불안, 트라우마, 습관 등)
3. 현재 사용자가 처한 상황

아래는 사용자의 입력입니다:
- 사용자의 이상: {ideal}
- 사용자의 두려움: {afraid}
- 사용자의 현재 상황: {current}

너는 아래 세 가지 항목을 출력해야 합니다:

- "succ": 두려움을 극복하고 미래를 성취한 모습의 시뮬레이션. 
        -   여기에 그 미래를 위한 매일 단위의 TO DO 루틴도 포함되어야 합니다. 
            주나 월, 년도 단위의 계획을 세우지 마세요. 
            앞에 시간에 대한 어구를 붙이지 마세요. 
            해야 할 작업만 작성해주세요. 
- "fail": 두려움에 지배당한 경우의 미래 시뮬레이션.
- "reason": 두려움의 원인을 분석하고 논리적으로 설명한 부분.
"""

prompt_json = """
응답 형식은 다음과 같은 JSON 형태로 작성되어야 합니다:

{
  "succ": {
    "description": "<두려움을 극복하고 목표를 이룬 미래에 대한 묘사>",
    "routine": [
      "<매일 실천할 TO DO 항목 1>",
      "<매일 실천할 TO DO 항목 2>",
      "... 등"
    ]
  },
  "fail": "<두려움에 지배되어 실패한 미래에 대한 묘사>",
  "reason": "<두려움의 원인 분석과 그에 대한 논리적인 설명>"
}

모든 응답은 한국어로 작성되어야 하며, 출력은 순수 JSON으로만 이루어져야 합니다. 설명이나 주석은 포함하지 마세요.
MARKDOWN 포매팅을 하지 마십시오. RAW TEXT로 출력하십시오.
"""