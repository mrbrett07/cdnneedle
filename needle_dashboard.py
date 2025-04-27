# needle_dashboard.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import requests

# ------------ SETTINGS ------------
AUTO_REFRESH_SECONDS = 60  # Change refresh interval (seconds)
MAJORITY_THRESHOLD = 170   # Canadian federal majority seat threshold
USE_FAKE_DATA = True       # Switch to False to use real Elections Canada feed
PARTIES = ['LPC', 'CPC', 'NDP', 'BQ', 'GPC', 'PPC']

# Party colours
party_colors = {
    'LPC': '#EF3B2C',
    'CPC': '#1C3F94',
    'NDP': '#F5841F',
    'BQ': '#49A2D6',
    'GPC': '#3D9B35',
    'PPC': '#6F259C'
}

# ------------ FUNCTIONS ------------

def fetch_fake_data():
    """Simulate fake live results for testing before election day."""
    ridings = [f"Riding {i}" for i in range(1, 31)]
    data = []
    for riding in ridings:
        reporting_pct = np.random.randint(10, 90)
        total_votes = np.random.randint(1000, 5000)
        votes = np.random.dirichlet(np.ones(len(PARTIES))) * total_votes
        votes = {party: int(v) for party, v in zip(PARTIES, votes)}
        entry = {"riding": riding, "reporting_pct": reporting_pct, **votes}
        data.append(entry)
    df = pd.DataFrame(data)
    return df

def fetch_real_data():
    """Fetch live Elections Canada data (update URL on election night)."""
    try:
        url = "https://enr.elections.ca/Feed/Results.json"  # Placeholder
        response = requests.get(url)
        data = response.json()

        results = []
        for riding in data["races"]:
            entry = {
                "riding": riding["name"],
                "reporting_pct": riding.get("reporting", 0)
            }
            for party in PARTIES:
                entry[party] = riding.get("votes", {}).get(party, 0)
            results.append(entry)

        return pd.DataFrame(results)

    except Exception as e:
        st.error(f"Error fetching Elections Canada data: {e}")
        return fetch_fake_data()  # fallback to fake

def get_live_results():
    """Get live election results."""
    if USE_FAKE_DATA:
        df = fetch_fake_data()
    else:
        df = fetch_real_data()

    party_cols = PARTIES
    total_votes = df[party_cols].sum()
    total = total_votes.sum()
    swing_projection = (total_votes / total).to_dict()

    # Base expected seats before election night
    base_forecast = {
        'LPC': 135, 'CPC': 145, 'NDP': 25, 'BQ': 30, 'GPC': 2, 'PPC': 1
    }

    results = {}
    for party in party_cols:
        share = swing_projection[party]
        median = int(base_forecast[party] * (1 + (share - 0.15)))  # rough adjust
        results[party] = {
            "median": median,
            "low": int(median * 0.9),
            "high": int(median * 1.1)
        }

    return results

# ------------ STREAMLIT APP ------------

st.set_page_config(page_title="Canadian Election Needle", layout="centered")

st.title("🇨🇦 Canadian Election Needle Dashboard")
st.caption("Real-time forecast — auto-refresh every 60 seconds")

while True:
    data = get_live_results()
    parties = list(data.keys())
    medians = [data[p]['median'] for p in parties]
    ci_lows = [data[p]['low'] for p in parties]
    ci_highs = [data[p]['high'] for p in parties]

    # ------------ PROBABILITY BAR ------------
    total_medians = sum(medians)
    probabilities = {party: (median / total_medians) for party, median in zip(parties, medians)}

    st.subheader("🗳️ Current Chance of Winning (Simulated)")

    fig2, ax2 = plt.subplots(figsize=(10, 2))

    # Stacked probability bar
    start = 0
    for party in parties:
        prob = probabilities[party]
        ax2.barh(0, prob, left=start, color=party_colors[party], edgecolor='black')
        start += prob

    ax2.set_xlim(0, 1)
    ax2.set_yticks([])
    ax2.set_xticks(np.linspace(0, 1, 11))
    ax2.set_xticklabels([f"{int(x*100)}%" for x in np.linspace(0, 1, 11)])
    ax2.set_title("Live Probability to Win (Based on Projected Seats)")
    ax2.grid(axis='x', linestyle='--', alpha=0.5)

    st.pyplot(fig2)

    # ------------ NEEDLE SEAT PROJECTION ------------
    st.subheader("📈 Projected Seats by Party")

    fig, ax = plt.subplots(figsize=(10, 6))

    for i, party in enumerate(parties):
        ax.barh(party, ci_highs[i] - ci_lows[i], left=ci_lows[i],
                color=party_colors[party], edgecolor='black', alpha=0.7)
        ax.plot(medians[i], party, 'o', color='black')

    ax.axvline(MAJORITY_THRESHOLD, color='black', linestyle='--', linewidth=1.5)
    ax.text(MAJORITY_THRESHOLD + 1, -0.5, f'Majority ({MAJORITY_THRESHOLD} seats)', verticalalignment='bottom', fontsize=9)

    ax.set_xlabel('Projected Seats')
    ax.set_title('Live Needle Forecast')
    ax.grid(True, linestyle='--', axis='x', alpha=0.5)

    st.pyplot(fig)

    st.info(f"⏳ Auto-refreshing in {AUTO_REFRESH_SECONDS} seconds...")

    time.sleep(AUTO_REFRESH_SECONDS)
    st.experimental_rerun()