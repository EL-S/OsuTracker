import requests
from bs4 import BeautifulSoup
import json

for i in range(0,14000000):
    try:
        req = requests.get('https://osu.ppy.sh/u/'+str(i), headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"})
        data = req.text
        with open("dlc.html", "w", encoding="utf-8") as file:
            file.write(data)

        soup = BeautifulSoup(data, "lxml")
        data_profile = soup.find("script", attrs={"id": "json-user"}).text.strip()
        json_data = json.loads(data_profile)
        print(json_data['username'],json_data['statistics']['pp'])
    except Exception as e:
        print("No User!")
