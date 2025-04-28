import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random

st.set_page_config(layout="wide", page_title="Canada Election Needle 🇨🇦")

# Projected seats baseline from 338Canada (static until updated)
PROJECTED_SEATS = {
    "CPC": 171,
    "LPC": 121,
    "NDP": 28,
    "BQ": 34,
    "GPC": 2,
    "PPC": 1,
    "Other": 1
}

MAJORITY_THRESHOLD = 172

PARTY_NAMES = {
    "CPC": "Conservative",
    "LPC": "Liberal",
    "NDP": "NDP",
    "BQ": "Bloc",
    "GPC": "Green",
    "PPC": "PPC",
    "Other": "Other"
}

@st.cache_data(ttl=30)
def scrape_live_seats():
    url = "https://enr.elections.ca/National.aspx?lang=e"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch Elections Canada page (status {response.status_code})")

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id': 'grdResultsucNationalResult0'})
    if not table:
        raise Exception("Could not find results table on Elections Canada page.")

    live_seat_data = {key: 0 for key in PROJECTED_SEATS.keys()}
    rows = table.find_all('tr')[1:]
    for row in rows:
        cells = row.find_all('td')
        if len(cells) < 2:
            continue

        party_name = cells[0].text.strip()
        try:
            seats_leading = int(cells[1].text.strip())
        except ValueError:
            seats_leading = 0

        if "Conservative" in party_name:
            live_seat_data["CPC"] += seats_leading
        elif "Liberal" in party_name:
            live_seat_data["LPC"] += seats_leading
        elif "NDP" in party_name or "New Democratic" in party_name:
            live_seat_data["NDP"] += seats_leading
        elif "Bloc" in party_name:
            live_seat_data["BQ"] += seats_leading
        elif "Green" in party_name:
            live_seat_data["GPC"] += seats_leading
        elif "People's Party" in party_name or "PPC" in party_name:
            live_seat_data["PPC"] += seats_leading
        elif "Independent" not in party_name and "No Affiliation" not in party_name:
            live_seat_data["Other"] += seats_leading

    return live_seat_data

def simulate_final_seats(live_seats, baseline_proj, sims=10000):
    results = []
    for _ in range(sims):
        simulated = {}
        for party in live_seats.keys():
            live = live_seats[party]
            baseline = baseline_proj[party]
            remaining = max(baseline - live, 0)
            # Add randomness to remaining seats
            simulated_total = live + max(0, int(random.gauss(remaining, remaining * 0.1)))
            simulated[party] = simulated_total
        results.append(simulated)

    df = pd.DataFrame(results)
    return df

# --- LIVE SECTION ---
live_seat_data = scrape_live_seats()

# Live Needle (based on % of seats reporting + current leads)
total_reported = sum(live_seat_data.values())
needle = (total_reported / 338) * 100

# Simulate final seat projections
df_simulation = simulate_final_seats(live_seat_data, PROJECTED_SEATS)

# Calculate win probabilities
lib_majority = (df_simulation['LPC'] >= MAJORITY_THRESHOLD).mean() * 100
con_majority = (df_simulation['CPC'] >= MAJORITY_THRESHOLD).mean() * 100
lib_minority = ((df_simulation['LPC'] < MAJORITY_THRESHOLD) & (df_simulation['LPC'] > df_simulation['CPC'])).mean() * 100
con_minority = ((df_simulation['CPC'] < MAJORITY_THRESHOLD) & (df_simulation['CPC'] > df_simulation['LPC'])).mean() * 100
ndp_official_party = (df_simulation['NDP'] >= 12).mean() * 100

# Projected Final Seats
projected_means = df_simulation.mean().round(0).astype(int)

# Projected Winner
winner_party = projected_means.idxmax()

# --- UI Layout ---

st.title("🇨🇦 Canada Election Live Needle")

col1, col2, col3 = st.columns([2, 2, 2])

with col1:
    st.metric("Live Needle", f"{needle:.1f}% of seats reporting")

with col2:
    st.metric("Projected Winner", PARTY_NAMES.get(winner_party, winner_party))

with col3:
    st.metric("Projected Seats", f"{projected_means[winner_party]} seats")

st.success(f"✅ {PARTY_NAMES.get(winner_party, winner_party)} projected to form {'a majority' if projected_means[winner_party] >= MAJORITY_THRESHOLD else 'a minority'} government.")

st.header("Current Leading (Live Results)")
st.dataframe(pd.DataFrame.from_dict(live_seat_data, orient='index', columns=['Seats Leading']))

st.header("Predicted Final Seat Totals")
st.dataframe(projected_means.rename(index=PARTY_NAMES).to_frame("Projected Seats"))

st.header("Probabilities")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Liberal Majority Chance", f"{lib_majority:.1f}%")
    st.metric("Liberal Minority Chance", f"{lib_minority:.1f}%")
with col2:
    st.metric("Conservative Majority Chance", f"{con_majority:.1f}%")
    st.metric("Conservative Minority Chance", f"{con_minority:.1f}%")
with col3:
    st.metric("NDP Official Party Status", f"{ndp_official_party:.1f}%")

st.caption("Data automatically refreshes every 30 seconds.")
time.sleep(30)
st.experimental_rerun()
