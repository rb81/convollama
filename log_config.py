import logging
import os
from datetime import datetime
from rich.logging import RichHandler

def setup_logging(level):
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"convollama_{timestamp}.log")

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="[%X]",
        handlers=[
            logging.FileHandler(log_file),
            RichHandler(rich_tracebacks=True, markup=True)
        ]
    )

    logging.info(f"Logging initialized. Log file: {log_file}")
