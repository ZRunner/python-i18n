from typing import Dict, Union

from . import config

container: Dict[str, Union[dict, list, str]] = {}


def add(key: str, value: str, locale: str = config.get('locale')):
    """Add a key-value translation in the given language

    Already existing translations for this language and this key will NOT be overwritten"""
    container.setdefault(locale, {})[key] = value


def has(key: str, locale: str = config.get('locale')):
    """Check if a translation exists for that specific key and language"""
    return key in container.get(locale, {})


def get(key: str, locale: str = config.get('locale')) -> Union[dict, list, str]:
    """Get the translation corresponding to that key and language"""
    return container[locale][key]
