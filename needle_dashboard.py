# needle_final_results_live.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import requests
from bs4 import BeautifulSoup

# ------------ SETTINGS ------------
MAJORITY_THRESHOLD = 172  # Updated for 2025 election
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
st.caption("LIVE Needle — Real-time prediction based on Elections Canada + 338Canada baseline")

# ------------ SCRAPE LIVE DATA ------------
@st.cache_data(ttl=30)  # Refresh every 30 seconds
def scrape_live_seats():
    url = "https://enr.elections.ca/National.aspx?lang=e"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
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

    # Cells[1] = CPC, [2] = GPC, [3] = LPC, [4] = NDP, [5] = Other
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
        return baseline_data.copy()  # No results yet, fallback to 338

    prediction = {}
    for party in EXPECTED_PARTIES:
        live_seats = live_data.get(party, 0)
        base_seats = baseline_data.get(party, 0)
        
        # Blend: weight live results more as more seats report
        weight_live = min(total_reported / 338.0, 1.0)  # Scale 0 to 1
        predicted = (live_seats / max(total_reported, 1)) * 338 * weight_live + base_seats * (1 - weight_live)
        prediction[party] = int(round(predicted))

    return prediction

# ------------ LOAD DATA ------------
live_seat_data = scrape_live_seats()
predicted_seat_data = predict_final_seats(live_seat_data, BASELINE_338)

# ------------ DISPLAY CURRENT LIVE LEADING SEATS ------------
st.subheader("📋 Current Leading Seats")

live_seat_df = pd.DataFrame.from_dict(live_seat_data, orient='index', columns=['Leading Seats'])
live_seat_df = live_seat_df.reindex(EXPECTED_PARTIES).fillna(0).astype(int)
live_seat_df = live_seat_df.sort_values(by='Leading Seats', ascending=False)

st.table(live_seat_df)

# ------------ DISPLAY PREDICTED FINAL SEATS ------------
st.subheader("📈 Predicted Final Seats (Live Adjusted)")

predicted_seat_df = pd.DataFrame.from_dict(predicted_seat_data, orient='index', columns=['Predicted Seats'])
predicted_seat_df = predicted_seat_df.reindex(EXPECTED_PARTIES).fillna(0).astype(int)
predicted_seat_df = predicted_seat_df.sort_values(by='Predicted Seats', ascending=False)

st.table(predicted_seat_df)

# ------------ MAPLE LEAF SLIDING SCALE BASED ON PREDICTIONS ------------
st.subheader("🍁 Live Election Needle (Based on Predicted Results)")

lpc_predicted = predicted_seat_data.get('LPC', 0)
cpc_predicted = predicted_seat_data.get('CPC', 0)

if lpc_predicted >= MAJORITY_THRESHOLD:
    slider_base = 0.125  # Liberal Majority
elif lpc_predicted > cpc_predicted:
    slider_base = 0.375  # Liberal Minority
elif cpc_predicted >= MAJORITY_THRESHOLD:
    slider_base = 0.875  # CPC Majority
else:
    slider_base = 0.625  # CPC Minority

slider_position = np.clip(slider_base + np.random.normal(0, 0.01), 0, 1)

fig, ax = plt.subplots(figsize=(12, 2))

ax.barh(0, 1, height=0.2, color='lightgray', edgecolor='black')
ax.barh(0, 0.25, height=0.2, color='#EF3B2C', alpha=0.4)         # Liberal Majority
ax.barh(0, 0.25, left=0.25, height=0.2, color='#EF3B2C', alpha=0.2)  # Liberal Minority
ax.barh(0, 0.25, left=0.5, height=0.2, color='#1C3F94', alpha=0.2)  # CPC Minority
ax.barh(0, 0.25, left=0.75, height=0.2, color='#1C3F94', alpha=0.4) # CPC Majority

ax.text(slider_position, 0.05, "🍁", ha='center', va='center', fontsize=28)

ax.text(0.125, -0.3, "Liberal Majority", ha='center', va='center', fontsize=10)
ax.text(0.375, -0.3, "Liberal Minority", ha='center', va='center', fontsize=10)
ax.text(0.625, -0.3, "CPC Minority", ha='center', va='center', fontsize=10)
ax.text(0.875, -0.3, "CPC Majority", ha='center', va='center', fontsize=10)

ax.set_xlim(0, 1)
ax.set_ylim(-0.6, 0.6)
ax.axis('off')

st.pyplot(fig)

# ------------ WINNER / MAJORITY CALL BASED ON PREDICTIONS ------------
st.subheader("🎯 Live Majority / Minority Status (Predicted)")

winner = max(predicted_seat_data.items(), key=lambda x: x[1])[0]
winner_seats = predicted_seat_data[winner]

st.write(f"### 🏆 **Projected Winner**: {winner}")
st.write(f"### 🪧 **Projected Seats**: {winner_seats}")

if winner_seats >= MAJORITY_THRESHOLD:
    st.success(f"✅ {winner} projected to win a **Majority Government**!")
else:
    st.warning(f"⚠️ {winner} projected to lead a **Minority Government**.")
