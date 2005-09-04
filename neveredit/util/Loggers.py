import logging

logger = logging.getLogger('neveredit')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(levelname)s %(module)s: %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.WARN)

logger = logging.getLogger('neveredit.file')
logger.setLevel(logging.WARN)

logger = logging.getLogger('neveredit.ui')
logger.setLevel(logging.WARN)

logger = logging.getLogger('neveredit.game')
logger.setLevel(logging.WARN)
