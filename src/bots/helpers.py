import json

def read_secret(key):
    secrets_file = open('./src/secrets.json')
    secrets_content = secrets_file.read()
    return json.loads(secrets_content)[key]

def read_section_secret(section, key):
    secrets_file = open('./src/secrets.json')
    secrets_content = secrets_file.read()
    return json.loads(secrets_content)[section][key]