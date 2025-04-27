# needle_final_results.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
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
TEST_MODE = st.sidebar.checkbox("🧪 Enable Test Simulation Mode", value=False)

if TEST_MODE:
    st.sidebar.warning("Test Simulation Active: Refreshing every 10 seconds")
    time.sleep(10)

    # Randomly adjust medians slightly
    for party in final_projection.keys():
        adjustment = np.random.randint(-5, 6)
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

# ------------ MAPLE LEAF SLIDING SCALE NEEDLE ------------
st.subheader("🍁 Final Election Needle - Maple Leaf Sliding Scale")

# Calculate probabilities
total_medians = sum(medians)
probabilities = {party: (median / total_medians) for party, median in zip(parties, medians)}

lpc_share = probabilities['LPC']
cpc_share = probabilities['CPC']

# Base deviation
base_position = lpc_share / (lpc_share + cpc_share)
deviation = (base_position - 0.5) * 2

# Add slight jitter
needle_jitter = np.random.normal(0, 0.01)
deviation = np.clip(deviation + needle_jitter, -1, 1)

# Map deviation [-1,1] to [0,1]
slider_position = (deviation + 1) / 2

fig, ax = plt.subplots(figsize=(12, 2))

# Draw base bar
ax.barh(0, 1, height=0.2, color='lightgray', edgecolor='black')

# Color zones
ax.barh(0, 0.25, height=0.2, color='#EF3B2C', alpha=0.4)         # Liberal Majority
ax.barh(0, 0.25, left=0.25, height=0.2, color='#EF3B2C', alpha=0.2)  # Liberal Minority
ax.barh(0, 0.25, left=0.5, height=0.2, color='#1C3F94', alpha=0.2)  # CPC Minority
ax.barh(0, 0.25, left=0.75, height=0.2, color='#1C3F94', alpha=0.4) # CPC Majority

# Load and plot Maple Leaf Image
leaf_img = mpimg.imread('maple_leaf.png')  # You need maple_leaf.png in your project folder
imagebox = OffsetImage(leaf_img, zoom=0.08)
ab = AnnotationBbox(imagebox, (slider_position, 0.05), frameon=False)
ax.add_artist(ab)

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

simulations = {party: np.random.normal(loc=data[party]['median'], scale=5, size=1000) for party in PARTIES}

cpc_seats = simulations['CPC']
lpc_seats = simulations['LPC']

cpc_majority_chance = (cpc_seats >= MAJORITY_THRESHOLD).mean()
lpc_majority_chance = (lpc_seats >= MAJORITY_THRESHOLD).mean()

cpc_lead_chance = (cpc_seats > lpc_seats).mean()
lpc_lead_chance = (lpc_seats > cpc_seats).mean()

cpc_minority_chance = cpc_lead_chance - cpc_majority_chance
lpc_minority_chance = lpc_lead_chance - lpc_majority_chance

st.markdown("### Conservatives (CPC)")
st.write(f"• **Majority chance**: {cpc_majority_chance:.1%}")
st.write(f"• **Minority lead chance**: {cpc_minority_chance:.1%}")

st.markdown("### Liberals (LPC)")
st.write(f"• **Majority chance**: {lpc_majority_chance:.1%}")
st.write(f"• **Minority lead chance**: {lpc_minority_chance:.1%}")

# ------------ FINAL WINNER / MAJORITY CALL ------------
st.subheader("🎯 Final Majority / Minority Status")

winner = max(data.items(), key=lambda x: x[1]['median'])[0]
winner_seats = data[winner]['median']

st.write(f"### 🏆 **Winning Party**: {winner}")
st.write(f"### 🪧 **Projected Seats**: {winner_seats}")

if winner_seats >= MAJORITY_THRESHOLD:
    st.success(f"✅ {winner} projected to win a **Majority Government**!")
else:
    st.warning(f"⚠️ {winner} projected to lead a **Minority Government**.")

# ------------ FINAL NEEDLE SEAT PROJECTION ------------
st.subheader("📈 Final Projected Seats by Party")

fig, ax = plt.subplots(figsize=(10, 6))

for i, party in enumerate(parties):
    ax.barh(party, ci_highs[i] - ci_lows[i], left=ci_lows[i],
            color=party_colors[party], edgecolor='black', alpha=0.7)
    ax.plot(medians[i], party, 'o', color='black')

ax.axvline(MAJORITY_THRESHOLD, color='black', linestyle='--', linewidth=1.5)
ax.text(MAJORITY_THRESHOLD + 1, -0.5, f'Majority ({MAJORITY_THRESHOLD} seats)', verticalalignment='bottom', fontsize=9)

ax.set_xlabel('Projected Seats')
ax.set_title('Final Needle Forecast')
ax.grid(True, linestyle='--', axis='x', alpha=0.5)

st.pyplot(fig)

# ------------ FINAL SEAT TRACKER TREND ------------
if len(history_tracker) > 1:
    st.subheader("📊 Seat Projection Tracker (Election Night Trend)")

    history_df = pd.DataFrame(history_tracker)

    fig3, ax3 = plt.subplots(figsize=(12, 6))

    for party in history_df.columns:
        ax3.plot(history_df.index, history_df[party], label=party, color=party_colors[party])

    ax3.set_xlabel('Update Cycle (Snapshot)')
    ax3.set_ylabel('Projected Seats')
    ax3.set_title('Seat Projection Tracker Over Election Night')
    ax3.grid(True, linestyle='--', alpha=0.5)
    ax3.legend()

    st.pyplot(fig3)
