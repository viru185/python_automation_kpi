import lmstudio as lms

from config import LLM_MODEL

model = lms.llm(f"{LLM_MODEL}")
response_format = {"type": "object", "additionalProperties": {"type": "string"}}


def call_llm(massage:str):
    return model.respond(massage, response_format=response_format)
