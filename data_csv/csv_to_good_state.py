import json
import pandas as pd
from datetime import datetime


file_path = "data.csv"
df = pd.read_csv(file_path, sep=';')


def correct_author_data():
    author_list_corrected = []
    author_data = df["Fio"]
    author_list = list(author_data)

    for author in author_list:
        if author == " " or author == "Нет имени":
            author_new = "NULL"
            author_list_corrected.append(author_new)
        else:
            author_temp = str(author).split()
            author_new = " ".join(author_temp)
            author_list_corrected.append(author_new)

    return author_list_corrected


def correct_phone_data():
    phone_list_corrected = []
    to_delete = ["+", "-", " ", "(", ")", "/", "r", "n"]
    phone_data = df["ContactData"]
    phone_list = list(phone_data)

    for phone in phone_list:
        if phone == "Нет номера":
            phone_new = "NULL"
            phone_list_corrected.append(phone_new)
        else:
            phone_main = phone.split("  ")[0]
            phone_new = "".join([i for i in phone_main if i not in to_delete]).strip()
            phone_list_corrected.append(phone_new)

    return phone_list_corrected


def correct_parse_date_data():
    parse_date_list_corrected = []
    parse_date_data = df["CreatedAtInOurDb"]
    parse_date_list = list(parse_date_data)

    for parse_date in parse_date_list:
        parse_date_datetime = datetime.strptime(parse_date[:10], "%Y-%m-%d")
        parse_date_new = parse_date_datetime.strftime('%d.%m.%Y')
        parse_date_list_corrected.append(parse_date_new)

    return parse_date_list_corrected


def correct_date_data():
    date_list_corrected = []
    date_data = df["CreatedAtFromSite"]
    date_list = list(date_data)

    for date in date_list:
        if date == "0001-01-01 00:00:00.0000000":
            date_new = "NULL"
            date_list_corrected.append(date_new)
        else:
            date_datetime = datetime.strptime(date[:10], "%Y-%m-%d")
            date_new = date_datetime.strftime('%d.%m.%Y')
            date_list_corrected.append(date_new)

    return date_list_corrected


def correct_address_data():
    address_list_corrected = []
    address_data = df["AdvAddress"].fillna("NULL")
    address_list = list(address_data)

    for address in address_list:
        address_new = str(address).replace('\xad', '')
        address_list_corrected.append(address_new)

    return address_list_corrected


def create_datalist():
    ad_data_list = []
    phone_list = correct_phone_data()
    author_list = correct_author_data()
    parse_date_list = correct_parse_date_data()
    date_list = correct_date_data()
    address_list = correct_address_data()

    resource_data = df["AdditionalInformation"]
    resource_list = list(resource_data)

    for i in range(len(address_list)):
        ad_data_list.append(
            {
                "Address": address_list[i],
                "Phone": phone_list[i],
                "Author": author_list[i],
                "Parse date": parse_date_list[i],
                "Date": date_list[i],
                "Resource": resource_list[i]
            }
        )
    create_json_file(ad_data_list)


def create_json_file(ad_data_list):
    with open("C:/Users/Lenovo/PycharmProjects/rent_parser/data_JSON/ad_data_csv.json", "w", encoding="utf-8") as file:
        json.dump(ad_data_list, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    create_datalist()
