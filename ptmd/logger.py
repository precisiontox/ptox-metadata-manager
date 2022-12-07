""" Small module to make the logger easy to import

@author: D. Batista (Terazus)
"""

from logging import getLogger, basicConfig, DEBUG

LOGGER = getLogger('ptmd')
basicConfig(format="%(asctime)s [%(levelname)s]: %(filename)s(%(funcName)s:%(lineno)s) >> %(message)s")
LOGGER.setLevel(DEBUG)
