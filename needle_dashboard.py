# needle_final_results.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ------------ SETTINGS ------------
MAJORITY_THRESHOLD = 170
PARTIES = ['LPC', 'CPC', 'BQ', 'NDP', 'GPC', 'PPC']

# Party colors
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

# Fake historical seat tracker
history_tracker = [
    {'LPC': 180, 'CPC': 130, 'BQ': 22, 'NDP': 8, 'GPC': 1, 'PPC': 0},
    {'LPC': 186, 'CPC': 126, 'BQ': 23, 'NDP': 7, 'GPC': 1, 'PPC': 0}
]

# ------------ STREAMLIT APP ------------
st.set_page_config(page_title="Canadian Election Final Needle", layout="centered")

st.title("🇨🇦 Final Canadian Election Projection")
st.caption("Static view — Final predicted results (April 26, 2025)")

# Fetch final results
data = final_projection
parties = list(data.keys())
medians = [data[p]['median'] for p in parties]
ci_lows = [data[p]['low'] for p in parties]
ci_highs = [data[p]['high'] for p in parties]

# ------------ CLEAR FINAL NUMBERS ------------
st.subheader("📋 Final Projected Seat Totals")

seat_data = {party: data[party]['median'] for party in parties}
seat_df = pd.DataFrame.from_dict(seat_data, orient='index', columns=['Projected Seats'])
seat_df = seat_df.sort_values(by='Projected Seats', ascending=False)

st.table(seat_df)

# ------------ NYT-STYLE ANIMATED NEEDLE ------------
st.subheader("🧭 Final Needle - NYT Animated Style")

total_medians = sum(medians)
probabilities = {party: (median / total_medians) for party, median in zip(parties, medians)}

lpc_share = probabilities['LPC']
cpc_share = probabilities['CPC']

# Base needle position
base_needle_position = lpc_share / (lpc_share + cpc_share)

# Add slight jitter to simulate animation
needle_jitter = np.random.normal(0, 0.01)
needle_position = np.clip(base_needle_position + needle_jitter, 0, 1)

fig2, ax2 = plt.subplots(figsize=(10, 2))

# Create a thin horizontal bar
ax2.barh(0, needle_position, color=party_colors['LPC'], edgecolor='black')
ax2.barh(0, 1-needle_position, left=needle_position, color=party_colors['CPC'], edgecolor='black')

# Draw needle (simple marker for now)
ax2.plot([needle_position], [0], marker='v', markersize=20, color='black')

ax2.set_xlim(0, 1)
ax2.set_ylim(-0.5, 0.5)
ax2.set_yticks([])
ax2.set_xticks(np.linspace(0, 1, 11))
ax2.set_xticklabels([f"{int(x*100)}%" for x in np.linspace(0, 1, 11)])
ax2.text(0.01, -0.3, "Liberals favored", ha='left', va='center', fontsize=10)
ax2.text(0.99, -0.3, "Conservatives favored", ha='right', va='center', fontsize=10)
ax2.axis('off')

st.pyplot(fig2)

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
