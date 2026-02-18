import streamlit as st

# Page Config
st.set_page_config(page_title="Waveside Golgappa", page_icon="🌊", layout="centered")

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #fefae0;
    }
    .title {
        text-align: center;
        color: #ff006e;
        font-size: 20px;
        font-weight: bold;
    }
    .subtitle {
        text-align: center;
        color: gray;
        font-size: 18px;
    }
    .menu-box {
        background-color: white;
        padding: 20px;
        margin: 10px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("<div class='title'>🌊 Waveside Golgappa</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Fresh • Crispy • Spicy</div>", unsafe_allow_html=True)

st.write("---")

# Welcome Section
st.header("welcome!")
st.write("Experience the taste of authentic, mouth-watering golgappas")
#import streamlit as st

st.title("Waveside Golgappa")

if "order_clicked" not in st.session_state:
   st.session_state.order_clicked = False

if st.button("Order Now"):
   st.session_state.order_clicked = True

if st.session_state.order_clicked:
    st.success("Your order has been placed successfully!")
st.write("---")

# Menu Section
st.header("Our Menu")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("<div class='menu-box'><h4>Classic Golgappa</h4><p>₹30 per plate</p></div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='menu-box'><h4>Spicy Mint Golgappa</h4><p>₹40 per plate</p></div>", unsafe_allow_html=True)

with col3:
    st.markdown("<div class='menu-box'><h4>Sweet & Tangy Golgappa</h4><p>₹40 per plate</p></div>", unsafe_allow_html=True)

st.write("---")

# Contact Section
st.header("Contact Us")
st.write("Waveside Beach Road")
st.write("Phone:+91 7052796564")

st.write("---")
st.caption("© 2026 Waveside Golgappa | All Rights Reserved")
