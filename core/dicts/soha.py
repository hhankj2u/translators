"""Fetch, parse, print, and save Webster dictionary."""

import requests

from ..dicts import dict
from ..log import logger
from ..settings import OP, DICTS
from ..utils import get_request_url, make_a_soup

SOHA_BASE_URL = "http://tratu.soha.vn"
SOHA_DICT_BASE_URL = SOHA_BASE_URL + "/dict/en_vn/"

res_word = ""


# ----------Request Web Resource----------
def search_soha(con, cur, input_word, is_fresh=False):
    """
    Entry point for dealing with Merriam-Webster Dictionary.
    It first checks the cache, if the word has been cached,
    uses it and prints it; if not, go fetch the web.
    If the word is found, prints it to the terminal and caches it concurrently.
    if not found, prints word suggestions and exit.
    """

    req_url = get_request_url(SOHA_DICT_BASE_URL, input_word, DICTS[1])

    if not is_fresh:
        cached, soup = dict.cache_run(con, cur, input_word, req_url)
        if not cached:
            return fresh_run(con, cur, req_url, input_word)
        return req_url, soup
    else:
        return fresh_run(con, cur, req_url, input_word)


def fetch_soha(request_url, input_word):
    """Get response url and response text for future parsing."""

    with requests.Session() as session:
        session.trust_env = False
        res = dict.fetch(request_url, session)

        res_url = res.url
        res_text = res.text
        status = res.status_code

        if status == 200:
            logger.debug(f'{OP[5]} "{input_word}" in {DICTS[1]} at {res_url}')
            return True, (res_url, res_text)

        # By default, Requests will perform location redirection for all verbs except HEAD.
        # https://requests.readthedocs.io/en/latest/user/quickstart/#redirection-and-history
        # You don't need to deal with redirection yourself.
        # if status == 301:
        #     loc = res.headers["location"]
        #     new_url = SOHA_BASE_URL + loc
        #     new_res = dict.fetch(new_url, session)

        if status == 404:
            logger.debug(f'{OP[6]} "{input_word}" in {DICTS[1]}')
            return False, (res_url, res_text)


def fresh_run(con, cur, req_url, input_word):
    """Print the result without cache."""

    result = fetch_soha(req_url, input_word)
    found = result[0]
    res_url, res_text = result[1]

    if found:
        soup = make_a_soup(res_text)
        response_word = parse_response_word(soup)
        expected = soup.body.find('div', {'id': 'column-content'})
        soup.body.clear()
        soup.body.append(expected)

        dict.save(con, cur, input_word, response_word, res_url, str(soup))
        return req_url, soup

    else:
        logger.debug(f"{OP[4]} the parsed result of {res_url}")

        soup = make_a_soup(res_text)
        nodes = soup.find('div', {'id': 'column-content'})
        soup.body.clear()
        if nodes:
            soup.body.append(nodes)
        return res_url, soup


def parse_response_word(soup):
    """Parse the response word from h1 tag."""

    return soup.find('h1', 'firstHeading').text
