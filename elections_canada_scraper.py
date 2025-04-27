# elections_canada_scraper.py

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape_elections_canada():
    url = "https://enr.elections.ca/National.aspx?lang=e"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch page. Status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the table containing national seat counts
    table = soup.find('table', {'id': 'ctl00_ContentPlaceHolder1_grdNational'})

    if table is None:
        print("Couldn't find seat count table!")
        return

    data = []
    rows = table.find_all('tr')

    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 2:
            party_name = cols[0].text.strip()
            seat_count_text = cols[1].text.strip()

            if seat_count_text.isdigit():
                seats = int(seat_count_text)

                # Normalize party names
                if "Liberal" in party_name:
                    party_code = "LPC"
                elif "Conservative" in party_name:
                    party_code = "CPC"
                elif "Bloc" in party_name:
                    party_code = "BQ"
                elif "New Democratic" in party_name:
                    party_code = "NDP"
                elif "Green" in party_name:
                    party_code = "GPC"
                elif "People's" in party_name:
                    party_code = "PPC"
                else:
                    party_code = None

                if party_code:
                    data.append((party_code, seats))

    # Save to CSV
    df = pd.DataFrame(data, columns=["Party", "Projected Seats"])
    df.to_csv("results.csv", index=False)
    print("✅ results.csv updated.")

if __name__ == "__main__":
    while True:
        scrape_elections_canada()
        time.sleep(60)  # Update every 60 seconds
