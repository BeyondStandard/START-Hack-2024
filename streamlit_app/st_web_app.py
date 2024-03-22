import json
import os
import pandas as pd
import numpy as np
import streamlit as st

col1_1, col2_1, col3_1 = st.columns([1.5, 5, 1])

col2_1.title('Team Beyond Standard')
st.image(os.path.join('pics', 'hack.png'))
st.image(os.path.join('pics', 'st_gallen.jpg'))

# Launch Button
col1, col2, col3 = st.columns([1.5, 1, 1])

# img = Image.open("images/top_spiderman.png")
# st.button(st.image(img))

if col2.button('Ask a question!'):
    col2.write("Listening...")
    os.system('python record_voice.py')

if col3.button('View history'):
    df = pd.read_json("streamlit_app/ratings.json")
    df["sentiment"] = df["sentiment"].astype("category")
    df["emotion"] = df["emotion"].astype("category")
    st.bar_chart(df, x="timestamp", y="emotion", color="sentiment")
