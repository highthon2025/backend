import os

from pydantic import BaseModel
from google import genai
from google.genai import types
import json
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models, schemas, database
from models import Vare, VareTodo, VareReason, VareAction
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
genai = genai.Client(api_key=os.getenv("GEMINI_KEY"))

class ApiRequest(BaseModel):
    ideal: str
    afraid: str
    current: str

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/api")
async def gemini_api(request: ApiRequest):
    """Gemini API를 호출하여 사용자의 두려움과 목표에 대한 JSON 응답을 생성"""
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

너는 아래 다섯 가지 항목을 출력해야 합니다:
- "category": 이 두려움이 어떤 종류인지 분류합니다.
- "title": 이 두려움에 대한 간단한 제목을 작성합니다.
- "succ": 두려움을 극복하고 미래를 성취한 모습의 시뮬레이션. 
        -   그 미래를 위한 매일 단위의 TO DO 루틴도 포함되어야 합니다. 
            주나 월, 년도 단위의 계획을 세우지 마세요. 
            앞에 시간에 대한 어구를 붙이지 마세요. 
            해야 할 작업만 작성해주세요. 
            TODO 리스트의 카테고리도 달아주세요. 카테고리는 최대한 크게 잡아주세요 (ex: 진로), 카테고리가 겹쳐도 상관없습니다.
            TODO는 6개 작성해주세요. 카테고리 또한 6개로 동일해야 합니다.
- "reason": 두려움의 원인을 분석하고 논리적으로 설명한 부분.
            두려움의 원인을 짧게 적어주세요.
            두려움은 4개 작성해주세요. 백분위 또한 4개로 동일해야 합니다.
            공포의 백분위도 매겨주세요. 단, 백분위는 제목에 작성하지 않습니다.
- "action": 두려움을 극복할 수 있는 행위들을 작성해야 합니다. 제목과 설명으로 나누어 설명합니다. '- 한 행동'라고 제목을 달아주세요. 그리고 설명해주세요. 6개 작성해주세요. 앞에 '-' 와 같은 접두사를 붙이지 않아도 됩니다.
"""

prompt_json = """
응답 형식은 다음과 같은 JSON 형태로 작성되어야 합니다:

{
  "category": "<두려움의 종류>",
  "title": "<두려움에 대한 제목>",
  "succ": {
    "description": "<두려움을 극복하고 미래를 성취한 모습의 시뮬레이션>",
    "todo": [
      "<매일 실천할 TO DO 항목 1>",
      "<매일 실천할 TO DO 항목 2>",
      "... 등"
    ],
    "todo_cata": [
        "<TODO 카테고리>",
        "<TODO 카테고리>",
        "<TODO 카테고리>"
    ],
  },
  "fail": {
    "description": "<두려움을 극복하지 못했을 때의 상황>",
    "reason": ["<두려움의 원인 1>", "<두려움의 원인 2>", "<두려움의 원인 3>", "<두려움의 원인 4>"],
    "percent": [10,20,30,40],
    "action_title": [
      "<두려움을 극복하기 위한 행동 1>",
      "<두려움을 극복하기 위한 행동 2>",
      "<두려움을 극복하기 위한 행동 3>"
    ],
    "action_desc": [
      "<두려움을 극복하기 위한 행동 설명 1>",
      "<두려움을 극복하기 위한 행동 설명 2>",
      "<두려움을 극복하기 위한 행동 설명 3>"
    ]
  },
}

모든 응답은 한국어로 작성되어야 하며, 출력은 순수 JSON으로만 이루어져야 합니다. 설명이나 주석은 포함하지 마세요.
MARKDOWN 포매팅을 하지 마십시오. RAW TEXT로 출력하십시오.
"""

models.Base.metadata.create_all(bind=database.engine)


@app.post("/db/", response_model=schemas.VareResponse)
async def create_vare(vare_data: schemas.VareCreate, db: Session = Depends(database.get_db)):
    """JSON 데이터를 받아서 vare 데이터 저장"""

    # 메인 vare 데이터 생성
    db_vare = Vare(
        category=vare_data.category,
        title=vare_data.title,
        succ_description=vare_data.succ.description,
        fail_description=vare_data.fail.description
    )

    db.add(db_vare)
    db.flush()  # ID 생성을 위해 flush

    for i, (todo, category) in enumerate(zip(vare_data.succ.todo, vare_data.succ.todo_cata)):
        todo_item = VareTodo(
            vare_id=db_vare.id,
            todo_text=todo,
            todo_category=category,
            order_seq=i + 1
        )
        db.add(todo_item)

    # Reason 데이터 저장
    for i, (reason, percent) in enumerate(zip(vare_data.fail.reason, vare_data.fail.percent)):
        reason_item = VareReason(
            vare_id=db_vare.id,
            reason_text=reason,
            percent=percent,
            order_seq=i + 1
        )
        db.add(reason_item)

    # Action 데이터 저장
    for i, (title, desc) in enumerate(zip(vare_data.fail.action_title, vare_data.fail.action_desc)):
        action_item = VareAction(
            vare_id=db_vare.id,
            action_title=title,
            action_desc=desc,
            order_seq=i + 1
        )
        db.add(action_item)

    db.commit()
    db.refresh(db_vare)

    return db_vare


@app.get("/db/latest", response_model=List[schemas.VareResponse])
async def get_latest_vare(db: Session = Depends(database.get_db)):
    """최근 3개의 vare 데이터 조회 (3개 이하면 이하인 대로 출력)"""

    latest_vares = db.query(Vare).order_by(Vare.created_at.desc()).limit(3).all()

    if not latest_vares:
        raise HTTPException(status_code=404, detail="데이터가 없습니다")

    return latest_vares


@app.get("/db/", response_model=List[schemas.VareResponse])
async def get_all_vare(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    """모든 vare 데이터 조회 (페이징)"""

    vares = db.query(Vare).order_by(Vare.created_at.desc()).offset(skip).limit(limit).all()
    return vares


@app.get("/db/{vare_id}", response_model=schemas.VareResponse)
async def get_vare_by_id(vare_id: int, db: Session = Depends(database.get_db)):
    """특정 ID의 vare 데이터 조회"""

    vare = db.query(Vare).filter(Vare.id == vare_id).first()

    if not vare:
        raise HTTPException(status_code=404, detail="해당 ID의 데이터가 없습니다")

    return vare

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)