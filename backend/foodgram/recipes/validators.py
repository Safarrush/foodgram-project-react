from django.core.exceptions import ValidationError

def validate_hex_color(value):
    if not value.startswith('#'):
        raise ValidationError('Цвет должен начинаться с символа #')
    
    hex_digits = set('0123456789ABCDEFabcdef')
    if not all(c in hex_digits for c in value[1:]):
        raise ValidationError('Некорректный HEX цвет')
    
    if len(value) != 7:
        raise ValidationError('HEX цвет должен состоять из 6 символов')
