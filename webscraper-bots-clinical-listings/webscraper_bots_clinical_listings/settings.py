from selenium.webdriver.common.proxy import Proxy, ProxyType
import os

PROXY = {
    "httpProxy": os.getenv('http_proxy'),
    "ftpProxy": None,
    "sslProxy": os.getenv('https_proxy')
}
if any(PROXY.values()):
    PROXY['proxyType'] = ProxyType.MANUAL
else:
    PROXY['proxyType'] = ProxyType.AUTODETECT

PROXY = Proxy(PROXY)


DB_CREDENTIALS = {
    'user': '',
    'password': '',
    'dbname': '',
    'host': ''
}


DEFAULT_IMPLICIT_WAIT = 10
DEFAULT_WAIT_TIMEOUT = 10
