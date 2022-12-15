""" Constants used by the pretox client. Conteains things such as the headers and the default URL for the requests

"""

from ptmd.const import CONFIG


HEADERS: dict = {"Accept": "application/json", "Content-Type": "application/json"}
DEFAULT_URL = CONFIG['PTOX_API_ENDPOINT']
