from . import en, ru, hy

TRANSLATIONS = {
    'en': en.MESSAGES,
    'ru': ru.MESSAGES,
    'hy': hy.MESSAGES,
}

DEFAULT_LANG = 'en'


def get_message(lang: str, key: str, **kwargs) -> str:
    lang = lang if lang in TRANSLATIONS else DEFAULT_LANG
    template = TRANSLATIONS[lang].get(key, TRANSLATIONS[DEFAULT_LANG].get(key, key))
    return template.format(**kwargs)


def supported_languages() -> set[str]:
    return set(TRANSLATIONS.keys())
