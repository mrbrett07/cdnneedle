# needle_final_results_live.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import requests
from bs4 import BeautifulSoup

# ------------ SETTINGS ------------
MAJORITY_THRESHOLD = 170
EXPECTED_PARTIES = ['LPC', 'CPC', 'BQ', 'NDP', 'GPC', 'PPC']

party_colors = {
    'LPC': '#EF3B2C',
    'CPC': '#1C3F94',
    'NDP': '#F5841F',
    'BQ': '#49A2D6',
    'GPC': '#3D9B35',
    'PPC': '#6F259C'
}

# ------------ STREAMLIT SETUP ------------
st.set_page_config(page_title="Canadian Election LIVE Needle", layout="centered")

st.title("🇨🇦 Canadian Federal Election 2025")
st.caption("LIVE from Elections Canada")

# ------------ SCRAPE LIVE DATA ------------
@st.cache_data(ttl=30)
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

    table = soup.find('table', {'id': 'ctl00_ContentPlaceHolder1_grdNational'})

    if table is None:
        st.error("Could not find national seat counts table.")
        st.stop()

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

    seat_data = dict(data)
    return seat_data

# Load seat counts
seat_data = scrape_live_seats()

# ------------ FINAL NUMBERS DISPLAY ------------
st.subheader("📋 Current Projected Seat Totals")

seat_df = pd.DataFrame.from_dict(seat_data, orient='index', columns=['Projected Seats'])
seat_df = seat_df.reindex(EXPECTED_PARTIES).fillna(0).astype(int)
seat_df = seat_df.sort_values(by='Projected Seats', ascending=False)

st.table(seat_df)

# ------------ MAPLE LEAF SLIDING SCALE (SMART VERSION) ------------
st.subheader("🍁 Live Election Needle")

# Get main party seat projections
lpc_seats = seat_data.get('LPC', 0)
cpc_seats = seat_data.get('CPC', 0)

# Map correctly:
if lpc_seats >= MAJORITY_THRESHOLD:
    slider_base = 0.125  # Liberal Majority
elif lpc_seats > cpc_seats:
    slider_base = 0.375  # Liberal Minority
elif cpc_seats >= MAJORITY_THRESHOLD:
    slider_base = 0.875  # CPC Majority
else:
    slider_base = 0.625  # CPC Minority

# Add slight jitter
slider_position = np.clip(slider_base + np.random.normal(0, 0.01), 0, 1)

fig, ax = plt.subplots(figsize=(12, 2))

# Draw bar
ax.barh(0, 1, height=0.2, color='lightgray', edgecolor='black')

# Color zones
ax.barh(0, 0.25, height=0.2, color='#EF3B2C', alpha=0.4)         # Liberal Majority
ax.barh(0, 0.25, left=0.25, height=0.2, color='#EF3B2C', alpha=0.2)  # Liberal Minority
ax.barh(0, 0.25, left=0.5, height=0.2, color='#1C3F94', alpha=0.2)  # CPC Minority
ax.barh(0, 0.25, left=0.75, height=0.2, color='#1C3F94', alpha=0.4) # CPC Majority

# Maple Leaf emoji
ax.text(slider_position, 0.05, "🍁", ha='center', va='center', fontsize=28)

# Labels
ax.text(0.125, -0.3, "Liberal Majority", ha='center', va='center', fontsize=10)
ax.text(0.375, -0.3, "Liberal Minority", ha='center', va='center', fontsize=10)
ax.text(0.625, -0.3, "CPC Minority", ha='center', va='center', fontsize=10)
ax.text(0.875, -0.3, "CPC Majority", ha='center', va='center', fontsize=10)

ax.set_xlim(0, 1)
ax.set_ylim(-0.6, 0.6)
ax.axis('off')

st.pyplot(fig)

# ------------ PARTY MAJORITY / MINORITY PROBABILITIES ------------
st.subheader("📊 Party Majority / Minority Chances")

simulations = {party: np.random.normal(loc=seat_data.get(party, 0), scale=5, size=1000) for party in EXPECTED_PARTIES}

cpc_sim = simulations['CPC']
lpc_sim = simulations['LPC']

cpc_majority_chance = (cpc_sim >= MAJORITY_THRESHOLD).mean()
lpc_majority_chance = (lpc_sim >= MAJORITY_THRESHOLD).mean()

cpc_lead_chance = (cpc_sim > lpc_sim).mean()
lpc_lead_chance = (lpc_sim > cpc_sim).mean()

cpc_minority_chance = cpc_lead_chance - cpc_majority_chance
lpc_minority_chance = lpc_lead_chance - lpc_majority_chance

st.markdown("### Conservatives (CPC)")
st.write(f"• **Majority chance**: {cpc_majority_chance:.1%}")
st.write(f"• **Minority lead chance**: {cpc_minority_chance:.1%}")

st.markdown("### Liberals (LPC)")
st.write(f"• **Majority chance**: {lpc_majority_chance:.1%}")
st.write(f"• **Minority lead chance**: {lpc_minority_chance:.1%}")

# ------------ FINAL WINNER / MAJORITY CALL ------------
st.subheader("🎯 Live Majority / Minority Status")

winner = max(seat_data.items(), key=lambda x: x[1])[0]
winner_seats = seat_data[winner]

st.write(f"### 🏆 **Current Leader**: {winner}")
st.write(f"### 🪧 **Projected Seats**: {winner_seats}")

if winner_seats >= MAJORITY_THRESHOLD:
    st.success(f"✅ {winner} currently projected to win a **Majority Government**!")
else:
    st.warning(f"⚠️ {winner} currently projected to lead a **Minority Government**.")

