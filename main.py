import json
import sys
from typing import Any

from config import CACHE_PATH, EXCEL_PATH
from utils.cache_manager import Cache
from utils.excel_manager import ExcelManager
from utils.llm_manager import call_llm
from utils.llm_prompt import build_kpi_prompt
from utils.logger import logger

# convenience constant for empty KPI cell
EMPTY = [None, "", "null"]


def normalize_json(input_str: str) -> str:
    """Return a canonical JSON string (sorted keys) for use as cache key.

    If the string is not valid JSON an exception bubbles up to caller.
    """
    obj = json.loads(input_str)
    return json.dumps(obj, sort_keys=True)


def main() -> None:
    logger.info("starting KPI automation run")

    cache = Cache(CACHE_PATH)
    excel = ExcelManager(EXCEL_PATH)
    total_rows = 0

    for sheet in excel.iterate_sheets():
        logger.info(f"processing sheet '{sheet.title}'")
        try:
            # will raise if headers are missing
            key_col, kpi_col = excel.find_columns(sheet)
        except ValueError as e:
            logger.error(str(e))
            continue

        # iterate each data row
        for row_idx, key_cell, kpi_cell in excel.iter_sheet_rows(sheet):
            total_rows += 1
            logger.info(f"sheet={sheet.title} row={row_idx}")

            key_val = key_cell.value
            # treat blank or whitespace as missing
            if key_val is None or str(key_val).strip() == "" or key_val == "null":
                # ensure KPI is blank too
                if kpi_cell.value not in EMPTY:
                    kpi_cell.value = "null"
                logger.debug("no key parameters; skipping")
                excel.save()
                continue

            # if KPI cell already has a value we treat row as completed
            if kpi_cell.value not in EMPTY:
                logger.debug("row already processed; caching and skipping")
                try:
                    result_obj: Any
                    if isinstance(kpi_cell.value, str):
                        result_obj = json.loads(kpi_cell.value)
                    else:
                        result_obj = kpi_cell.value
                    canonical = normalize_json(str(key_val))
                    cache.set(canonical, result_obj)
                except Exception as e:
                    logger.warning(f"could not cache existing KPI value: {e}")
                continue

            # parse key parameters json and normalize
            try:
                canonical = normalize_json(str(key_val))
            except Exception as e:
                logger.error(f"invalid JSON in key parameters at row {row_idx}: {e}")
                # leave KPI blank so it can be retried later
                continue

            # check cache for previous result
            if canonical in cache:
                logger.info(f"cache hit for sheet={sheet.title} row={row_idx}; reusing KPI from cache")
                kpi_cell.value = json.dumps(cache.get(canonical))
                excel.save()
                continue

            # need to call LLM (cache miss)
            logger.debug("cache miss; invoking LLM")
            try:
                prompt = build_kpi_prompt(json.loads(canonical))
                response = call_llm(prompt)
                # make sure we have something JSON serializable
                response_str = str(response)
                try:
                    response_obj = json.loads(response_str)
                except json.JSONDecodeError:
                    # if parsing fails, we still store the raw string
                    response_obj = response_str
                    logger.warning(f"LLM returned non-JSON response for row {row_idx}")
                # store result in sheet and cache
                kpi_cell.value = json.dumps(response_obj)
                cache.set(canonical, response_obj)
                excel.save()
                logger.info(f"LLM call succeeded for row {row_idx}")
            except Exception as e:
                logger.error(f"error processing row {row_idx}: {e}")
                # continue to next row without stopping
                continue

    logger.info(f"total rows processed: {total_rows}")
    logger.info("processing complete")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logger.critical(f"fatal error: {exc}")
        sys.exit(1)
