"""Parse and print cambridge dictionary."""
import requests

from ..dicts import dict
from ..log import logger
from ..settings import OP, DICTS
from ..utils import (
    make_a_soup,
    get_request_url,
    get_request_url_spellcheck,
    parse_response_url,
)

CAMBRIDGE_URL = "https://dictionary.cambridge.org"
CAMBRIDGE_DICT_BASE_URL = CAMBRIDGE_URL + "/dictionary/english/"
CAMBRIDGE_SPELLCHECK_URL = CAMBRIDGE_URL + "/spellcheck/english/?q="


# ----------Request Web Resource----------
def search_cambridge(con, cur, input_word, is_fresh=False):
    req_url = get_request_url(CAMBRIDGE_DICT_BASE_URL, input_word, DICTS[0])

    if not is_fresh:
        cached, soup = dict.cache_run(con, cur, input_word, req_url)
        if not cached:
            return fresh_run(con, cur, req_url, input_word)
        return req_url, soup
    else:
        return fresh_run(con, cur, req_url, input_word)


def fetch_cambridge(req_url, input_word):
    """Get response url and response text for later parsing."""

    with requests.Session() as session:
        session.trust_env = False  # not to use proxy
        res = dict.fetch(req_url, session)

        if res.url == CAMBRIDGE_DICT_BASE_URL:
            logger.debug(f'{OP[6]} "{input_word}" in {DICTS[0]}')
            spell_req_url = get_request_url_spellcheck(CAMBRIDGE_SPELLCHECK_URL, input_word)

            spell_res = dict.fetch(spell_req_url, session)
            spell_res_url = spell_res.url
            spell_res_text = spell_res.text
            return False, (spell_res_url, spell_res_text)

        else:
            res_url = parse_response_url(res.url)
            res_text = res.text

            logger.debug(f'{OP[5]} "{input_word}" in {DICTS[0]} at {res_url}')
            return True, (res_url, res_text)


def fresh_run(con, cur, req_url, input_word):
    """Print the result without cache."""

    result = fetch_cambridge(req_url, input_word)
    found = result[0]

    if found:
        res_url, res_text = result[1]
        soup = make_a_soup(res_text)
        response_word = parse_response_word(soup)
        expected = soup.body.find('div', {'class': 'page'})
        soup.body.clear()
        soup.body.append(expected)

        dict.save(con, cur, input_word, response_word, res_url, str(soup))
        return res_url, soup
    else:
        spell_res_url, spell_res_text = result[1]
        logger.debug(f"{OP[4]} the parsed result of {spell_res_url}")

        soup = make_a_soup(spell_res_text)
        nodes = soup.find("div", "hfl-s lt2b lmt-10 lmb-25 lp-s_r-20")
        nodes = nodes.find("ul", "hul-u")
        soup.body.clear()
        if nodes:
            soup.body.append(nodes)
        return spell_res_url, soup


def parse_response_word(soup):
    """Parse the response word from html head title tag."""

    temp = soup.find("title").text.split("-")[0].strip()
    if "|" in temp:
        response_word = temp.split("|")[0].strip().lower()
    else:
        response_word = temp.lower()

    return response_word
