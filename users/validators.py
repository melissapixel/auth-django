import re   # Импортируем модуль для работы с регулярными выражениями
from django.core.exceptions import ValidationError  # Импортируем исключение для валидации
from django.utils.translation import gettext as _   # Импортируем функцию для перевода сообщений


class UppercaseLetterValidator:
    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("Пароль должен содержать хотя бы одну заглавную букву."),
                code='password_no_upper',
            )

    def get_help_text(self):
        return _("Ваш пароль должен содержать хотя бы одну заглавную букву.")


class DigitValidator:
    def validate(self, password, user=None):
        if not re.search(r'\d', password):
            raise ValidationError(
                _("Пароль должен содержать хотя бы одну цифру."),
                code='password_no_digit',
            )

    def get_help_text(self):
        return _("Ваш пароль должен содержать хотя бы одну цифру.")


class SpecialCharValidator:
    def validate(self, password, user=None):
        if not re.search(r'[!@#$%^&*()_+={}\[\]|\\:";\'<>?,./`~\-]', password):
            raise ValidationError(
                _("Пароль должен содержать хотя бы один спецсимвол (!@#$%^&* и др.)."),
                code='password_no_special',
            )

    def get_help_text(self):
        return _("Ваш пароль должен содержать хотя бы один спецсимвол.")


def name_validator(value):
    if not re.match(r'^[a-zA-Zа-яА-Я\s\-\'\`]+$', value):
        raise ValidationError(
            _("Имя может содержать только буквы, пробелы, дефисы и апострофы."),
            code='invalid_name',
        )