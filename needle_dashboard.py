# needle_dashboard.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Simulate live results (replace with live Elections Canada feed)
def get_live_results():
    # Replace with actual API or JSON feed later
    return {
        'LPC': {'median': 142, 'low': 130, 'high': 155},
        'CPC': {'median': 151, 'low': 140, 'high': 163},
        'NDP': {'median': 22, 'low': 15, 'high': 30},
        'BQ': {'median': 30, 'low': 25, 'high': 35},
        'GPC': {'median': 2, 'low': 1, 'high': 4},
        'PPC': {'median': 1, 'low': 0, 'high': 2},
    }

# Party colors
party_colors = {
    'LPC': '#EF3B2C',
    'CPC': '#1C3F94',
    'NDP': '#F5841F',
    'BQ': '#49A2D6',
    'GPC': '#3D9B35',
    'PPC': '#6F259C'
}

# Streamlit app layout
st.title("Canadian Election Needle Forecast")
st.caption("Simulated real-time forecast")

data = get_live_results()
parties = list(data.keys())
medians = [data[p]['median'] for p in parties]
ci_lows = [data[p]['low'] for p in parties]
ci_highs = [data[p]['high'] for p in parties]

# Visualization
fig, ax = plt.subplots(figsize=(10, 6))

for i, party in enumerate(parties):
    ax.barh(party, ci_highs[i] - ci_lows[i], left=ci_lows[i],
            color=party_colors[party], edgecolor='black', alpha=0.6)
    ax.plot(medians[i], party, 'o', color='black')

# Majority line
majority = 170
ax.axvline(majority, color='black', linestyle='--', linewidth=1.5)
ax.text(majority + 1, -0.5, 'Majority (170 seats)', verticalalignment='bottom', fontsize=9)

ax.set_xlabel('Projected Seats')
ax.set_title('Live Needle Forecast')
ax.grid(True, linestyle='--', axis='x', alpha=0.6)

st.pyplot(fig)
