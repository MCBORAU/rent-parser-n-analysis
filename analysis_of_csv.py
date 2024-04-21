import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

general_data = []

file_path = "data_csv/ad_data_csv.json"

with open(file_path, "r", encoding="utf-8") as file:
    try:
        data = json.load(file)
        general_data.extend(data)
    except json.JSONDecodeError as e:
        print(f"Ошибка при загрузке данных: {e}")

df = pd.DataFrame(general_data)

sns.set(style="whitegrid")
palette = sns.color_palette("pastel")


def assign_colors_to_values(y_values):
    my_palette = ['#bcebcb', '#e08b8b', '#9bdbe8', '#df90c4', '#aec8cf', '#ffefd6', '#c8bcd4', '#abc4ff', '#f1f4f9',
                  '#fdffb6', '#f3d7f0', '#ece4d0', '#b7c7e1', '#d9c9d4', '#dfd49c', '#d1d1d1', '#cad3fa', '#f5ee98',
                  '#ace5ee', '#f7e4f7']

    interval = 25

    max_value = max(y_values)

    interval_min_limit = [i * interval + 1 for i in range(int(max_value // interval + 1))]

    assigned_colors = [my_palette[limit_index] for val in y_values for limit_index, limit in
                       enumerate(interval_min_limit) if (val > limit and val - limit < interval)]

    return assigned_colors


def assign_colors_to_unique_values(y_values):
    my_palette = ['#bcebcb', '#e08b8b', '#9bdbe8', '#df90c4', '#aec8cf', '#abc4ff', '#c8bcd4', '#ffefd6', '#f1f4f9',
                  '#fdffb6', '#f3d7f0', '#ece4d0', '#b7c7e1', '#d9c9d4', '#dfd49c', '#d1d1d1', '#cad3fa', '#f5ee98',
                  '#ace5ee', '#f7e4f7']

    unique_values = sorted(set(y_values))
    colors = sns.color_palette(my_palette, len(unique_values))
    color_dict = dict(zip(unique_values, colors))
    return [color_dict[val] for val in y_values]


def week_ad_amount_barplot(df):
    palette = sns.color_palette("pastel", 7)

    df = df[df["Date"] != "NULL"]
    df["Date"] = pd.to_datetime(df["Date"], errors='coerce', dayfirst=True)
    df['Day_of_Week'] = df['Date'].dt.day_name()

    day_names_ru = {
        'Monday': 'Понедельник',
        'Tuesday': 'Вторник',
        'Wednesday': 'Среда',
        'Thursday': 'Четверг',
        'Friday': 'Пятница',
        'Saturday': 'Суббота',
        'Sunday': 'Воскресенье'
    }

    df['Day_of_Week'] = df['Day_of_Week'].map(day_names_ru)

    order = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']

    plt.figure(figsize=(10, 6))

    sns.countplot(y='Day_of_Week', data=df, hue='Day_of_Week', order=order, palette=palette)

    plt.xlabel("Количество объявлений", fontsize=12)
    plt.ylabel("День недели", fontsize=12)
    plt.title("Количество объявлений по дням недели", fontsize=14)

    plt.savefig('plots_csv/week_ad_amount_barplot.png', dpi=300, bbox_inches='tight')
    plt.close()


def one_phone_authors(df):
    df = df[df["Phone"] != "NULL"]

    phone_author_counts = df.groupby("Phone")["Author"].nunique()

    phones_with_multiple_authors = phone_author_counts[phone_author_counts > 2]

    sorted_unique_author_counts = phones_with_multiple_authors.sort_values(ascending=False)

    colors = assign_colors_to_unique_values(sorted_unique_author_counts.values)

    plt.figure(figsize=(10, 6))

    plt.bar(sorted_unique_author_counts.index, sorted_unique_author_counts.values, color=colors)

    plt.xlabel("Телефоны", fontsize=12)
    plt.ylabel("Количество уникальных авторов", fontsize=12)
    plt.title("Телефоны с разными именами авторов в объявлениях", fontsize=14)

    plt.xticks([])
    plt.tight_layout()

    plt.savefig('plots_csv/one_phone_authors.png', dpi=300, bbox_inches='tight')
    plt.close()


def one_phone_ads(df):
    df = df[df["Phone"] != "NULL"]

    phone_author_counts = df.groupby("Phone")["Author"].nunique()

    phones_with_multiple_authors = phone_author_counts[phone_author_counts > 2]

    phone_ad_counts = df["Phone"].value_counts()

    phones_with_multiple_ads = phone_ad_counts[phone_ad_counts > 3]

    filtered_phones = phones_with_multiple_ads.index.intersection(phones_with_multiple_authors.index)

    data_for_plot = phone_ad_counts.loc[filtered_phones]

    plt.figure(figsize=(10, 6))

    colors = assign_colors_to_values(data_for_plot.values)

    plt.bar(data_for_plot.index, data_for_plot.values, color=colors)

    plt.xlabel("Телефоны", fontsize=12)
    plt.ylabel("Количество объявлений", fontsize=12)
    plt.title("Телефоны с разными именами авторов в объявлениях", fontsize=14)

    plt.xticks([])
    plt.tight_layout()

    plt.savefig('plots_csv/one_phone_ads.png', dpi=300, bbox_inches='tight')
    plt.close()


def one_phone_many_authors_ads_pie(df):
    my_palette = ['#bcebcb', '#e08b8b', '#9bdbe8', '#df90c4', '#aec8cf', '#ffefd6', '#c8bcd4', '#abc4ff', '#f1f4f9',
                  '#fdffb6', '#f3d7f0', '#ece4d0', '#b7c7e1', '#d9c9d4', '#dfd49c', '#d1d1d1', '#cad3fa', '#f5ee98',
                  '#ace5ee', '#f7e4f7']

    df = df[df["Phone"] != "NULL"]

    phone_author_counts = df.groupby("Phone")["Author"].nunique()

    phones_with_multiple_authors = phone_author_counts[phone_author_counts > 2]

    phone_ad_counts = df["Phone"].value_counts()

    phones_with_multiple_ads = phone_ad_counts[phone_ad_counts > 3]

    filtered_phones = phones_with_multiple_ads.index.intersection(phones_with_multiple_authors.index)

    data_for_plot = phone_ad_counts.loc[filtered_phones]

    plt.figure(figsize=(10, 6))

    data_for_plot.plot.pie(startangle=140, labels=None, colors=my_palette)

    plt.title("Доля каждого номера телефона под разными именами по количеству объявлений", fontsize=14)
    plt.ylabel("")
    plt.axis('equal')

    plt.tight_layout()

    plt.savefig('plots_csv/one_phone_many_authors_ads_pie.png', dpi=300, bbox_inches='tight')
    plt.close()


def one_address_ads_barplot(df):
    df = df[(df["Address"] != "NULL")]

    phone_counts = df.groupby("Address")["Phone"].nunique()

    phone_counts_filtered = phone_counts[phone_counts > 2].sort_values(ascending=False)

    colors = assign_colors_to_unique_values(phone_counts_filtered.values)

    plt.figure(figsize=(10, 6))

    plt.bar(phone_counts_filtered.index, phone_counts_filtered.values, color=colors)

    plt.xlabel("Адрес", fontsize=12)
    plt.ylabel("Количество номеров телефонов", fontsize=12)
    plt.title("Количество объявлений с разными номерами по одному адресу", fontsize=14)

    plt.xticks([])
    plt.yticks(range(int(phone_counts_filtered.max()) + 1))
    plt.tight_layout()

    plt.savefig('plots_csv/one_address_ads_barplot.png', dpi=300, bbox_inches='tight')
    plt.close()


def one_phone_ads_pie(df):
    my_palette = ['#bcebcb', '#e08b8b', '#9bdbe8', '#df90c4', '#aec8cf', '#ffefd6', '#c8bcd4', '#abc4ff', '#f1f4f9',
                  '#fdffb6', '#f3d7f0', '#ece4d0', '#b7c7e1', '#d9c9d4', '#dfd49c', '#d1d1d1', '#cad3fa', '#f5ee98',
                  '#ace5ee', '#f7e4f7']

    df = df[df["Date"] != "NULL"]

    df["Date"] = pd.to_datetime(df["Date"], errors='coerce', dayfirst=True)

    phone_author_counts = df.groupby("Phone")["Author"].nunique()

    phones_with_multiple_authors = phone_author_counts[phone_author_counts > 2]

    phone_ad_counts = df["Phone"].value_counts()

    phones_with_multiple_ads = phone_ad_counts[phone_ad_counts > 3]

    filtered_phones = phones_with_multiple_ads.index.intersection(phones_with_multiple_authors.index)

    data_for_plot = phone_ad_counts.loc[filtered_phones]

    df = df[df["Phone"] != "NULL"]
    phones_to_plot = df[df["Phone"].apply(lambda x: x not in data_for_plot.index and df["Phone"].value_counts()[x] > 15)]

    data_for_plot_new = phones_to_plot["Phone"].value_counts()

    plt.figure(figsize=(10, 6))

    data_for_plot_new.plot.pie(startangle=140, labels=None, colors=my_palette)

    plt.title("Доля каждого номера телефона, используемого только под 1 именем, по количеству объявлений(>15)",
              fontsize=13)

    plt.ylabel("")
    plt.axis('equal')

    plt.tight_layout()

    plt.savefig('plots_csv/one_phone_ads_pie.png', dpi=300, bbox_inches='tight')
    plt.close()


if __name__ == "__main__":
    week_ad_amount_barplot(df)
    one_phone_authors(df)
    one_phone_ads(df)
    one_phone_many_authors_ads_pie(df)
    one_address_ads_barplot(df)
    one_phone_ads_pie(df)
