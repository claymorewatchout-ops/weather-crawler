import os
import requests
import pandas as pd
import matplotlib.pyplot as plt


def get_hko_six_day_forecast():
    url = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=fnd&lang=en"
    csv_file = "weather_forecast.csv"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        print("--- General Situation ---")
        print(data.get("generalSituation", "N/A"))
        print("\n" + "=" * 50 + "\n")

        forecast_list = data.get("weatherForecast", [])

        parsed_data = []
        for day in forecast_list[:6]:
            min_val = float(day.get("forecastMintemp", {}).get("value", 0))
            max_val = float(day.get("forecastMaxtemp", {}).get("value", 0))
            avg_temp = (min_val + max_val) / 2

            parsed_data.append(
                {
                    # 強制確保 Date 抓下來是字串
                    "Date": str(day.get("forecastDate")),
                    "Day": day.get("week"),
                    "Weather": day.get("forecastWeather"),
                    "Min Temp (°C)": f"{day.get('forecastMintemp', {}).get('value')} {day.get('forecastMintemp', {}).get('unit')}",
                    "Max Temp (°C)": f"{day.get('forecastMaxtemp', {}).get('value')} {day.get('forecastMaxtemp', {}).get('unit')}",
                    "Humidity (%)": f"{day.get('forecastMinrh', {}).get('value')} - {day.get('forecastMaxrh', {}).get('value')}",
                    "Avg Temp (°C)": avg_temp,
                }
            )

        df_new = pd.DataFrame(parsed_data)

        if os.path.exists(csv_file):
            # 讀取時加上 dtype={'Date': str}，避免日期被自動轉成整數
            df_old = pd.read_csv(csv_file, dtype={"Date": str})
            df_combined = pd.concat([df_old, df_new], ignore_index=True)
        else:
            df_combined = df_new

        # 確保整個 Date 欄位統一都是字串型態
        df_combined["Date"] = df_combined["Date"].astype(str)

        # 移除重複日期，保留最新的
        df_combined.drop_duplicates(subset=["Date"], keep="last", inplace=True)

        # 排序
        df_combined.sort_values(by="Date", inplace=True)

        # 儲存
        df_combined.to_csv(csv_file, index=False)

        print(f"資料已成功更新並儲存至 {csv_file}")
        display(df_combined)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from HKO API: {e}")


get_hko_six_day_forecast()
