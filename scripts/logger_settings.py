import logging

# Create custom logger
logger = logging.getLogger("scripts")
logger.setLevel(logging.DEBUG)
# logger.setLevel(logging.INFO)

# Create a handler
handler = logging.StreamHandler()
# Modify according to your preferred logging level.
handler.setLevel(logging.DEBUG)
# handler.setLevel(logging.INFO)
# handler.setLevel(logging.WARNING)
# handler.setLevel(logging.ERROR)

# Create formatter and add it to the handler
# logger_format = logging.Formatter('%(name)s : %(funcName)s : %(levelname)s : %(message)s')
# logger_format = logging.Formatter('%(levelname)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s')
logger_format = logging.Formatter('%(levelname)s: %(funcName)s: %(message)s')
handler.setFormatter(logger_format)

# Add handler to the logger
logger.addHandler(handler)
