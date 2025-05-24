# -*- coding: utf-8 -*-
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file"
]
def init_connection():
    creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"])
    scoped_creds = creds.with_scopes(SCOPES)
    return gspread.authorize(scoped_creds)

client = init_connection()
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1uo2H9vWtxUAL2Y7FU6fQi922_Pk7PWGzW75OwpIPFB0/edit?gid=0#gid=0").sheet1

#manually refresh database load every submission to ensure up to date
@st.cache_data(ttl=60)
def get_mood_data():
    return pd.DataFrame(sheet.get_all_records())

###############################################
def main():
    st.title("Mood Tracker")
    st.write("select a mood on the dropdown below")
    mood_types = ["😁Great", "🙂 Happy", "😐 ok", "😞 Sad", "😢 Very sad"]
    with st.form("Current mood"):
        moodscore = st.selectbox("Rate your current mood",
                                     options = mood_types, index = 2)
        note = st.text_input("Additional notes")
        submitted = st.form_submit_button("Submit your mood")

        if submitted:
            timestamp = datetime.now().strftime("%m-%d-%y %H:%M")
            edit_data(timestamp, moodscore,note)
            st.success("Mood logged successfully")
            st.cache_data.clear()
            st.rerun()
    ################################################
    st.write("Quickly review submitted moodscores in the datatable below")
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    st.dataframe(data)
    #bar graph current moods
    mood_counts = df['Moodscore'].value_counts().reindex(mood_types, fill_value=0)
    fig,ax = plt.subplots(figsize=(10,5), constrained_layout=True, facecolor = 'white')
    bars = ax.barh(mood_types,mood_counts.values)
    for bar in bars:
        ax.text(bar.get_width(), bar.get_y() + bar.get_height()/2,f'{bar.get_width()}',va='center',color='white')
    ax.set_title("All logged moods", fontsize=14, pad = 20, color = 'black')
    ax.set_xlabel('count', fontsize = 12, visible = True, color = 'black')
    ax.set_ylabel('moods', fontsize=12, visible = True, color = 'black')
    ax.tick_params(axis='both', colors='black')
    fig.tight_layout(pad = 3)
    plt.rcParams.update({'figure.autolayout': True})
    st.pyplot(fig,clear_figure = False,use_container_width=True)
    
    
    st.write("Demo internal tool")
def edit_data(timestamp,moodscore, note=""):
    try: 
        sheet.append_row([timestamp, moodscore, note])
        return True
    except Exception as e:
        st.error(f"Failed to add to database:{e}")

if __name__ == "__main__":
    main()