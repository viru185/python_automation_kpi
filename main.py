import logging
from datetime import datetime
from time import sleep

import pyperclip

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def log_status(msg, level="info"):
    if level == "debug":
        logging.debug(msg)
    elif level == "warning":
        logging.warning(msg)
    elif level == "error":
        logging.error(msg)
    else:
        logging.info(msg)


last = ""

log_status("Clipboard monitor started")
try:
    while True:
        sleep(0.5)
        copy_text = pyperclip.paste()

        if copy_text != last:
            data = copy_text.strip()
            if not data:
                last = copy_text
                log_status("Empty clipboard content — ignored", "debug")
                continue

            if data == "exit":
                log_status("Received exit command — stopping monitor")
                break

            log_status(f"New clipboard content detected: {data[:80]!r}")

            prompt = f"""
You are given equipment data in this possible format (not fixed):
"type of device ; company ; model"

Task:
- Identify VERY COMMON parameters that can be monitored live for the device.
- Do NOT include model-specific or rare parameters.
- If the input is NOT an equipment/device, reply with a single-line message only.

Output Rules:
- If valid equipment → return ONLY a JSON object.
- Keep keys simple and standard (e.g., Power, Voltage, Temperature, Speed).
- Values should be realistic example values with units.
- Do NOT include explanations or extra text.
- Do NOT include source websites in the JSON.

Example output:
```json
{{"Power":"5 kW","Voltage":"220 V","Speed":"300 rpm"}}

Input:
{data}
"""

            pyperclip.copy(prompt)
            last = prompt
            log_status("Prompt copied to clipboard; monitor will ignore this replacement until changed")
        else:
            log_status("No change in clipboard", "debug")
            continue
except KeyboardInterrupt:
    log_status("Monitor stopped by user (KeyboardInterrupt)")
