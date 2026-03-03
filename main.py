import json

from utils import logger
from utils.llm_manager import call_llm
from utils.llm_prompt import build_kpi_prompt

input_json = {
    "Temperature": "22 °C",
    "Pressure": "1.2 bar",
    "AirFlow": "500 CFM",
    "Humidity": "50 %",
    "Power": "3 kW",
    "Current": "10 A",
    "Voltage": "230 V",
    "Frequency": "50 Hz",
}

print(call_llm(build_kpi_prompt(input_json)))
