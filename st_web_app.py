import os

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

    # If you're curious of all the loggers

    # chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
    # st.bar_chart(chart_data)
