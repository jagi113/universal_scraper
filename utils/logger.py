import logging
from datetime import datetime
import os


# Setup logg out file
log_path = os.path.join(os.getcwd(), "logs")
if not os.path.exists(log_path):
    os.mkdir(log_path)
log_file = os.path.join(log_path, f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter(
    "%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s"
)

# Create console handler
console_log = logging.StreamHandler()
console_log.setLevel(logging.INFO)
# Add formatter to console handler
console_log.setFormatter(formatter)
# Add console handler to logger
logger.addHandler(console_log)

# Create file handler
file_log = logging.FileHandler(log_file, mode="a")
file_log.setLevel(logging.DEBUG)
# Add formatter to file handler
file_log.setFormatter(formatter)
# Add file handler to logger
logger.addHandler(file_log)
