# needle_final_results_live.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import requests
from bs4 import BeautifulSoup
import random

# ------------ SETTINGS ------------
MAJORITY_THRESHOLD = 172
EXPECTED_PARTIES = ['LPC', 'CPC', 'NDP', 'BQ', 'GPC', 'PPC', 'Other']

# 338Canada baseline as of April 28, 2025
BASELINE_338 = {
    "LPC": 186,
    "CPC": 124,
    "BQ": 23,
    "NDP": 9,
    "GPC": 1,
    "PPC": 0,
    "Other": 0
}

party_colors = {
    'LPC': '#EF3B2C',
    'CPC': '#1C3F94',
    'NDP': '#F5841F',
    'BQ': '#49A2D6',
    'GPC': '#3D9B35',
    'PPC': '#6F259C',
    'Other': '#888888'
}

# ------------ STREAMLIT SETUP ------------
st.set_page_config(page_title="Canadian Election LIVE Needle", layout="centered")

st.title("🇨🇦 Canadian Federal Election 2025")
st.caption("LIVE Real-time predictions")

# ------------ SCRAPE LIVE DATA ------------
@st.cache_data(ttl=30)
def scrape_live_seats():
    url = "https://enr.elections.ca/National.aspx?lang=e"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        st.error(f"Failed to fetch Elections Canada page (Status {response.status_code})")
        st.stop()

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id': 'grdNationalDataBlock'})
    if not table:
        st.error("Could not find National Data Block table.")
        st.stop()

    rows = table.find_all('tr')
    if len(rows) < 2:
        st.error("National Data Block table doesn't have expected rows.")
        st.stop()

    leading_row = rows[1]
    cells = leading_row.find_all('td')
    if len(cells) < 6:
        st.error("Not enough cells in leading row.")
        st.stop()

    seat_data = {
        "CPC": int(cells[1].text.strip()),
        "GPC": int(cells[2].text.strip()),
        "LPC": int(cells[3].text.strip()),
        "NDP": int(cells[4].text.strip()),
        "Other": int(cells[5].text.strip())
    }
    return seat_data

# ------------ BLEND LIVE DATA WITH BASELINE ------------
def predict_final_seats(live_data, baseline_data):
    total_baseline_seats = sum(baseline_data.values())
    total_reported = sum(live_data.values())

    if total_reported == 0:
        return baseline_data.copy()

    prediction = {}
    for party in EXPECTED_PARTIES:
        live_seats = live_data.get(party, 0)
        base_seats = baseline_data.get(party, 0)
        weight_live = min(total_reported / 338.0, 1.0)
        predicted = (live_seats / max(total_reported, 1)) * 338 * weight_live + base_seats * (1 - weight_live)
        prediction[party] = int(round(predicted))
    return prediction

# ------------ LOAD DATA ------------
live_seat_data = scrape_live_seats()

# ------------ SIMULATE RANDOM IF NEEDED ------------
if sum(live_seat_data.values()) == 0:
    st.warning("⚠️ No live seats yet. Simulating test data...")
    live_seat_data = {
        "CPC": random.randint(10, 50),
        "GPC": random.randint(0, 3),
        "LPC": random.randint(15, 60),
        "NDP": random.randint(5, 20),
        "Other": random.randint(0, 5)
    }

predicted_seat_data = predict_final_seats(live_seat_data, BASELINE_338)

# ------------ CALCULATE OUTCOMES ------------
lib_majority = 0
lib_minority = 0
cpc_majority = 0
cpc_minority = 0
ndp_official = 0

for sim in simulations:
    lpc = sim['LPC']
    cpc = sim['CPC']
    ndp = sim['NDP']

    if lpc >= MAJORITY_THRESHOLD:
        lib_majority += 1
    elif lpc > cpc:
        lib_minority += 1

    if cpc >= MAJORITY_THRESHOLD:
        cpc_majority += 1
    elif cpc > lpc:
        cpc_minority += 1

    if ndp >= 12:
        ndp_official += 1

total_sim = len(simulations)

# ------------ 2. PROJECTED WINNER ------------

winner = max(predicted_seat_data.items(), key=lambda x: x[1])[0]
winner_seats = predicted_seat_data[winner]

st.write(f"### 🏆 **Projected Winner**: {winner}")
st.write(f"### 🪧 **Projected Seats**: {winner_seats}")

# ------------ 4. GREEN TEXT BOX ------------
if winner_seats >= MAJORITY_THRESHOLD:
    st.success(f"✅ {winner} projected to win a **Majority Government**!")
else:
    st.success(f"✅ {winner} projected to lead a **Minority Government**.")

# ------------ LIVE NEEDLE ------------

lpc_predicted = predicted_seat_data.get('LPC', 0)
cpc_predicted = predicted_seat_data.get('CPC', 0)

if lpc_predicted >= MAJORITY_THRESHOLD:
    center_pos = 0.125
elif lpc_predicted > cpc_predicted:
    center_pos = 0.375
elif cpc_predicted >= MAJORITY_THRESHOLD:
    center_pos = 0.875
else:
    center_pos = 0.625

slider_position = np.clip(center_pos + np.random.normal(0, 0.005), 0, 1)

fig, ax = plt.subplots(figsize=(12, 2))

# Background bars
ax.barh(0, 1, height=0.2, color='lightgray', edgecolor='black')
ax.barh(0, 0.25, height=0.2, color='#EF3B2C', alpha=0.4)
ax.barh(0, 0.25, left=0.25, height=0.2, color='#EF3B2C', alpha=0.2)
ax.barh(0, 0.25, left=0.5, height=0.2, color='#1C3F94', alpha=0.2)
ax.barh(0, 0.25, left=0.75, height=0.2, color='#1C3F94', alpha=0.4)

# Draw Maple Leaf manually
ax.annotate(
    "🍁",
    xy=(slider_position, 0.05),
    ha='center',
    va='center',
    fontsize=28,
    fontweight='bold',
    color='black'
)

# Labels
ax.text(0.125, -0.3, "Liberal Majority", ha='center', va='center', fontsize=10)
ax.text(0.375, -0.3, "Liberal Minority", ha='center', va='center', fontsize=10)
ax.text(0.625, -0.3, "CPC Minority", ha='center', va='center', fontsize=10)
ax.text(0.875, -0.3, "CPC Majority", ha='center', va='center', fontsize=10)

ax.set_xlim(0, 1)
ax.set_ylim(-0.6, 0.6)
ax.axis('off')

st.pyplot(fig)

# ------------ 5. CHANCES DISPLAY ------------
st.subheader("📊 Outcome Probabilities")

st.write(f"🔴 Liberal Majority: **{lib_majority/total_sim:.1%}**")
st.write(f"🔴 Liberal Minority: **{lib_minority/total_sim:.1%}**")
st.write(f"🔵 CPC Majority: **{cpc_majority/total_sim:.1%}**")
st.write(f"🔵 CPC Minority: **{cpc_minority/total_sim:.1%}**")
st.write(f"🟠 NDP Official Party Status (12+ seats): **{ndp_official/total_sim:.1%}**")

# ------------ 3. PROJECTED SEATS ------------
st.subheader("📈 Projected Seats")

predicted_seat_df = pd.DataFrame.from_dict(predicted_seat_data, orient='index', columns=['Predicted Seats'])
predicted_seat_df = predicted_seat_df.reindex(EXPECTED_PARTIES).fillna(0).astype(int)
predicted_seat_df = predicted_seat_df.sort_values(by='Predicted Seats', ascending=False)

st.table(predicted_seat_df)

# ------------ 5. CURRENT LEADING SEATS ------------
st.subheader("📋 Current Leading Seats")

live_seat_df = pd.DataFrame.from_dict(live_seat_data, orient='index', columns=['Leading Seats'])
live_seat_df = live_seat_df.reindex(EXPECTED_PARTIES).fillna(0).astype(int)
live_seat_df = live_seat_df.sort_values(by='Leading Seats', ascending=False)

st.table(live_seat_df)
