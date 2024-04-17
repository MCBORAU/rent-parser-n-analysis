import json
import os
import time
import requests
import random
from bs4 import BeautifulSoup
from datetime import datetime

ad_data_list = []
resource = "flatbook.by"
towns_list = ["Брест", "Витебск", "Гомель", "Гродно", "Минск", "Могилев"]
common_url_list = ["https://brest.flatbook.by/", "https://vitebsk.flatbook.by/",
                   "https://gomel.flatbook.by/", "https://grodno.flatbook.by/",
                   "https://flatbook.by/", "https://mogilev.flatbook.by/"]
headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/122.0.0.0 Mobile Safari/537.36 Edg/122.0.0.0"
}


def get_amount_of_pages(url):
    first_page = requests.get(url, headers=headers)
    soup = BeautifulSoup(first_page.text, "lxml")
    amount_raw = soup.find("span", class_="highlight").text
    amount = int(amount_raw)
    return amount


def get_data(url, region):
    item = 1
    max_counter = get_amount_of_pages(common_url_list[region]) // 24 + 1

    for item_counter in range(1, max_counter + 1):
        all_ads = requests.get(url + f"page-{item}/", headers=headers)

        folder_name = f"flatbook_by/items/region_{region + 1}"

        if not os.path.exists(folder_name):
            os.mkdir(folder_name)

        folder_name = f"flatbook_by/items/region_{region + 1}/item_{item_counter}"

        if not os.path.exists(folder_name):
            os.mkdir(folder_name)

        pattern_file_name = f"{folder_name}/pattern_{item_counter}.html"

        with open(pattern_file_name, "w", encoding="utf-8") as file:
            file.write(all_ads.text)

        with open(pattern_file_name, "r", encoding="utf-8") as file:
            source = file.read()

        soup = BeautifulSoup(source, "lxml")

        ads = soup.find("div", class_="new-flat-grid").find_all("div",
                                                                class_="flat-item")

        ad_urls = []
        for ad in ads:
            ad_url = common_url_list[region][:-1] + ad.find("div", class_="flat-item-line new-flat-margin-top-5 "
                                                                          "new-flat-margin-left-5 "
                                                                          "new-flat-margin-right-5 "
                                                                          "new-flat-margin-bottom-5").find_all(
                "a")[1].get("href")
            ad_urls.append(ad_url)

        for ad_url in ad_urls:
            request = requests.get(ad_url, headers=headers)
            page_id = ad_url.split('/')[-2]
            to_delete = ["*"]
            page_id = "".join([i for i in page_id if i not in to_delete])
            file_name = f"{folder_name}/{page_id}.html"

            with open(file_name, "w", encoding="utf-8") as file:
                file.write(request.text)

            with open(file_name, "r", encoding="utf-8") as file:
                ad = file.read()

            soup = BeautifulSoup(ad, "lxml")

            try:
                address_raw = soup.find("div", class_="span6 info pull-right").find("h1")
                address_text = address_raw.text
                address_parts = address_text.split(",")
                street_n_building = address_parts[-3:-1]
                address = f"{towns_list[region]}, " + ",".join(street_n_building).strip()
            except Exception:
                address = "NULL"

            try:
                price_raw = soup.find("span", class_="label blue")
                price = "".join([str(item) for item in price_raw.contents if isinstance(item, str)]).strip()
                price = int(price) * 100
            except Exception:
                price = -1
            if price == -1:
                try:
                    price_raw = soup.find("span", class_="label green")
                    price = "".join([str(item) for item in price_raw.contents if isinstance(item, str)]).strip()
                    price = int(price) * 100
                except Exception:
                    price = -1
            if price == -1:
                try:
                    price_raw = soup.find("span", class_="label orange")
                    price = "".join([str(item) for item in price_raw.contents if isinstance(item, str)]).strip()
                    price = int(price) * 100
                except Exception:
                    price = -1

            try:
                phone_number = soup.find("div", class_="phones-flex").text
                to_delete = ["+", "-", " ", "(", ")"]
                phone_number = "".join([i for i in phone_number if i not in to_delete]).strip()
            except Exception:
                phone_number = "NULL"

            try:
                author_name_raw = soup.find("ul", class_="breadcrumb").find_all("li")[1].find("a").text
                author_name = " ".join(author_name_raw.split()).strip()
            except Exception:
                author_name = "NULL"

            current_date = datetime.now()
            formatted_date = current_date.strftime('%d.%m.%Y')

            date = "NULL"

            try:
                address_raw = soup.find("div", class_="span6 info pull-right").find("h1")
                address_text = address_raw.text
                address_parts = address_text.split(",")
                floor_raw = address_parts[-1]
                floor_parts = floor_raw.split()
                floor = floor_parts[0]
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

        item += 1
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

    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    for region in range(len(towns_list)):
        get_data(common_url_list[region], region)
    create_json_file()
