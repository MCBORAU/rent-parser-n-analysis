import json
import os
import time
import requests
import random
from bs4 import BeautifulSoup
from datetime import datetime

ad_data_list = []
resource = "neagent.by"
towns_list = ["Брест", "Витебск", "Гомель", "Гродно", "Минск", "Могилев"]
common_url_list = ["https://neagent.by/brest/kvartira/na-sutki", "https://neagent.by/vitebsk/kvartira/na-sutki",
                   "https://neagent.by/gomel/kvartira/na-sutki", "https://neagent.by/grodno/kvartira/na-sutki",
                   "https://neagent.by/kvartira/na-sutki", "https://neagent.by/mogilev/kvartira/na-sutki"]
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0"
}


def get_data(url, region):
    all_ads = requests.get(url, headers=headers)

    folder_name = f"neagent_by/items/region_{region + 1}"

    if not os.path.exists(folder_name):
        os.mkdir(folder_name)

    folder_name = f"neagent_by/items/region_{region + 1}/item_1"

    if not os.path.exists(folder_name):
        os.mkdir(folder_name)

    pattern_file_name = f"{folder_name}/pattern_1.html"

    with open(pattern_file_name, "w", encoding="utf-8") as file:
        file.write(all_ads.text)

    with open(pattern_file_name, "r", encoding="utf-8") as file:
        source = file.read()

    soup = BeautifulSoup(source, "lxml")

    ads = soup.find_all("div", class_="c-card__column-left")

    ad_urls = []
    for ad in ads:
        ad_url = ad.find("a").get("href")
        ad_urls.append(ad_url)

    for ad_url in ad_urls:
        request = requests.get(ad_url, headers=headers)
        page_id = ad_url.split('/')[-1]
        file_name = f"{folder_name}/{page_id}.html"

        with open(file_name, "w", encoding="utf-8") as file:
            file.write(request.text)

        with open(file_name, "r", encoding="utf-8") as file:
            ad = file.read()

        soup = BeautifulSoup(ad, "lxml")

        try:
            address_raw = soup.find("div", class_="page-header page-header_no-mb page-header_mb--pho "
                                                  "text-left").find("h1")
            address_text = address_raw.text
            address_parts = address_text.split(",")
            del address_parts[0], address_parts[-1]
            address = f"{towns_list[region]}, " + ",".join(address_parts).strip()
        except Exception:
            address = "NULL"

        try:
            price_raw = soup.find("div", class_="page-header page-header_no-mb page-header_mb--pho "
                                                "text-left").find("h1")
            price_text = price_raw.text
            price_parts = price_text.split(",")[-1].split()
            price = int(price_parts[0])*100
        except Exception:
            price = -1

        try:
            phone_number_raw = soup.find("div", class_="agent-content").find("div").get("title")
            phone_number_parts = phone_number_raw.split()
            del phone_number_parts[0]
            phone_number_parts = " ".join(phone_number_parts)
            phone_number_parts.split()
            to_delete = ["+", "-", " ", "(", ")"]
            phone_number = "".join([i for i in phone_number_parts if i not in to_delete]).strip()
        except Exception:
            phone_number = "NULL"

        try:
            author_name = soup.find("div", class_="cname").text.strip()
        except Exception:
            author_name = "NULL"

        current_date = datetime.now()
        formatted_date = current_date.strftime('%d.%m.%Y')

        try:
            date_raw = soup.find("span", class_="ann-contact__date").text
            date_parts = date_raw.split()
            date_obj = datetime.strptime(date_parts[0], "%Y-%m-%d")
            date = date_obj.strftime("%d.%m.%Y")
        except Exception:
            date = "NULL"

        try:
            floor_raw = soup.find_all("div", class_="key-value-item equal-cols")[2].find("div", class_="value "
                                                                                                       "text-right").text
            floor = floor_raw.split()[0]
        except Exception:
            floor = -1

        ad_data_list.append(
            {
                "Address": address,
                "Price": price,
                "Phone": phone_number,
                "Author": author_name,
                "Parse date": formatted_date,
                "Date": date,
                "Floor": floor,
                "Resource": resource
            }
        )

        time.sleep(random.randrange(2, 4))


def create_json_file():
    file_name = f"data_JSON/ad_data_{resource}.json"

    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as file:
            data = json.load(file)
    else:
        data = []

    for new_record in ad_data_list:
        exists = False
        for record in data:
            if all(new_record[key] == record[key] for key in new_record if key != "Parse date"):
                exists = True
                break
        if not exists:
            data.append(new_record)

    corrected_data = [record for record in data if record.get("Date") != "NULL"]

    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(corrected_data, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    for region in range(len(towns_list)):
        get_data(common_url_list[region], region)
    create_json_file()
