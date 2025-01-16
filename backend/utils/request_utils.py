import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def get_session_with_retries():
    session = requests.Session()
    retries = Retry(
        total=5,  # Retry up to 5 times
        backoff_factor=0.5,  # Exponential backoff
        status_forcelist=[500, 502, 503, 504],  # Retry on these status codes
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    return session