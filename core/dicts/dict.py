"""Shared functionality of all dictionaries."""

import sqlite3

import requests
from fake_user_agent import user_agent
from ..cache import insert_into_table, get_cache
from ..errors import call_on_error
from ..log import logger
from ..settings import OP
from ..utils import make_a_soup


def fetch(url, session):
    """Make a web request with retry mechanism."""

    ua = user_agent()
    headers = {"User-Agent": ua}
    session.headers.update(headers)
    attempt = 0

    while True:
        try:
            logger.debug(f"{OP[0]} {url}")
            r = session.get(url, timeout=9.05)
        except requests.exceptions.HTTPError as e:
            attempt = call_on_error(e, url, attempt, OP[2])
            continue
        except requests.exceptions.ConnectTimeout as e:
            attempt = call_on_error(e, url, attempt, OP[2])
            continue
        except requests.exceptions.ConnectionError as e:
            attempt = call_on_error(e, url, attempt, OP[2])
            continue
        except requests.exceptions.ReadTimeout as e:
            attempt = call_on_error(e, url, attempt, OP[2])
            continue
        except Exception as e:
            attempt = call_on_error(e, url, attempt, OP[2])
            continue
        else:
            return r


def cache_run(con, cur, input_word, req_url):
    """Check the cache is from Cambridge or Merrian Webster."""

    # data is a tuple (response_url, response_text) if any
    data = get_cache(con, cur, input_word, req_url)

    if data is not None:
        res_url, res_text = data
        return True, make_a_soup(res_text)

    return False, None


def save(con, cur, input_word, response_word, response_url, response_text):
    """Save a word info into local DB for cache."""

    try:
        insert_into_table(
            con, cur, input_word, response_word, response_url, response_text
        )
        logger.debug(f'{OP[7]} the search result of "{input_word}"')
    except sqlite3.IntegrityError as error:
        if "UNIQUE constraint" in str(error):
            logger.debug(f'{OP[8]} caching "{input_word}" - [ERROR] - already cached before\n')
        else:
            logger.debug(f'{OP[8]} caching "{input_word}" - [ERROR] - {error}\n')
    except sqlite3.InterfaceError as error:
        logger.debug(f'{OP[8]} caching "{input_word}" - [ERROR] - {error}\n')
