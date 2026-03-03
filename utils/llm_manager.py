import json
from typing import Any

import lmstudio as lms

from config import LLM_MODEL
from utils.logger import logger

# instantiate model once; configuration is kept in config.py
model = lms.llm(f"{LLM_MODEL}")
response_format = {"type": "object", "additionalProperties": {"type": "string"}}


def call_llm(message: str) -> Any:
    """Send a prompt to the underlying LLM and return a JSON-serializable
    response.

    Because some backends return a :class:`PredictionResult` or another
    custom object, we always convert the result to a string first and then
    attempt to parse JSON from that string.  The cache layer expects the
    final return value to be JSON-compatible (dict, list, etc.), so if the
    response cannot be decoded we return the raw string and log a warning.
    """
    try:
        raw = model.respond(message, response_format=response_format)
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise

    # convert everything to string for parsing; this handles PredictionResult
    raw_str = str(raw)

    # if the model already returned a dict, keep it
    if isinstance(raw, dict):
        return raw

    # now try to decode JSON from the string
    try:
        parsed = json.loads(raw_str)
        return parsed
    except json.JSONDecodeError:
        logger.warning("LLM response could not be parsed as JSON, returning raw string")
        return raw_str
