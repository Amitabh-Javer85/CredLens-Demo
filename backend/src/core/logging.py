import json
import logging
import sys
import time
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """
    Structured logging formatter that outputs logs as JSON strings.
    """
    def __init__(self, **kwargs):
        super().__init__()
        self.default_keys = kwargs

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "file": f"{record.pathname}:{record.lineno}",
            "function": record.funcName,
        }
        
        # Inject standard default keys
        for k, v in self.default_keys.items():
            log_data[k] = v

        # Inject extra fields if present
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "lender_id"):
            log_data["lender_id"] = record.lender_id
        if hasattr(record, "application_id"):
            log_data["application_id"] = record.application_id
            
        # Add details from dict if passed via extra
        if isinstance(record.args, dict):
            for k, v in record.args.items():
                log_data[k] = v
                
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)

    def formatTime(self, record: logging.LogRecord, datefmt: str = None) -> str:
        ct = self.converter(record.created)
        if datefmt:
            s = time.strftime(datefmt, ct)
        else:
            t = time.strftime("%Y-%m-%dT%H:%M:%S", ct)
            s = f"{t}.{int(record.msecs):03d}Z"
        return s


def setup_logger(name: str = "credlens") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handler attachments
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        formatter = JSONFormatter(service=name)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    logger.propagate = False
    return logger


logger = setup_logger()
