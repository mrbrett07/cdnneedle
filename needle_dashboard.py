# needle_final_results.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import time

# ------------ SETTINGS ------------
MAJORITY_THRESHOLD = 170
PARTIES = ['LPC', 'CPC', 'BQ', 'NDP', 'GPC', 'PPC']

party_colors = {
    'LPC': '#EF3B2C',
    'CPC': '#1C3F94',
    'NDP': '#F5841F',
    'BQ': '#49A2D6',
    'GPC': '#3D9B35',
    'PPC': '#6F259C'
}

# ------------ FINAL RESULTS BASED ON 338Canada (April 26, 2025) ------------
final_projection = {
    'LPC': {'median': 186, 'low': 172, 'high': 200},
    'CPC': {'median': 126, 'low': 110, 'high': 140},
    'BQ':  {'median': 23,  'low': 18,  'high': 28},
    'NDP': {'median': 7,   'low': 4,   'high': 10},
    'GPC': {'median': 1,   'low': 0,   'high': 2},
    'PPC': {'median': 0,   'low': 0,   'high': 1}
}

# Fake history tracker
history_tracker = [
    {'LPC': 180, 'CPC': 130, 'BQ': 22, 'NDP': 8, 'GPC': 1, 'PPC': 0},
    {'LPC': 186, 'CPC': 126, 'BQ': 23, 'NDP': 7, 'GPC': 1, 'PPC': 0}
]

# ------------ STREAMLIT APP SETUP ------------
st.set_page_config(page_title="Canadian Election Final Needle", layout="centered")

st.title("🇨🇦 Final Canadian Election Projection")
st.caption("Static view — Final predicted results (April 26, 2025)")

# ------------ TEST SIMULATION MODE ------------
TEST_MODE = st.sidebar.selectbox(
    "🧪 Test Simulation Mode",
    options=["Off", "Normal (10s small swings)", "Wild (5s big swings)"],
    index=0
)

if TEST_MODE == "Normal (10s small swings)":
    st.sidebar.warning("Normal Test Mode: Refreshing every 10 seconds, small seat changes.")
    time.sleep(10)
    for party in final_projection.keys():
        adjustment = np.random.randint(-5, 6)
        final_projection[party]['median'] = max(0, final_projection[party]['median'] + adjustment)

elif TEST_MODE == "Wild (5s big swings)":
    st.sidebar.warning("⚡ Wild Test Mode: Refreshing every 5 seconds, big chaotic swings!")
    time.sleep(5)
    for party in final_projection.keys():
        adjustment = np.random.randint(-20, 21)  # wild swings
        final_projection[party]['median'] = max(0, final_projection[party]['median'] + adjustment)

# ------------ FINAL RESULTS ------------
data = final_projection
parties = list(data.keys())
medians = [data[p]['median'] for p in parties]
ci_lows = [data[p]['low'] for p in parties]
ci_highs = [data[p]['high'] for p in parties]

# ------------ FINAL NUMBERS DISPLAY ------------
st.subheader("📋 Final Projected Seat Totals")

seat_data = {party: data[party]['median'] for party in parties}
seat_df = pd.DataFrame.from_dict(seat_data, orient='index', columns=['Projected Seats'])
seat_df = seat_df.sort_values(by='Projected Seats', ascending=False)

st.table(seat_df)

# ------------ MAPLE LEAF SLIDING SCALE (SMART VERSION) ------------
st.subheader("🍁 Final Election Needle - Maple Leaf Sliding Scale")

# Get main party seat projections
lpc_seats = final_projection['LPC']['median']
cpc_seats = final_projection['CPC']['median']

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
slider_position = np.clip(slider_base + np.random.normal(0, 0.02), 0, 1)

fig, ax = plt.subplots(figsize=(12, 2))

# Draw base bar
ax.barh(0, 1, height=0.2, color='lightgray', edgecolor='black')

# Color zones
ax.barh(0, 0.25, height=0.2, color='#EF3B2C', alpha=0.4)         # Liberal Majority
ax.barh(0, 0.25, left=0.25, height=0.2, color='#EF3B2C', alpha=0.2)  # Liberal Minority
ax.barh(0, 0.25, left=0.5, height=0.2, color='#1C3F94', alpha=0.2)  # CPC Minority
ax.barh(0, 0.25, left=0.75, height=0.2, color='#1C3F94', alpha=0.4) # CPC Majority

# Maple Leaf emoji as the needle
ax.text(slider_position, 0.05, "🍁", ha='center', va='center', fontsize=28)

# Labels
ax.text(0.125,
