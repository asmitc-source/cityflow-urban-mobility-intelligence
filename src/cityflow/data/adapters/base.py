from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class SourceMetadata:
    source_name: str
    source_url: str
    refresh_frequency: str
    owner: str


class SourceAdapter(ABC):
    """Contract for mapping external public data into CityFlow canonical tables."""

    metadata: SourceMetadata

    @abstractmethod
    def extract(self, source_path: Path | str) -> pd.DataFrame:
        """Load raw source data from a file path, API export, or staging object."""

    @abstractmethod
    def normalize(self, raw: pd.DataFrame) -> pd.DataFrame:
        """Return source data mapped to a CityFlow canonical schema."""

    def validate_required_columns(self, frame: pd.DataFrame, required: set[str]) -> None:
        missing = required.difference(frame.columns)
        if missing:
            raise ValueError(f"{self.metadata.source_name} missing required columns: {sorted(missing)}")

