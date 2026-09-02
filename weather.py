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
            df_old = pd.read_csv(csv_file, dtype={"Date": str})
            df_combined = pd.concat([df_old, df_new], ignore_index=True)
        else:
            df_combined = df_new

        df_combined["Date"] = df_combined["Date"].astype(str)
        df_combined.drop_duplicates(subset=["Date"], keep="last", inplace=True)
        df_combined.sort_values(by="Date", inplace=True)
        df_combined.to_csv(csv_file, index=False)

        print(f"資料已成功更新並儲存至 {csv_file}")
        # 在純 Python 腳本中用 print 取代 display，避免報錯
        print(df_combined.head())

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from HKO API: {e}")


get_hko_six_day_forecast()
