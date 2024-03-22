import time
import pandas as pd
import streamlit as st
import os

if "current_page" not in st.session_state:
    st.session_state.current_page = "page_1"


def navigate_to_page(page_name):
    st.session_state.current_page = page_name


if st.session_state.current_page == "page_1":
    st.markdown(
        """
        <style>
        .appview-container {
            background-image: url("https://cdn.discordapp.com/attachments/663083712619216897/1220566048215142501/Frame_1_2.png?ex=660f67b6&is=65fcf2b6&hm=aef67506fbc07d7366db7687be411c0ef87a3751dd4db498b25bcdc60b8923d8&");
            background-size: cover;
        }
        .circle-button {
            display: inline-block;
            height: 80px;
            width: 80px;
            line-height: 80px;
            border-radius: 50%;
            background-color: #414141;
            opacity: 0.85;
            color: white;
            text-align: center;
            font-size: 28px;
            position: relative;
            cursor: pointer;
            margin: 1.5%;
          }
          .circle-button:active {
            background-color: #5E5E5E;
          }
          .phone-wrapper {
            text-align: center;
          }
          .phone-svg {
            background-color: #66C961;
            border-radius: 50%;
            margin: 1.5%;
          }
          .phone-svg:active {
            background-color: #3C9548;
          }
          .phone-number {
            font-size: 26px;
            margin-bottom: 4%;
            color: white;
          }
          .stButton>button {
            left: 35%;
            position: absolute;
            background-color: #4CAF50;
            color: white;
            padding: 14px 20px;
            margin: 20px 0;
            border: none;
            cursor: pointer;
            width: 30%;
          }
          .stButton>button:hover {
            color: white;
          }
          .stSpinner {
            left: 42%;
            position: absolute;
          }
        </style>
        <div class="phone-wrapper">
            <div class="phone-number">+41 87199 73012</div>
            <div>
                <div class="circle-button" onclick="alert('Clicked!')">1</div>
                <div class="circle-button">2</div>
                <div class="circle-button">3</div>
            </div>
            <div>
                <div class="circle-button">4</div>
                <div class="circle-button">5</div>
                <div class="circle-button">6</div>
            </div>
            <div>
                <div class="circle-button">7</div>
                <div class="circle-button">8</div>
                <div class="circle-button">9</div>
            </div>
            <div>
                <div class="circle-button">*</div>
                <div class="circle-button">0</div>
                <div class="circle-button">#</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.spinner("Listening..."):
        if st.button("Call", key="btn"):
            navigate_to_page("page_2")
            os.system("python STT/record_voice.py")

        with st.sidebar:
            ratings_path = os.path.join("frontend", "ratings.json")
            df = pd.read_json(ratings_path)
            df["sentiment"] = df["sentiment"].astype("category")
            df["emotion"] = df["emotion"].astype("category")
            df = df.rename(
                columns={
                    "timestamp": "Timestamp",
                    "emotion": "Emotion",
                    "sentiment": "Sentiment",
                }
            )
            st.bar_chart(df, x="Timestamp", y="Emotion", color="Sentiment")


elif st.session_state.current_page == "page_2":
    st.markdown(
        """
        <style>
        .appview-container {
            background-image: url("https://cdn.discordapp.com/attachments/663083712619216897/1220566048215142501/Frame_1_2.png?ex=660f67b6&is=65fcf2b6&hm=aef67506fbc07d7366db7687be411c0ef87a3751dd4db498b25bcdc60b8923d8&");
            background-size: cover;
        }
        .circle-button {
            display: inline-block;
            height: 80px;
            width: 80px;
            line-height: 80px;
            border-radius: 50%;
            background-color: #414141;
            opacity: 0.85;
            color: white;
            text-align: center;
            font-size: 28px;
            position: relative;
            cursor: pointer;
            margin: 1.5%;
        }
        .circle-button:active {
            background-color: #5E5E5E;
        }

        .phone-wrapper {
            text-align: center;
        }

        .phone-number {
            font-size: 26px;
            margin-bottom: 4%;
            color: white;
        }
        .stButton>button {
            left: 35%;
            position: absolute;
            background-color: #FF3B30;
            color: white;
            padding: 14px 20px;
            margin: 8px 0;
            border: none;
            cursor: pointer;
            width: 30%;
          }
          .stButton>button:hover {
            color: white;
          }
          .spinner {
            left: 35%;
            position: absolute;
          }
        .end-call-button {
            display: inline-block;
            background-color: #FF3B30;
            color: white;
            padding: 14px 20px;
            border: none;
            cursor: pointer;
            width: 30%;
            font-size: 20px;
            border-radius: 50px;
            margin: 100px auto;
            display: block;
        }
        .end-call-button:hover {
            background-color: #E63946;
        }
        .lower-button-row {
            margin-bottom: 70px; 
        }
        </style>
        <div class="phone-wrapper">
            <div class="phone-number">+41 87199 73012</div>
            <div>
                <div class="circle-button" onclick="alert('Mute!')">&#x1f507;</div>
                <div class="circle-button" onclick="alert('Keypad!')">&#x1f50a;</div>
                <div class="circle-button" onclick="alert('Speaker!')">&#x2328;</div>
            </div>
            <div class="lower-button-row">
                <div class="circle-button" onclick="alert('Add call!')">&#x2b;</div>
                <div class="circle-button" onclick="alert('FaceTime!')">&#x1f440;</div>
                <div class="circle-button" onclick="alert('Show contacts!')">&#x1f464;</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Remove this block if you're handling the end call with the HTML/CSS-styled button
    with st.spinner("Listening..."):
        if st.button("End Call", key="btn"):
            navigate_to_page("page_1")
