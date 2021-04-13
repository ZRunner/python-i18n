from string import Template
from typing import Any, Dict, List, Union

from . import config
from . import resource_loader
from . import translations


class TranslationFormatter(Template):
    """Class used to format a specific translation"""

    delimiter = config.get('placeholder_delimiter')

    def __init__(self, template: str):
        super(TranslationFormatter, self).__init__(template)

    def format(self, **kwargs):
        """Format the template with the given values
        
        If a value is missing, the function will either silently ignores it or
        raise an error, depending of your config"""
        if config.get('error_on_missing_placeholder'):
            return self.substitute(**kwargs)
        else:
            return self.safe_substitute(**kwargs)


def t(key: str, **kwargs) -> Union[str, list]:
    """Get a translation

    If 'locale' is not specified, it will be taken from the configuration.
    If 'locale' is specified but cannot be found, it will use the fallback language from config

    You can use the 'count' kwarg to specify a count (pluralization system)
    
    Any other kwarg will be used to format the result"""
    locale = kwargs.pop('locale', config.get('locale'))
    if translations.has(key, locale):
        return translate(key, locale=locale, **kwargs)
    else:
        resource_loader.search_translation(key, locale)
        if translations.has(key, locale):
            return translate(key, locale=locale, **kwargs)
        elif locale != config.get('fallback'):
            return t(key, locale=config.get('fallback'), **kwargs)
    if 'default' in kwargs:
        return kwargs['default']
    if config.get('error_on_missing_translation'):
        raise KeyError('key {0} not found'.format(key))
    else:
        return key


def translate(key: str, **kwargs) -> Union[List[Union[str, Any]], str]:
    """Actually translate something and apply plurals/kwargs if needed
    
    If the translation is a list of strings, each string will be formatted accordingly and the whole list will be returned"""
    locale = kwargs.pop('locale', config.get('locale'))
    translation = translations.get(key, locale=locale)
    if isinstance(translation, list):
        # if we can apply plural/formats to the items, let's try
        if all(isinstance(data, (str, dict)) for data in translation):
            # if needed, we should format every item in the list
            if 'count' in kwargs:
                translation = [pluralize(key, data, kwargs['count']) for data in translation]
            # items may be non-plural dictionnaries, which we cannot format
            return [TranslationFormatter(data).format(**kwargs) if isinstance(data, str) else data for data in translation]
        return translation
    if 'count' in kwargs:
        translation = pluralize(key, translation, kwargs['count'])
    return TranslationFormatter(translation).format(**kwargs)


def pluralize(key: str, translation: Dict[str, str], count: int) -> str:
    """Find the right string to use for the corresponding count
    
    If the translation isn't a dictionnary, cannot be used for plural,
    or if the count isn't in the dict, the function may either return the key,
    the translation, or raise an error if specified by the config"""
    return_value = key
    try:
        if type(translation) != dict:
            return_value = translation
            raise KeyError('use of count witouth dict for key {0}'.format(key))
        if count == 0:
            if 'zero' in translation:
                return translation['zero']
        elif count == 1:
            if 'one' in translation:
                return translation['one']
        elif count <= config.get('plural_few'):
            if 'few' in translation:
                return translation['few']
        # TODO: deprecate other
        if 'other' in translation:
            return translation['other']
        if 'many' in translation:
            return translation['many']
        else:
            raise KeyError('"many" not defined for key {0}'.format(key))
    except KeyError as e:
        if config.get('error_on_missing_plural'):
            raise e
        else:
            return return_value
