from typing import List
from pydantic import BaseModel

class WordBankQuestionData(BaseModel):
    instruction: str
    text_template: str
    tokens: List[str]

class WordBankAnswerData(BaseModel):
    correct_tokens: List[str]
