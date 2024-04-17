import json
import os
import time
import requests
import random
from bs4 import BeautifulSoup
from datetime import datetime

ad_data_list = []
resource = "gohome.by"
basic_url = "https://gohome.by/"
towns_list = ["Брест", "Витебск", "Гомель", "Гродно", "Минск", "Могилев"]
common_url = "https://gohome.by/rent/search/"
additional_url_list = ["?search%5Btype%5D=5&search%5Bmap_latitude%5D=&search%5Bmap_longitude%5D=&search%5Bmap_zoom%5D"
                       "=0&search%5Bregion%5D=2&search%5Barea%5D=0&search%5Bmax_persons%5D=&search%5Bcost_person_from"
                       "%5D=&search%5Bcost_person_to%5D=&search%5Bcost_from%5D=&search%5Bcost_to%5D=",
                       "?search%5Btype%5D=5&search%5Bmap_latitude%5D=&search%5Bmap_longitude%5D=&search%5Bmap_zoom%5D"
                       "=0&search%5Bregion%5D=3&search%5Barea%5D=0&search%5Bmax_persons%5D=&search%5Bcost_person_from"
                       "%5D=&search%5Bcost_person_to%5D=&search%5Bcost_from%5D=&search%5Bcost_to%5D=",
                       "?search%5Btype%5D=5&search%5Bmap_latitude%5D=&search%5Bmap_longitude%5D=&search%5Bmap_zoom%5D"
                       "=0&search%5Bregion%5D=4&search%5Barea%5D=0&search%5Bmax_persons%5D=&search%5Bcost_person_from"
                       "%5D=&search%5Bcost_person_to%5D=&search%5Bcost_from%5D=&search%5Bcost_to%5D=",
                       "?search%5Btype%5D=5&search%5Bmap_latitude%5D=&search%5Bmap_longitude%5D=&search%5Bmap_zoom%5D"
                       "=0&search%5Bregion%5D=5&search%5Barea%5D=0&search%5Bmax_persons%5D=&search%5Bcost_person_from"
                       "%5D=&search%5Bcost_person_to%5D=&search%5Bcost_from%5D=&search%5Bcost_to%5D=",
                       "?search%5Btype%5D=5&search%5Bmap_latitude%5D=&search%5Bmap_longitude%5D=&search%5Bmap_zoom%5D"
                       "=0&search%5Bregion%5D=1&search%5Barea%5D=0&search%5Bmax_persons%5D=&search%5Bcost_person_from"
                       "%5D=&search%5Bcost_person_to%5D=&search%5Bcost_from%5D=&search%5Bcost_to%5D=",
                       "?search%5Btype%5D=5&search%5Bmap_latitude%5D=&search%5Bmap_longitude%5D=&search%5Bmap_zoom%5D"
                       "=0&search%5Bregion%5D=6&search%5Barea%5D=0&search%5Bmax_persons%5D=&search%5Bcost_person_from"
                       "%5D=&search%5Bcost_person_to%5D=&search%5Bcost_from%5D=&search%5Bcost_to%5D="]
headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/122.0.0.0 Mobile Safari/537.36 Edg/122.0.0.0"
        }


def get_amount_of_pages(url):
    first_page = requests.get(url, headers=headers)
    soup = BeautifulSoup(first_page.text, "lxml")
    amount_raw = soup.find("div", class_="s-name upper _h3").text
    amount = int(amount_raw.split()[-1])
    return amount


def get_data(url, region):
    item = 0
    max_counter = get_amount_of_pages(common_url+additional_url_list[region]) // 30 + 1

    for item_counter in range(1, max_counter + 1):
        all_ads = requests.get(url + f"{item}" + additional_url_list[region], headers=headers)

        folder_name = f"gohome_by/items/region_{region+1}"

        if not os.path.exists(folder_name):
            os.mkdir(folder_name)

        folder_name = f"gohome_by/items/region_{region+1}/item_{item_counter}"

        if not os.path.exists(folder_name):
            os.mkdir(folder_name)

        pattern_file_name = f"{folder_name}/pattern_{item_counter}.html"

        with open(pattern_file_name, "w", encoding="utf-8") as file:
            file.write(all_ads.text)

        with open(pattern_file_name, "r", encoding="utf-8") as file:
            source = file.read()

        soup = BeautifulSoup(source, "lxml")

        ads = soup.find_all("div", class_="w-object-list-item w-corner-sticker color003")
        ads.extend(soup.find_all("div", class_="w-object-list-item color002"))
        ads.extend(soup.find_all("div", class_="w-object-list-item color001"))

        ad_urls = []
        for ad in ads:
            ad_url = basic_url + ad.find("a", class_="name__link").get("href")
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
                address_raw = soup.find("div", class_="left-side").find("h1")
                address_text = address_raw.text
                address_parts = address_text.split(",")
                street_n_building = address_parts[-3:]
                if "Снять" in street_n_building[0]:
                    del street_n_building[0]
                if street_n_building[0] == ' ':
                    del street_n_building[0]
                address = ",".join(street_n_building).strip()
            except Exception:
                address = "NULL"

            try:
                price = soup.find("div", class_="price big").find("span").text
                to_delete = [" "]
                price = "".join([i for i in price if i not in to_delete])
                price = int(price) * 100
            except Exception:
                price = -1

            try:
                phone_number = soup.find("a", class_="phone__link").text
                to_delete = ["+", "-", " ", "(", ")"]
                phone_number = "".join([i for i in phone_number if i not in to_delete]).strip()
            except Exception:
                phone_number = "NULL"

            try:
                author_name_raw = soup.find("div", class_="username").find("div", class_="bold").text
                author_name = " ".join(author_name_raw.split())
            except Exception:
                author_name = "NULL"

            current_date = datetime.now()
            formatted_date = current_date.strftime('%d.%m.%Y')

            try:
                date = soup.find("ul", class_="ul-features").find_all("div", class_="description")[-1].text
            except Exception:
                date = "NULL"

            try:
                floor = soup.find_all("ul", class_="ul-features")[2].find_all("div", class_="description")[2:4]
                if "из" in floor[1].text:
                    floor = floor[1].text.split()[0]
                else:
                    floor = floor[0].text.split()[0]
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

        item += 30
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
        get_data(common_url+additional_url_list[region], region)
    create_json_file()
