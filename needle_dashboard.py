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
    options=["Off", "Normal (10s small swings)", "Wild (5s big swings)", "Elections Canada Simulator"],
    index=0
)

# Tracking % reporting for Elections Canada Simulator
if 'votes_counted_pct' not in st.session_state:
    st.session_state.votes_counted_pct = 0

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
        adjustment = np.random.randint(-20, 21)
        final_projection[party]['median'] = max(0, final_projection[party]['median'] + adjustment)

elif TEST_MODE == "Elections Canada Simulator":
    st.sidebar.warning("🗳️ Elections Canada Simulator Active: Simulating votes coming in.")
    time.sleep(5)
    # Increase counted votes
    if st.session_state.votes_counted_pct < 100:
        increase = np.random.randint(3, 8)  # +3% to +7% votes counted per update
        st.session_state.votes_counted_pct = min(100, st.session_state.votes_counted_pct + increase)

        uncertainty_factor = (100 - st.session_state.votes_counted_pct) / 100  # Higher uncertainty early on

        for party in final_projection.keys():
            adjustment = int(np.random.normal(0, 10 * uncertainty_factor))  # Wild early, small late
            final_projection[party]['median'] = max(0, final_projection[party]['median'] + adjustment)

    st.sidebar.info(f"📊 Votes counted: **{st.session_state.votes_counted_pct}%**")

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

