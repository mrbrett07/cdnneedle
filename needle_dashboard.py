import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

st.set_page_config(page_title="Canada Election Needle", layout="centered")

st.title("🌍 Canada Federal Election Live Tracker")

# Constants
EXPECTED_PARTIES = ['LPC', 'CPC', 'NDP', 'BQ', 'GPC', 'PPC']
MAJORITY_THRESHOLD = 170

# Functions to fetch live seat data
def scrape_live_seats():
    url = "https://enr.elections.ca/National.aspx?lang=e"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", {"id": "grdNationalDataBlock"})

    live_data = {party: 0 for party in EXPECTED_PARTIES}
    rows = table.find_all("tr")[1]
    cells = rows.find_all("td")

    live_data['CPC'] = int(cells[1].text.strip())
    live_data['LPC'] = int(cells[2].text.strip())
    live_data['BQ'] = int(cells[4].text.strip())
    # Approximation: No Green or PPC leads reported separately in this table
    live_data['NDP'] = 0
    live_data['GPC'] = 0
    live_data['PPC'] = 0

    return live_data

@st.cache_data(ttl=30)
def get_live_data():
    return scrape_live_seats()

# Baseline projections (fetched from 338Canada.com manually)
PROJECTED_SEATS = {
    'LPC': 114,
    'CPC': 171,
    'NDP': 32,
    'BQ': 28,
    'GPC': 2,
    'PPC': 1,
}

# Monte Carlo Simulations
def simulate_seats(live_data, n_simulations=10000):
    simulations = []

    for _ in range(n_simulations):
        results = {}
        for party in EXPECTED_PARTIES:
            baseline = PROJECTED_SEATS.get(party, 0)
            live = live_data.get(party, 0)
            remaining = baseline - live

            # Random adjustment with some noise
            final = live + np.random.poisson(remaining)
            results[party] = final

        simulations.append(results)

    return simulations

# Live data
data = get_live_data()

# --- Layout ---

# Needle
st.subheader("Live Needle")

fig, ax = plt.subplots(figsize=(5,2))
ax.axis('off')
needle_position = (data['LPC'] - data['CPC']) / 100  # Rough scaling
ax.annotate('🍀', xy=(0.5 + needle_position, 0.5), fontsize=30, ha='center')
st.pyplot(fig)

# Winner projection
st.subheader("Projected Winner")

simulations = simulate_seats(data)
final_counts = pd.DataFrame(simulations)

winner = final_counts.sum().idxmax()
winner_seats = final_counts.mean().round(1)[winner]

st.metric(label="Projected Winner", value=winner)

# Projected seats
st.subheader("Projected Seats")

avg_seats = final_counts.mean().round(1)
st.dataframe(avg_seats.to_frame(name="Average Projected Seats"))

# Outcome green box
st.subheader("Outcome Prediction")

if winner == "CPC" and winner_seats >= MAJORITY_THRESHOLD:
    outcome = "Projected Conservative Majority"
elif winner == "LPC" and winner_seats >= MAJORITY_THRESHOLD:
    outcome = "Projected Liberal Majority"\elif winner_seats < MAJORITY_THRESHOLD:
    outcome = f"Projected {winner} Minority"

st.success(outcome)

# Current Leading
st.subheader("Current Leading (Live)")
st.dataframe(pd.DataFrame(data, index=["Seats Leading"]))

# Final seats prediction
st.subheader("Predicted Final Seats (Simulation)")
st.dataframe(final_counts.describe().loc[['mean','std']].T)

# Majority and Minority Probabilities
st.subheader("Probability of Outcomes")

lpc_majority = (final_counts['LPC'] >= MAJORITY_THRESHOLD).mean()*100
cpc_majority = (final_counts['CPC'] >= MAJORITY_THRESHOLD).mean()*100
lpc_minority = ((final_counts['LPC'] < MAJORITY_THRESHOLD) & (final_counts['LPC'] > final_counts['CPC'])).mean()*100
cpc_minority = ((final_counts['CPC'] < MAJORITY_THRESHOLD) & (final_counts['CPC'] > final_counts['LPC'])).mean()*100
ndp_official = (final_counts['NDP'] >= 12).mean()*100

st.write(f"**Chance of Liberal Majority:** {lpc_majority:.1f}%")
st.write(f"**Chance of Conservative Majority:** {cpc_majority:.1f}%")
st.write(f"**Chance of Liberal Minority:** {lpc_minority:.1f}%")
st.write(f"**Chance of Conservative Minority:** {cpc_minority:.1f}%")
st.write(f"**Chance NDP gets Official Party Status (12+ seats):** {ndp_official:.1f}%")

# Auto-refresh page every 30 seconds
st.experimental_rerun() if int(time.time()) % 30 == 0 else None
