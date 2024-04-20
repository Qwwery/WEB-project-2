from string import ascii_uppercase, ascii_letters, digits
from email_validator import validate_email


def check_simvols(password):
    s = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', '-', '=',
         '{', '}', '|', ':', ';', '"', '<', '>', '.', '?', '/', "'"]
    check_string = set(ascii_uppercase) | set(ascii_letters) | set(digits) | set(s)
    for simvol in password:
        if simvol not in check_string:
            return False
    return True


def check_correct_domen_user(domen):
    if len(domen) > 20:
        return False, 'Длина псевдонима не должна превышать 20 символов'

    check_string = set(ascii_uppercase) | set(ascii_letters) | set(digits) | set('_')
    for elem in domen:
        if elem not in check_string:
            return False, 'В псевдониме разрешены только латинские буквы, цифры и символ "_"'

    if domen.count('_') > 5:
        return False, 'В псевдониме символ "_" можно использовать не более 5 раз'

    return True, 'успех'


def check_correct_password(password):
    if not (8 <= len(password) <= 16):
        return False, 'длина пароля от 8 до 16 символов'
    if len(set(password) & (set(digits))) == 0:
        return False, 'пароль должен содержать хотя бы одну цифру'
    if len(set(password) & set(ascii_letters)) == 0:
        return False, 'пароль должен содержать хотя бы одну строчную латинскую букву'
    if len(set(password) & set(ascii_uppercase)) == 0:
        return False, 'пароль должен содержать хотя бы одну заглавную латинскую букву'
    if check_simvols(password):
        return True, 'успех'
    else:
        s = ' '.join(['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', '-', '=',
                      '{', '}', '|', ':', ';', '"', '<', '>', '.', '?', '/', "'"])
        return False, f'пароль должен содержать только латинские буквы и цифры или специальные символы {s}'


def check_correct_email(email):
    try:
        result = validate_email(email)
        return True, 'да'
    except Exception as e:
        return False, e
