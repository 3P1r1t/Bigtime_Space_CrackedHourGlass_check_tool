from datetime import datetime, timedelta
from curl_cffi import requests
from rich.console import Console
from rich.theme import Theme

custom_theme = Theme({"info": "dim cyan", "warning": "magenta", "danger": "bold red"})
console = Console(theme=custom_theme)

GREEN = "\033[92m"
RED = "\033[91m"
ENDC = "\033[0m"

headers = {
    "authority": "api.openloot.com",
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9",
    "content-type": "application/json",
    "cookie": "you_data_here",
    "origin": "https://openloot.com",
    "sec-ch-ua": '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "X-client-id": "marketplace",
    "X-device-id": "you_data_here",
    "X-is-mobile": "false",
    "X-session-id": "you_data_here",
    "X-user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
}


def get_openloot_in_game_items(page=1, proxy=None):
    proxies = proxy if proxy else None
    url = f"https://api.openloot.com/v2/market/items/in-game?gameId=56a149cf-f146-487a-8a1c-58dc9ff3a15c&page={page}&pageSize=50&sort=name%3Aasc&tags=space"
    r = requests.get(
        url,
        headers=headers,
        impersonate="chrome110",
        proxies=proxies,
    )
    return r.json()


def calculate_time_difference(timestamp_str):
    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    timestamp = timestamp + timedelta(hours=8)
    current_time = datetime.now()
    time_difference = current_time - timestamp
    remaining_time = timedelta(hours=48) - time_difference

    return remaining_time if remaining_time > timedelta(0) else timedelta(0)

if __name__ == "__main__":
    page = 1
    true_count = 0
    false_count = 0
    max_time = None
    while True:
        try:
            data = get_openloot_in_game_items(page)
            items = data["items"]
            for item in items:
                key = item["issuedId"]
                for att in item["extra"]["attributes"]:
                    if att["name"] == "LastCrackedHourGlassDropTime":
                        timestamp = att["value"]
                        time_diff = calculate_time_difference(timestamp)
                        if max_time is None or time_diff > max_time:
                            max_time = time_diff
                        if time_diff <= timedelta(0):
                            print(f"{GREEN}■{ENDC} #{key:06d}")
                            true_count += 1
                        else:
                            print(f"{RED}■{ENDC} #{key:06d} [ {time_diff} ]")
                            false_count += 1
                        break
        except Exception as e:
            console.log(f"error: {e}", style="warning")
            continue
        page += 1
        if page > data["totalPages"]:
            break

    print(f"\n{GREEN}■ {true_count}{ENDC}")
    print(f"{RED}■ {false_count}{ENDC}")
    print(f"全部刷新时间: {max_time}")
