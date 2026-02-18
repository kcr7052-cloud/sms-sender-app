import streamlit as st
import datetime
from twilio.rest import Client  # For SMS

# Twilio setup (replace with your real credentials)
TWILIO_ACCOUNT_SID = 'your_account_sid_here'  # From Twilio dashboard
TWILIO_AUTH_TOKEN = 'your_auth_token_here'    # From Twilio dashboard
TWILIO_PHONE_NUMBER = '+1234567890'          # Your Twilio virtual number
YOUR_PHONE_NUMBER = '+0987654321'            # Your real phone number to receive SMS

# Sample menu items (you can customize)
menu = {
    "Gulab Jamun": 50,  # Price in INR
    "Ras Malai": 60,
    "Jalebi": 40,
    "Ladoo": 30,
    "Barfi": 70
}

# Function to calculate total
def calculate_total(order):
    return sum(menu[item] * qty for item, qty in order.items() if qty > 0)

# Function to send SMS
def send_sms(message):
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=YOUR_PHONE_NUMBER
        )
        return True
    except Exception as e:
        st.error(f"SMS failed: {e}")
        return False

# Sidebar for navigation (with colored title)
st.sidebar.markdown("<h2 style='color: #FF6B35;'>Sweet Waveside SK Shop</h2>", unsafe_allow_html=True)
st.sidebar.image("https://via.placeholder.com/150x100?text=Shop+Logo", caption="Our Logo")  # Replace with your image URL
page = st.sidebar.radio("Navigate", ["Browse Menu", "Place Order"])

if page == "Browse Menu":
    # Colored title for Menu
    st.markdown("<h1 style='color: #4CAF50;'>Our Delicious Sweets Menu</h1>", unsafe_allow_html=True)
    st.write("Explore our handcrafted sweets!")
    for item, price in menu.items():
        st.write(f"**{item}**: ₹{price} per piece")
    st.info("Head to 'Place Order' to select and order items.")

elif page == "Place Order":
    # Colored title for Order
    st.markdown("<h1 style='color: #2196F3;'>Place Your Order</h1>", unsafe_allow_html=True)
    st.write("Select your sweets, enter details, and click 'Order Now'!")

    # Colored subheader for Select Items group
    st.markdown("<h3 style='color: #9C27B0;'>Select Items</h3>", unsafe_allow_html=True)
    order = {}
    cols = st.columns(2)
    for i, (item, price) in enumerate(menu.items()):
        with cols[i % 2]:
            qty = st.number_input(f"{item} (₹{price})", min_value=0, max_value=10, step=1, key=item)
            order[item] = qty

    total = calculate_total(order)
    if total > 0:
        st.markdown(f"<h4 style='color: #FF9800;'>Total Cost: ₹{total}</h4>", unsafe_allow_html=True)
    else:
        st.warning("Please select at least one item.")

    # Colored subheader for Your Details group
    st.markdown("<h3 style='color: #9C27B0;'>Your Details</h3>", unsafe_allow_html=True)
    with st.form("order_form"):
        name = st.text_input("Full Name")
        phone = st.text_input("Phone Number")
        address = st.text_area("Delivery Address")
        special_notes = st.text_area("Special Notes (e.g., allergies or preferences)", height=100)
        order_now = st.form_submit_button("Order Now")

    # Handle order submission
    if order_now:
        if total > 0 and name and phone and address:
            # Create order summary
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            order_items = "\n".join([f"- {item}: {qty} pcs" for item, qty in order.items() if qty > 0])
            summary = f"[{timestamp}]\nName: {name}\nPhone: {phone}\nAddress: {address}\nSpecial Notes: {special_notes}\nOrder:\n{order_items}\nTotal: ₹{total}\n\n"
            
            # Display success and summary
            st.success("Order placed successfully! Thank you for choosing Sweet Waveside SK Shop.")
            st.text_area("Order Summary", summary, height=200)
            
            # Save to file (with UTF-8 encoding)
            with open("customer_orders.txt", "a", encoding="utf-8") as f:
                f.write(summary)
            st.info("Order saved to 'customer_orders.txt' for processing.")
            
            # Send SMS with customer details
            sms_message = f"New Order from Sweet Waveside SK Shop:\n{summary}"
            if send_sms(sms_message):
                st.info("SMS notification sent to your phone!")
            else:
                st.warning("Order saved, but SMS failed—check Twilio setup.")
        else:
            st.error("Please select items and fill in all required details (Name, Phone, Address).")
