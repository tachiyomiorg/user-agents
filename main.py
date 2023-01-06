import json
import os
import random
import re
import time
from itertools import product
from pathlib import Path

import requests
from lxml import html

build_path = Path().cwd().joinpath("build")
build_path.mkdir(exist_ok = True)

base_url = 'https://www.whatismybrowser.com/guides/the-latest-user-agent'

browsers = ['chrome', 'firefox', 'safari', 'edge', 'opera', 'vivaldi']

mobile_os_field_patterns = [
    re.compile(r'windows mobile', flags = re.IGNORECASE),
    re.compile(r'iphone', flags = re.IGNORECASE),
    re.compile(r'ipad', flags = re.IGNORECASE),
    re.compile(r'android', flags = re.IGNORECASE),
]

desktop_os_field_patterns = [
    re.compile(r'windows nt \d+\.\d+', flags = re.IGNORECASE),
    re.compile(r'macintosh', flags = re.IGNORECASE),
    re.compile(r'linux (x86_64|i686)', flags = re.IGNORECASE),
]

def get_user_agent() -> str:
    if os.getenv("CI", None) == "true":
        # Running in CI (GitHub Actions)
        print("Running in CI mode")
        with open("gh-pages/user-agents.min.json") as ua_file:
            desktop_uas = json.load(ua_file)["desktop"]
            return random.choice(desktop_uas)

    return input("Provide a user agent for scraping -> ").strip()

def main():
    desktop_uas = []
    mobile_uas = []

    user_agent = get_user_agent()

    for browser in browsers:
        print(f"Collecting user agents of {browser}")
        response = requests.get(f"{base_url}/{browser}", headers={'User-Agent': user_agent})

        ua_elements = html.fromstring(response.content).cssselect('td li span.code')

        for element in ua_elements:
            ua = element.text_content().strip()
            if not ua.startswith('Mozilla/5.0 ('):
                continue

            platform = ua[len('Mozilla/5.0 ('):ua.find(')')].lower()
            platform_tokens = [p.strip() for p in platform.split(';')]

            if any(p.match(t) for p, t in product(mobile_os_field_patterns, platform_tokens)):
                mobile_uas.append(ua)
            elif any(p.match(t) for p, t in product(desktop_os_field_patterns, platform_tokens)):
                desktop_uas.append(ua)

            time.sleep(1)

    ua_dict = {
        "desktop": desktop_uas,
        "mobile": mobile_uas
    }

    for minified in [True, False]:
        file_path = build_path.joinpath(f"user-agents{'.min' if minified else ''}.json")
        with open(file_path, "w+") as file:
            json_str = json.dumps(
                ua_dict,
                indent = None if minified else 2,
                separators = (",", ":") if minified else None,
            )
            file.write(json_str + '\n')


if __name__ == '__main__':
    main()
