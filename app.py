import json
import requests
import streamlit as st
import base64

def set_bg_hack(main_bg):
    main_bg_ext = "jpg"
    st.markdown(
         f"""
         <style>
         .stApp {{
             background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()});
             background-size: cover;
         }}
         </style>
         """,
         unsafe_allow_html=True
     )


try:
    set_bg_hack('background.png')
except:
    st.warning("Pozadinska slika 'background.jpg' nije pronađena.")

st.set_page_config(page_title="MPG Predictor", page_icon="⛽", layout="centered")

st.title("⛽ Auto MPG Predictor")
st.write("Unesi podatke o autu i dobit ćeš predikciju potrošnje (MPG).")

DEFAULT_ENDPOINT = "http://6b25a45b-1390-4c03-b2f6-7daefa15827a.germanywestcentral.azurecontainer.io/score"

endpoint = st.secrets["AZURE_ENDPOINT"]

st.divider()

col1, col2 = st.columns(2)

with col1:
    cylinders = st.number_input("Cylinders", min_value=3, max_value=16, value=4, step=1)
    displacement = st.number_input("Displacement", min_value=0.0, value=140.0, step=1.0)
    horsepower = st.number_input("Horsepower", min_value=0.0, value=90.0, step=1.0)
    weight = st.number_input("Weight", min_value=0, value=2400, step=10)

with col2:
    acceleration = st.number_input("Acceleration", min_value=0.0, value=15.0, step=0.1)
    model_year = st.number_input("Model year", min_value=70, max_value=90, value=78, step=1)
    origin = st.selectbox("Origin", options=[1, 2, 3], index=0, help="1=USA, 2=Europe, 3=Japan")

payload = {
    "input_data": [
        {
            "cylinders": int(cylinders),
            "displacement": float(displacement),
            "horsepower": float(horsepower),
            "weight": int(weight),
            "acceleration": float(acceleration),
            "model year": int(model_year),
            "origin": int(origin),
        }
    ]
}

if st.button("Predict MPG", type="primary"):
    if not endpoint or endpoint.startswith("PASTE_"):
        st.error("Upiši ispravan Azure endpoint URL.")
    else:
        try:
            headers = {"Content-Type": "application/json"}
            resp = requests.post(endpoint, json=payload, headers=headers, timeout=30)

            if resp.status_code != 200:
                st.error(f"Greška {resp.status_code}: {resp.text}")
            else:
                result = resp.json()  
                mpg = float(result[0]) if isinstance(result, list) else float(result)

                st.success(f"Predikcija: **{mpg:.2f} MPG**")
                
                l_per_100km = 235.214583 / mpg if mpg > 0 else None
                if l_per_100km:
                    st.info(f"≈ **{l_per_100km:.2f} L/100km**")

        except requests.exceptions.Timeout:
            st.error("Timeout (30s). Endpoint je spor ili nedostupan.")
        except Exception as e:
            st.error(f"Nešto je pošlo krivo: {e}")