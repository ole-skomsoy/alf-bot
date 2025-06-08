import json

def read_secret(key):
    secrets_file = open('./src/secrets.json')
    secrets_content = secrets_file.read()
    return json.loads(secrets_content)[key]

def read_section_secret(section, key):
    secrets_file = open('./src/secrets.json')
    secrets_content = secrets_file.read()
    return json.loads(secrets_content)[section][key]

def add_ordinal_suffix(n):
    last_two_digits = n % 100
    if 11 <= last_two_digits <= 13:
        return f"{n}th"

    last_digit = n % 10
    if last_digit == 1:
        return f"{n}st"
    elif last_digit == 2:
        return f"{n}nd"
    elif last_digit == 3:
        return f"{n}rd"

    return f"{n}th"