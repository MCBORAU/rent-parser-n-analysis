import os
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

general_data = []

folder_path = "C:/Users/Lenovo/PycharmProjects/rent_parser/data_JSON"

for filename in os.listdir(folder_path):
    if filename.endswith(".json"):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
                general_data.extend(data)
            except json.JSONDecodeError as e:
                print(f"Ошибка при загрузке данных из файла {filename}: {e}")

df = pd.DataFrame(general_data)
df = df[df["Price"] != -1]
df["Price"] = df["Price"] / 100

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
    unique_values = sorted(set(y_values))
    colors = sns.color_palette("pastel", len(unique_values))
    color_dict = dict(zip(unique_values, colors))
    return [color_dict[val] for val in y_values]


def price_histogram():
    median_price = np.median(df["Price"])
    mean_price = np.round(np.mean(df["Price"]))

    plt.figure(figsize=(10, 6))

    sns.histplot(df["Price"], bins=20, color=palette[0], element="step", edgecolor="w", linewidth=0, alpha=1, fill=True)

    plt.axvline(median_price, color='black', linestyle='-', label=f'Медиана: {median_price}')
    plt.text(median_price, 10, '', fontsize=10, ha='center', color='black', weight='bold')

    plt.axvline(mean_price, color='blue', linestyle='-', label=f'Среднее: {mean_price}')
    plt.text(mean_price, -30, '', fontsize=10, ha='center', color='blue', weight='bold')

    plt.xlabel("Цена, рубли", fontsize=12)
    plt.ylabel("Количество предложений", fontsize=12)
    plt.title("Гистограмма стоимости аренды", fontsize=14)

    plt.legend()
    plt.xlim(left=0)

    plt.savefig('plots_parsed/price_histogram.png', dpi=300, bbox_inches='tight')
    plt.close()


def week_price_boxplot(df):
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

    sns.boxplot(y='Day_of_Week', x='Price', data=df, hue='Day_of_Week', dodge=False, saturation=0.75, showfliers=False,
                order=order, linewidth=1, palette=palette, boxprops=dict(edgecolor=None))

    plt.xlabel("Цена, рубли", fontsize=12)
    plt.ylabel("День недели", fontsize=12)
    plt.title("Горизонтальный ящик с усами для стоимости аренды по дням недели", fontsize=14)

    plt.xlim(left=0)
    plt.tight_layout()

    plt.savefig('plots_parsed/week_price_boxplot.png', dpi=300, bbox_inches='tight')
    plt.close()


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

    sns.countplot(y='Day_of_Week', data=df, order=order, palette=palette, hue='Day_of_Week', legend=False)

    plt.xlabel("Количество объявлений", fontsize=12)
    plt.ylabel("День недели", fontsize=12)
    plt.title("Количество объявлений по дням недели", fontsize=14)

    plt.tight_layout()
    plt.savefig('plots_parsed/week_ad_amount_barplot.png', dpi=300, bbox_inches='tight')
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
    plt.savefig('plots_parsed/one_phone_authors.png', dpi=300, bbox_inches='tight')
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
    plt.savefig('plots_parsed/one_phone_ads.png', dpi=300, bbox_inches='tight')
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
    plt.legend(title="Номер телефона", loc="center left", bbox_to_anchor=(0.78, 0.5), labels=data_for_plot.index,
               fontsize=11)

    plt.savefig('plots_parsed/one_phone_many_authors_ads_pie.png', dpi=300, bbox_inches='tight')
    plt.close()


def one_address_ads_barplot(df):
    df = df[(df["Address"] != "NULL") & (df["Floor"] != -1)]
    df["Floor"] = df["Floor"].astype(str)
    df["Unique_Address"] = df["Address"] + ", " + df["Floor"] + " этаж"

    phone_counts = df.groupby("Unique_Address")["Phone"].nunique()

    phone_counts_filtered = phone_counts[phone_counts > 2].head(20)

    plt.figure(figsize=(10, 6))

    phone_counts_filtered.plot(kind='bar', color=palette[6])

    plt.xlabel("Адрес, этаж", fontsize=12)
    plt.ylabel("Количество номеров телефонов", fontsize=12)
    plt.title("Количество объявлений с разными номерами по одному адресу", fontsize=14)

    plt.xticks(rotation=0)
    plt.yticks(range(int(phone_counts_filtered.max()) + 1))
    plt.tight_layout()
    plt.savefig('plots_parsed/one_address_ads_barplot.png', dpi=300, bbox_inches='tight')
    plt.close()


def one_phone_ads_pie(df):
    my_palette = ['#bcebcb', '#e08b8b', '#9bdbe8', '#df90c4', '#aec8cf', '#ffefd6', '#c8bcd4', '#abc4ff', '#f1f4f9',
                  '#fdffb6', '#f3d7f0', '#ece4d0', '#b7c7e1', '#d9c9d4', '#dfd49c', '#d1d1d1', '#cad3fa', '#f5ee98',
                  '#ace5ee', '#f7e4f7']

    df = df[df["Date"] != "NULL"]
    df["Date"] = pd.to_datetime(df["Date"], errors='coerce', dayfirst=True)
    df = df[(df["Address"] != "NULL") & (df["Floor"] != -1)]
    df["Unique_Address"] = df["Address"] + ", этаж " + df["Floor"].astype(str)

    phone_author_counts = df.groupby("Phone")["Author"].nunique()

    phones_with_multiple_authors = phone_author_counts[phone_author_counts > 2]

    phone_ad_counts = df["Phone"].value_counts()

    phones_with_multiple_ads = phone_ad_counts[phone_ad_counts > 3]

    filtered_phones = phones_with_multiple_ads.index.intersection(phones_with_multiple_authors.index)

    data_for_plot = phone_ad_counts.loc[filtered_phones]

    df = df[df["Phone"] != "NULL"]
    phones_to_plot = df[df["Phone"].apply(lambda x: x not in data_for_plot.index and df["Phone"].value_counts()[x] > 15)]

    data_for_plot_new = phones_to_plot["Phone"].value_counts().head(20)

    plt.figure(figsize=(10, 6))

    data_for_plot_new.plot.pie(startangle=140, labels=None, colors=my_palette)

    plt.title("Доля каждого номера телефона, используемого только под 1 именем, по количеству объявлений(>15)",
              fontsize=13)

    plt.ylabel("")
    plt.axis('equal')

    plt.tight_layout()
    plt.legend(title="Номер телефона", loc="center left", bbox_to_anchor=(0.78, 0.5), labels=data_for_plot_new.index,
               fontsize=11)

    plt.savefig('plots_parsed/one_phone_ads_pie.png', dpi=300, bbox_inches='tight')
    plt.close()


def cheap_ads_amount_barplot():
    count_by_resource_top_20_percent = df[df['Price'] <= df['Price'].quantile(0.2)]['Resource'].value_counts()

    count_by_resource = df['Resource'].value_counts()

    data_for_plot = pd.DataFrame({'Общее количество объявлений': count_by_resource,
                                  'Количество объявлений с низкой ценой': count_by_resource_top_20_percent})

    data_for_plot = data_for_plot.sort_values(by='Общее количество объявлений')

    plt.figure(figsize=(10, 6))

    sns.barplot(x='Общее количество объявлений', y=data_for_plot.index, data=data_for_plot,
                color=palette[6], label='Общее количество объявлений')
    sns.barplot(x='Количество объявлений с низкой ценой', y=data_for_plot.index, data=data_for_plot,
                color=palette[3], label='Количество объявлений с низкой ценой')

    plt.xlabel('Количество объявлений', fontsize=12)
    plt.ylabel('Название ресурса', fontsize=12)
    plt.title('   Сравнение общего количества объявлений и количества объявлений с низкой ценой по ресурсам',
              fontsize=14, x=0.41)

    plt.legend()
    plt.tight_layout()

    plt.savefig('plots_parsed/cheap_ads_amount_barplot.png', dpi=300, bbox_inches='tight')
    plt.close()


def cheap_ads_percentage_barplot():
    count_by_resource_top_20_percent = df[df['Price'] <= df['Price'].quantile(0.2)]['Resource'].value_counts()

    count_by_resource = df['Resource'].value_counts()

    data_for_plot = pd.DataFrame({'Все объявления': 1,
                                  'Доля объявлений с низкой ценой': count_by_resource_top_20_percent/count_by_resource})

    data_for_plot = data_for_plot.sort_values(by='Все объявления')

    plt.figure(figsize=(10, 6))

    sns.barplot(x='Все объявления', y=data_for_plot.index, data=data_for_plot,
                color=palette[6], label='Остальные объявления')
    sns.barplot(x='Доля объявлений с низкой ценой', y=data_for_plot.index, data=data_for_plot,
                color=palette[3], label='Объявления с низкой ценой')

    plt.xlabel('Доля объявлений', fontsize=12)
    plt.ylabel('Название ресурса', fontsize=12)
    plt.title('   Сравнение долей дешёвых и обычных объявлений по ресурсам',
              fontsize=14, x=0.41)

    plt.legend()
    plt.tight_layout()

    plt.savefig('plots_parsed/cheap_ads_percentage_barplot.png', dpi=300, bbox_inches='tight')
    plt.close()


def ads_per_day(df):
    df = df[df["Date"] != "NULL"]
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    df = df.infer_objects()

    newest_dates = df['Date'].max()
    start_date = newest_dates - pd.DateOffset(days=8)
    df_last_week = df[(df['Date'] >= start_date) & (df['Date'] <= newest_dates)]

    df_per_day = df_last_week.resample('D', on='Date').size()

    plt.figure(figsize=(10, 6))
    sns.lineplot(x=df_per_day.index.strftime('%d.%m.%Y'), y=df_per_day.values, color='#9bdbe8', linewidth=4)

    plt.xlabel('Дата', fontsize=12)
    plt.ylabel('Количество объявлений', fontsize=12)
    plt.title('Количество объявлений по датам за последнюю неделю', fontsize=14)

    plt.xlim(left=0)

    plt.savefig('plots_parsed/ads_per_day.png', dpi=300, bbox_inches='tight')
    plt.close()


def average_price_per_day(df):
    df = df[df["Date"] != "NULL"]
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)

    max_date = df['Date'].max()
    start_date = max_date - pd.DateOffset(days=8)

    df_last_week = df[(df['Date'] >= start_date) & (df['Date'] <= max_date)]

    df_per_day = df_last_week.groupby(df_last_week['Date'].dt.date)['Price'].mean()

    dates_str = df_per_day.index.astype(str)

    plt.figure(figsize=(10, 6))
    sns.lineplot(x=dates_str, y=df_per_day.values, color='#bcebcb', linewidth=4)

    plt.xlabel('Дата', fontsize=12)
    plt.ylabel('Средняя цена', fontsize=12)
    plt.title('Средняя цена по датам за последнюю неделю', fontsize=14)

    plt.xlim(left=0)

    plt.savefig('plots_parsed/average_price_per_day.png', dpi=300, bbox_inches='tight')
    plt.close()


if __name__ == "__main__":
    price_histogram()
    week_price_boxplot(df)
    week_ad_amount_barplot(df)
    one_phone_authors(df)
    one_phone_ads(df)
    one_phone_many_authors_ads_pie(df)
    one_address_ads_barplot(df)
    one_phone_ads_pie(df)
    cheap_ads_amount_barplot()
    cheap_ads_percentage_barplot()
    ads_per_day(df)
    average_price_per_day(df)
