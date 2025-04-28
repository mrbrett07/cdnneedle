import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

st.set_page_config(page_title="Canada Election Needle", layout="centered")

st.title("🌊 Canada Election Live Needle")

# Constants
MAJORITY_THRESHOLD = 170
EXPECTED_PARTIES = ['LPC', 'CPC', 'NDP', 'BQ', 'GPC', 'PPC']
PARTY_FULLNAMES = {
    'LPC': 'Liberal',
    'CPC': 'Conservative',
    'NDP': 'New Democratic Party',
    'BQ': 'Bloc Quebecois',
    'GPC': 'Green Party',
    'PPC': "People's Party"
}

# Baseline projections from 338Canada (April 28, 2025)
BASELINE_PROJECTIONS = {
    'LPC': 110,
    'CPC': 160,
    'NDP': 30,
    'BQ': 30,
    'GPC': 2,
    'PPC': 1
}

@st.cache_data(ttl=30)
def scrape_live_seats():
    url = "https://enr.elections.ca/National.aspx?lang=e"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    table = soup.find("table", {"id": "grdNationalDataBlock"})
    rows = table.find_all("tr")

    live_data = {
        "CPC": 0,
        "LPC": 0,
        "BQ": 0,
        "NDP": 0,
        "GPC": 0,
        "PPC": 0
    }

    for row in rows:
        cells = row.find_all("td")
        if len(cells) >= 2:
            party_name = cells[0].get_text(strip=True)
            if "Conservative" in party_name:
                live_data["CPC"] = int(cells[1].text.strip())
            elif "Liberal" in party_name:
                live_data["LPC"] = int(cells[1].text.strip())
            elif "Bloc" in party_name:
                live_data["BQ"] = int(cells[1].text.strip())
            elif "NDP" in party_name:
                live_data["NDP"] = int(cells[1].text.strip())
            elif "Green" in party_name:
                live_data["GPC"] = int(cells[1].text.strip())
            elif "People's Party" in party_name:
                live_data["PPC"] = int(cells[1].text.strip())
    
    return live_data

def simulate_final_seats(live_data, baseline_data, num_simulations=10000):
    simulations = []
    for _ in range(num_simulations):
        sim = {}
        for party in EXPECTED_PARTIES:
            live = live_data.get(party, 0)
            projected = baseline_data.get(party, 0)
            remaining = max(projected - live, 0)
            simulated_wins = np.random.binomial(remaining, 0.5)
            sim[party] = live + simulated_wins
        simulations.append(sim)
    return simulations

def calculate_probabilities(simulations):
    df = pd.DataFrame(simulations)
    majority_liberal = (df['LPC'] >= MAJORITY_THRESHOLD).mean()
    majority_conservative = (df['CPC'] >= MAJORITY_THRESHOLD).mean()
    minority_liberal = ((df['LPC'] < MAJORITY_THRESHOLD) & (df['LPC'] > df['CPC'])).mean()
    minority_conservative = ((df['CPC'] < MAJORITY_THRESHOLD) & (df['CPC'] > df['LPC'])).mean()
    ndp_official = (df['NDP'] >= 12).mean()
    return majority_liberal, majority_conservative, minority_liberal, minority_conservative, ndp_official

def display_needle(winner, conf_level):
    fig, ax = plt.subplots(figsize=(6, 1))
    ax.barh([0], conf_level, color='red')
    ax.set_xlim(0, 1)
    ax.set_yticks([])
    ax.set_title(f"Projected Winner: {PARTY_FULLNAMES.get(winner, winner)}", fontsize=16)
    st.pyplot(fig)

# Refresh every 30 seconds
st_autorefresh = st.empty()
with st_autorefresh.container():
    time.sleep(30)

live_seat_data = scrape_live_seats()

# Simulations
simulations = simulate_final_seats(live_seat_data, BASELINE_PROJECTIONS)
maj_L, maj_C, min_L, min_C, ndp_status = calculate_probabilities(simulations)

# Current Projected Leader
leader = max(live_seat_data, key=lambda x: live_seat_data[x])
winner_seats = live_seat_data[leader]

# Live Needle
st.subheader("Live Needle")
confidence = max(maj_L, maj_C, min_L, min_C)
display_needle(leader, confidence)

# Projected Winner
st.subheader("Projected Winner")
st.write(f"**{PARTY_FULLNAMES.get(leader, leader)}**")

# Projected Seats
st.subheader("Projected Seats")
final_seats = pd.DataFrame(simulations).mean().round(0).astype(int).to_dict()
st.dataframe(pd.DataFrame(final_seats.items(), columns=["Party", "Projected Seats"]))

# Outcome
st.subheader("Projected Outcome")
if leader == "CPC":
    if winner_seats >= MAJORITY_THRESHOLD:
        outcome = "Projected Conservative Majority"
    else:
        outcome = "Projected Conservative Minority"
elif leader == "LPC":
    if winner_seats >= MAJORITY_THRESHOLD:
        outcome = "Projected Liberal Majority"
    else:
        outcome = "Projected Liberal Minority"
else:
    outcome = "Projected Minority Government"
st.success(outcome)

# Current Leading
st.subheader("Current Leading")
st.write(live_seat_data)

# Predicted Final Seats
st.subheader("Predicted Final Seats")
predicted_seats = pd.DataFrame(simulations).mean().round(0).astype(int)
st.bar_chart(predicted_seats)

# Extra Probabilities
st.subheader("Chances:")
st.write(f"Liberal Majority Chance: {maj_L*100:.1f}%")
st.write(f"Conservative Majority Chance: {maj_C*100:.1f}%")
st.write(f"Liberal Minority Chance: {min_L*100:.1f}%")
st.write(f"Conservative Minority Chance: {min_C*100:.1f}%")
st.write(f"NDP Official Party Status (12+ seats) Chance: {ndp_status*100:.1f}%")
