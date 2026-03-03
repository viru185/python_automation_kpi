# config related to logging
"""
Log levels:
    DEBUG: Detailed information, typically of interest only when diagnosing problems.
    INFO: Confirmation that things are working as expected.
    WARNING: An indication that something unexpected happened, or indicative of some problem in the near future (e.g. ‘disk space low’). The software is still functioning as expected.
    ERROR: Due to a more serious problem, the software has not been able to perform some function.
    CRITICAL: A serious error, indicating that the program itself may be unable to continue running.
"""

# Logging config

LOGS_FILE = "logs/app.log"
LOGS_DIR = "logs"
LOG_LEVEL = "INFO"
LOG_TO_FILE = True
LOG_TO_CONSOLE = True


# CONFIGURATION FOR LLM
LLM_MODEL = "mistralai/ministral-3-8b-reasoning"

# available model
# 1. "mistralai/ministral-3-8b"
# 2. "mistralai/ministral-3-8b-reasoning"
# 3. "deepseek/deepseek-r1-distill-llama-8b"
# 4. "mistralai/mistral-7b-instruct-v0.3"
# 5. "deepseek/deepseek-r1-0528-qwen3-8b"
# 6. "google/gemma-3-4b"


# excel file path
EXCEL_PATH = "data/Merian_Gold_Mines_KPIs.xlsx"

# cache file path (will store processed key parameters results)
CACHE_PATH = "data/cache.json"
