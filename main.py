import json
import re
from itertools import product
from pathlib import Path

import requests
from lxml import html

build_path = Path().cwd().joinpath("build")
build_path.mkdir(exist_ok=True)

base_url = "https://www.useragents.me"

mobile_os_field_patterns = [
    re.compile(r"windows mobile", flags=re.IGNORECASE),
    re.compile(r"iphone", flags=re.IGNORECASE),
    re.compile(r"ipad", flags=re.IGNORECASE),
    re.compile(r"android", flags=re.IGNORECASE),
]

desktop_os_field_patterns = [
    re.compile(r"windows nt \d+\.\d+", flags=re.IGNORECASE),
    re.compile(r"macintosh", flags=re.IGNORECASE),
    re.compile(r"linux (x86_64|i686)", flags=re.IGNORECASE),
]


def main():
    desktop_uas = []
    mobile_uas = []

    response = requests.get(base_url)
    ua_elements = html.fromstring(response.content).cssselect("textarea")

    for element in ua_elements:
        ua = element.text_content().strip()
        if not ua.startswith("Mozilla/5.0 ("):
            continue

        platform = ua[len("Mozilla/5.0 (") : ua.find(")")].lower()
        platform_tokens = [p.strip() for p in platform.split(";")]

        if any(
            p.match(t) for p, t in product(mobile_os_field_patterns, platform_tokens)
        ):
            mobile_uas.append(ua)
        elif any(
            p.match(t) for p, t in product(desktop_os_field_patterns, platform_tokens)
        ):
            desktop_uas.append(ua)

    if len(desktop_uas) == 0 or len(mobile_uas) == 0:
        raise Exception("Failed to collect user agents")

    ua_dict = {"desktop": desktop_uas, "mobile": mobile_uas}

    for minified in [True, False]:
        file_path = build_path.joinpath(f"user-agents{'.min' if minified else ''}.json")
        with open(file_path, "w+") as file:
            json_str = json.dumps(
                ua_dict,
                indent=None if minified else 2,
                separators=(",", ":") if minified else None,
            )
            file.write(json_str + "\n")


if __name__ == "__main__":
    main()
