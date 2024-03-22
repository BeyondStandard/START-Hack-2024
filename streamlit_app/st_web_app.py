import json
import os
import pandas as pd
import numpy as np
import streamlit as st

col1_1, col2_1, col3_1 = st.columns([1.5, 5, 2])

col2_1.title('Team Beyond Standard')
st.image(os.path.join('pics', 'hack.png'))
st.image(os.path.join('pics', 'st_gallen.jpg'))

# Launch Button
col1, col2, col3 = st.columns([2, 3, 1])

# img = Image.open("images/top_spiderman.png")
# st.button(st.image(img))

if col1.button('Ask a question!'):
    col1.write("Listening...")
    os.system('python record_voice.py')

if col3.button('View history'):
    df = pd.read_json("streamlit_app/ratings.json")
    df["sentiment"] = df["sentiment"].astype("category")
    df["emotion"] = df["emotion"].astype("category")
    df = df.rename(columns={"timestamp": "Timestamp", "emotion": "Emotion", "sentiment":"Sentiment"})
    st.bar_chart(df, x="Timestamp", y="Emotion", color="Sentiment")
