from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from cityflow.data.warehouse import build_marts, connect_warehouse
from cityflow.models.train import load_training_frame, train_models
from cityflow.utils.config import load_config


def main() -> None:
    config = load_config()
    conn = connect_warehouse()
    build_marts(conn)
    frame = load_training_frame(conn, limit=int(config["modeling"]["max_training_rows"]))
    metrics = train_models(frame)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()

