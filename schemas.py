from pydantic import BaseModel
from typing import List
from datetime import datetime


# 입력용 스키마 (기존과 동일)
class SuccData(BaseModel):
    description: str
    todo: List[str]
    todo_cata: List[str]


class FailData(BaseModel):
    description: str
    reason: List[str]
    percent: List[int]
    action_title: List[str]
    action_desc: List[str]


class VareCreate(BaseModel):
    category: str
    title: str
    succ: SuccData
    fail: FailData


# 출력용 스키마 (수정됨)
class TodoResponse(BaseModel):
    id: int
    todo_text: str
    todo_category: str
    order_seq: int
    is_completed: bool  # 새로 추가된 필드

    class Config:
        from_attributes = True


class ReasonResponse(BaseModel):
    id: int
    reason_text: str
    percent: int
    order_seq: int

    class Config:
        from_attributes = True


class ActionResponse(BaseModel):
    id: int
    action_title: str
    action_desc: str
    order_seq: int

    class Config:
        from_attributes = True


class VareResponse(BaseModel):
    id: int
    category: str
    title: str
    succ_description: str
    fail_description: str
    created_at: datetime
    updated_at: datetime
    todos: List[TodoResponse]
    reasons: List[ReasonResponse]
    actions: List[ActionResponse]

    class Config:
        from_attributes = True


# TODO 업데이트용 스키마 (새로 추가)
class TodoUpdate(BaseModel):
    is_completed: bool