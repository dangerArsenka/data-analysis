# Importing all the necessary libraries
import pandas as pd
pd.plotting.register_matplotlib_converters()
import matplotlib.pyplot as plt
import seaborn as sns
from spyre import server
import os
# Setup complete

def data_cleaning(dir_path):
    # List to store DataFrames from individual CSV files
    all_dfs = []

    if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
        print(f"Directory {dir_path} does not exist or is not a directory.")
        return None
    else:
        files = os.listdir(dir_path)

        # Loop through each file in the directory
        for i, file in enumerate(files):
            if file.endswith(".csv"):
                filePath = os.path.join(dir_path, file)
                df = pd.read_csv(filePath, index_col=False, header=1)
                df["ID"] = i + 1
                all_dfs.append(df)

        df = pd.concat(all_dfs).drop_duplicates().reset_index(drop=True)

    # Made some operations dedicated to Data Cleaning 
    df.columns = [col.replace(" ", "").replace("<br>", "") for col in df.columns]
    df["year"] = df["year"].str.replace(r'<tt>|<pre>', '', regex=True)
    df = df.drop(df.loc[df['VHI'] == -1].index)
    df = df.loc[(df['ID'] != 12) & (df['ID'] != 20)]
    df = df.drop(60398)
    return df

# Replacing regions' indexes
def ID_replace(df):
    index_mapping = {
        1: 22,
        2: 24,
        3: 23,
        4: 25,
        5: 3,
        6: 4,
        7: 8,
        8: 19,
        9: 20,
        10: 21,
        11: 9,
        13: 10,
        14: 11,
        15: 12,
        16: 13,
        17: 14,
        18: 15,
        19: 16,
        21: 17,
        22: 18,
        23: 6,
        24: 1,
        25: 2,
        26: 7,
        27: 5,
    }
    df['ID'] = df['ID'].replace(index_mapping)
    return df

region_id_name = {
    1: 'Вінницька', 2: 'Волинська', 3: 'Дніпропетровська', 4: 'Донецька', 5: 'Житомирська',
    6: 'Закарпатська', 7: 'Запорізька', 8: 'Івано-Франківська', 9: 'Київська', 10: 'Кіровоградська',
    11: 'Луганська', 12: 'Львівська', 13: 'Миколаївська', 14: 'Одеська', 15: 'Полтавська',
    16: 'Рівенська', 17: 'Сумська', 18: 'Тернопільська', 19: 'Харківська', 20: 'Херсонська',
    21: 'Хмельницька', 22: 'Черкаська', 23: 'Чернівецька', 24: 'Чернігівська', 25: 'Республіка Крим'
}

# Клас додатку
class DataAnalysisApp(server.App):
    title = "LAB 3 by arsenka"

    inputs = [
        {
            "type": 'dropdown',
            "label": 'Часовий ряд',
            "options": [
                {"label": "VCI", "value": "VCI"},
                {"label": "TCI", "value": "TCI"},
                {"label": "VHI", "value": "VHI"}
            ],
            "key": 'index',
            "action_id": "update_data"
        },
        {
            "type": 'dropdown',
            "label": 'Область',
            "options": [
                {"label": region_id_name[i], "value": i} for i in range(1, 26)
            ],
            "key": 'region',
            "action_id": "update_data"
        },
        {
            "type": 'text',
            "label": 'Інтервал тижнів',
            "value": 10,
            "key": 'week_interval',
            "action_id": "update_data"
        },
        {
            "type": 'text',
            "label": 'Дата (рррр-рррр)',
            "value": '2000-2021',
            "key": 'date_range',
            "action_id": "update_data"
        }
    ]

    controls = [{"type": "button", "label": "Оновити", "id": "update_data"}]

    tabs = ["Таблиця", "Графік"]

    outputs = [
        {"type": "table", "id": "table", "control_id": "update_data", "tab": "Таблиця"},
        {"type": "plot", "id": "plot", "control_id": "update_data", "tab": "Графік"}
    ]

    def getData(self, params):
        # Extracting parameters
        index = params['index']
        region = int(params['region'])
        week_interval = int(params['week_interval'])
        date_range = params['date_range'].split('-')

        # Used my functions to clean data and to change ID
        cleaned_data = data_cleaning("data")
        replaced_data = ID_replace(cleaned_data)

        # The values of the columns, which are displayed in the table in the order of the selected index
        if index == 'VCI':
            display_columns = ['year', 'week', 'VCI']
        elif index == 'TCI':
            display_columns = ['year', 'week', 'TCI']
        else:
            display_columns = ['year', 'week', 'VHI']

        # Filtering
        filtered_data = replaced_data[(replaced_data['ID'] == region) & 
                                      (replaced_data['year'].between(date_range[0], date_range[1])) &
                                      (replaced_data['week'] <= week_interval)]
        
        # Selecting as many items as needed
        filtered_data = filtered_data[display_columns]

        return filtered_data

    def getPlot(self, params):
        # Extracting parameters
        index = params['index']
        region = int(params['region'])
        week_interval = int(params['week_interval'])
        date_range = params['date_range'].split('-')

        # Used previous function
        filtered_data = self.getData(params)

        # Filtering
        filtered_data = filtered_data[(filtered_data['year'].between(date_range[0], date_range[1])) &
                                    (filtered_data['week'] <= week_interval)]

        # Creating a graphic
        plt.figure(figsize=(10, 6))
        for year in filtered_data['year'].unique():
            data_year = filtered_data[filtered_data['year'] == year]
            plt.plot(data_year['week'], data_year[index], marker='o', linestyle='-', label=year)
        plt.title(f'Графік {index} для області {region_id_name[region]}')
        plt.xlabel('Тиждень')
        plt.ylabel('Значення')
        plt.grid(True)
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)
        
        # Graphic object
        plot = plt.gcf()

        return plot

app = DataAnalysisApp()
app.launch()