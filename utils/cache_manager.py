import json
import os
from typing import Any, Optional

from utils.logger import logger


class Cache:
    """Simple file-backed cache for mapping key-parameters to KPI results.

    The underlying store is a JSON file. The keys are canonical JSON strings
    (sorted keys) and the values are arbitrary JSON-serializable objects
    returned by the LLM.
    """

    def __init__(self, path: str) -> None:
        self.path = path
        self._data: dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
                logger.info(f"Loaded cache ({len(self._data)} entries) from {self.path}")
            except Exception as e:
                logger.error(f"Failed to load cache from {self.path}: {e}")
                self._data = {}
        else:
            # ensure directory exists so later saves don't fail
            directory = os.path.dirname(self.path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            self._data = {}

    def save(self) -> None:
        try:
            directory = os.path.dirname(self.path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
            logger.debug(f"Cache saved to {self.path}")
        except Exception as e:
            logger.error(f"Failed to save cache to {self.path}: {e}")

    def get(self, key: str) -> Optional[Any]:
        return self._data.get(key)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self.save()

    def __contains__(self, key: str) -> bool:
        return key in self._data
