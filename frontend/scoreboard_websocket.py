import streamlit as st
import requests
import websocket
import json
import threading
import pandas as pd
import trueskill as ts
from algorithms import matchmaking_afterwards, update_ratings
from dotenv import load_dotenv
import os

load_dotenv()
API_URL= os.getenv('API_URL')
DUEL_URL = f"{API_URL}/api/duel"


def get_headers():
    return {"Authorization": f"Bearer {st.session_state['jwt_token']}"}

# Global variable to store duel results
duel_results = []

# Function to handle WebSocket messages
def on_message(ws, message):
    data = json.loads(message)
    duel_results.append(data)  # Update the list of results
    # Refresh the Streamlit app to display the updated list
    st.rerun()

# Initialize WebSocket connection
def connect_ws():
    ws = websocket.WebSocketApp("ws://localhost:8080/ws", on_message=on_message)
    ws.run_forever()

# Function to update duel result
def update_duel_result(did, result_data):
    try: # Add error handling
        headers = get_headers()
        url = f"{DUEL_URL}/{did}/result"
        response = requests.put(url, json=result_data, headers=headers)
        st.success("Duel result updated successfully.")
    except requests.exceptions.RequestException as e:
        st.warning({"error": "Failed to update duel result."})

# Function to fetch all duels
def fetch_duels(tid):
    try: # Add error handling
        url = f"{DUEL_URL}?tid={tid}"
        response = requests.get(url, headers=get_headers())
        return response.json() if response.status_code == 200 else []
    except requests.exceptions.RequestException as e:
        return []
    
# Prepare data for display
def prepare_duel_data(duels):
    duel_data = []
    if duels:
        for duel in duels:
            # Convert milliseconds to seconds
            player1Time_s = duel['result'].get('player1Time', None) / 1000 if duel['result'] and 'player1Time' in duel['result'] else "N/A"
            player2Time_s = duel['result'].get('player2Time', None) / 1000 if duel['result'] and 'player2Time' in duel['result'] else "N/A"
            
            duel_info = {
                "Duel ID": duel['duel_id'],
                "Round": duel['roundName'],
                "Player 1 Username": duel['pid1']['username'],
                "Player 2 Username": duel['pid2']['username'] if duel.get('pid2') and duel['pid2'].get('username') else "N/A",
                "Player 1 Time (s)": player1Time_s,
                "Player 2 Time (s)": player2Time_s,
                "Winner": (
                    duel['pid1']['username'] if duel['winner'] == 1 and duel['pid1'] is not None
                    # else duel['pid2']['username'] if duel['winner'] == duel['pid2']['profileId']
                    else duel['pid2']['username'] if duel['winner'] == 2 and duel['pid2'] is not None
                    else "Not determined"
                )
            }

            duel_data.append(duel_info)
    return duel_data

@st.cache_data
def display_duel_table(duel_data):
    if duel_data:
        duel_df = pd.DataFrame(duel_data)
        st.dataframe(duel_df, hide_index=True)        
    else:
        st.write("No duels happening right now.")

def update_scoreboard():
    # Start the WebSocket connection in a separate thread
    if 'ws_thread' not in st.session_state:
        st.session_state.ws_thread = threading.Thread(target=connect_ws, daemon=True)
        st.session_state.ws_thread.start()

    st.title("Duel Management Live Scoreboard")
    for result in duel_results:
        st.write(f"Duel ID: {result['duel_id']}, Player 1 Time: {result['score']['player1Time']} ms, Player 2 Time: {result['score']['player2Time']} ms, Winner: {result['winner']}")

    # Update Duel Form
    did = st.number_input("Enter Duel ID:", min_value=1)
    col1, col2 = st.columns(2)
    with col1:
        player1_seconds = st.number_input("Player 1 Time (seconds):", min_value=0)
    with col2:
        player1_milliseconds = st.number_input("Player 1 Time (milliseconds):", min_value=0)

    col3, col4 = st.columns(2)
    with col3:
        player2_seconds = st.number_input("Player 2 Time (seconds):", min_value=0)
    with col4:
        player2_milliseconds = st.number_input("Player 2 Time (milliseconds):", min_value=0)

    # Convert seconds and milliseconds to total milliseconds
    player1Time = player1_seconds * 1000 + player1_milliseconds
    player2Time = player2_seconds * 1000 + player2_milliseconds

    # Update Duel Result Form
    if st.button("Update Duel Result"):
        result_data = {
            "player1Time": player1Time,
            "player2Time": player2Time,
        }
        update_duel_result(did, result_data)
        update_ratings(did, player1Time, player2Time)
        matchmaking_afterwards()

def live_scoreboard(tid):
    st.title("Live Duel Scoreboard")

    if 'duels' not in st.session_state:
        st.session_state.duels = fetch_duels(tid)

    duel_data = prepare_duel_data(st.session_state.duels)

    # if st.button("Refresh Results"):
    with st.spinner("Fetching latest results..."):
        st.session_state.duels = fetch_duels(tid) 
        duel_data = prepare_duel_data(st.session_state.duels) 

        # Update the cached table
        display_duel_table(duel_data)

        # Check for errors after fetching
        # if not st.session_state.duels:
        #     st.error("Failed to fetch duel results. Please try again.")
