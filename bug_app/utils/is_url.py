from urllib.parse import urlparse

def is_https_url(url):
    parsed_url = urlparse(url)
    return parsed_url.scheme == 'https'