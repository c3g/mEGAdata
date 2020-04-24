import logging

# Create custom logger
logger = logging.getLogger("scripts")
logger.setLevel(logging.INFO)

# Create a handler
handler = logging.StreamHandler()
# Modify according to your preferred logging level.
# handler.setLevel(logging.INFO)
handler.setLevel(logging.WARNING)
# handler.setLevel(logging.ERROR)

# Create formatter and add it to the handler
logger_format = logging.Formatter('%(name)s : %(levelname)s : %(message)s')
handler.setFormatter(logger_format)

# Add handler to the logger
logger.addHandler(handler)
