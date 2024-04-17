import json
import os
import time
import requests
import random
from bs4 import BeautifulSoup
from datetime import datetime

ad_data_list = []
resource = "hata.by"
towns_list = ["Брест", "Витебск", "Гомель", "Гродно", "Минск", "Могилев"]
common_url_list = ["https://brest.hata.by/rentsutki-flat/", "https://vitebsk.hata.by/rentsutki-flat/",
                   "https://gomel.hata.by/rentsutki-flat/", "https://grodno.hata.by/rentsutki-flat/",
                   "https://www.hata.by/rentsutki-flat/", "https://mogilev.hata.by/rentsutki-flat/"]
headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/122.0.0.0 Mobile Safari/537.36 Edg/122.0.0.0"
        }


def get_data(url, region):
    all_ads = requests.get(url, headers=headers)

    folder_name = f"hata_by/items/region_{region + 1}"

    if not os.path.exists(folder_name):
        os.mkdir(folder_name)

    folder_name = f"hata_by/items/region_{region + 1}/item_1"

    if not os.path.exists(folder_name):
        os.mkdir(folder_name)

    pattern_file_name = f"{folder_name}/pattern_1.html"

    with open(pattern_file_name, "w", encoding="utf-8") as file:
        file.write(all_ads.text)

    with open(pattern_file_name, "r", encoding="utf-8") as file:
        source = file.read()

    soup = BeautifulSoup(source, "lxml")

    ads = soup.find_all("div", class_="b-specials__item")

    ad_urls = []
    for ad in ads:
        ad_url = ad.find("a", target="_blank").get("href")
        ad_urls.append(ad_url)

    for ad_url in ad_urls:
        request = requests.get(ad_url, headers=headers)
        page_id = ad_url.split('/')[-2]
        file_name = f"{folder_name}/{page_id}.html"

        with open(file_name, "w", encoding="utf-8") as file:
            file.write(request.text)

        with open(file_name, "r", encoding="utf-8") as file:
            ad = file.read()

        soup = BeautifulSoup(ad, "lxml")

        try:
            address_raw = soup.find("div", class_="b-card__address noprint").find("a").find("span")
            address_text = address_raw.text
            address_parts = address_text.split()
            del address_parts[0]
            to_edit = address_parts.pop(-3)
            address_parts.insert(-2, to_edit + ",")
            address = " ".join(address_parts).strip()
        except Exception:
            address = "NULL"

        try:
            price_raw = soup.find("div", class_="value").text
            price_parts = price_raw.split()
            price = price_parts[0]
            to_delete = [" "]
            price_doll = int("".join([i for i in price if i not in to_delete]))
            price = price_doll * 3.3 * 100
            price = round(price)
        except Exception:
            price = -1

        try:
            phone_number_raw = soup.find("div", style="width:260px; float: left; margin-bottom: 5px;").text.strip()
            phone_number = phone_number_raw.split("  ")[0].strip()
            to_delete = ["+", "-", " ", "(", ")"]
            phone_number = "".join([i for i in phone_number if i not in to_delete]).strip()
        except Exception:
            phone_number = "NULL"

        try:
            author_name = soup.find_all("div", class_="contact_block my-1")[0].find_all("div")[1].text.strip()
        except Exception:
            author_name = "NULL"

        current_date = datetime.now()
        formatted_date = current_date.strftime('%d.%m.%Y')

        try:
            date = soup.find_all("table", class_="i-table")[2].find_all("td", class_="value")[-2].text.strip()
        except Exception:
            date = "NULL"

        try:
            floor_raw = soup.find_all("table", class_="i-table")[0].find("tr").text.split()
            if floor_raw[0] == "Этаж":
                floor = floor_raw[-3]
            else:
                floor = -1
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
