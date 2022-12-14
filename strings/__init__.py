
import os
from typing import List

import yaml

languages = {}
commands = {}


def get_command(value: str) -> List:
    return commands["command"][value]


def get_string(lang: str):
    return languages[lang]


for filename in os.listdir(r"./strings"):
    if filename.endswith(".yml"):
        language_name = filename[:-4]
        commands[language_name] = yaml.safe_load(
            open(r"./strings/" + filename, encoding="utf8")
        )

for filename in os.listdir(r"./strings/langs/"):
    if filename.endswith(".yml"):
        language_name = filename[:-4]
        languages[language_name] = yaml.safe_load(
            open(r"./strings/langs/" + filename, encoding="utf8")
        )
