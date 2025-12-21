import streamlit as st
import gspread
import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials
import pytz

tz = pytz.timezone("Asia/Kolkata")  # your timezone
current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
# ---------- CONFIG ----------
SHEET_NAME = "ISKCON_BOOK_INVENTORY"
SHEET_ID = "1GKYhoxUS6XrDlrb6j5KjUzgsnIBUuYPA6Pd64r5EAxc"
# ---------- AUTH ----------
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)
st.text("SHOWING UPDATED CODE")
client = gspread.authorize(creds)
st.write("Secrets loaded:", st.secrets["gcp_service_account"]["client_email"])
# sheet = client.open(SHEET_NAME)
sheet = client.open_by_key(SHEET_ID)
sales_sheet = sheet.worksheet("sales_log")
books_sheet = sheet.worksheet("books_master")

# ---------- LOAD BOOK DATA ----------
books_df = pd.DataFrame(books_sheet.get_all_records())

st.title("📚 ISKCON Book Distribution Tracker")

devotee = st.text_input("Devotee Name")
if devotee.strip()=="":
    devotee="Anonymous"

# ---------- BOOK SEARCH ----------
# book_search = st.text_input("Type Book Name (eg: B, Bh, Bhag)")

filtered_books = books_df["Book Name"].str.lower()

# book_name = st.selectbox(
#     "Select Book",
#     filtered_books["Book Name"].unique()
#     if not filtered_books.empty else []
# )

book_name = st.selectbox(
    "Type Book Name",
    options=filtered_books.unique(),
    index=None,
    placeholder="Start typing (B, Bh, Bha...)"
)

# ---------- LANGUAGE ----------
language = st.selectbox(
    "Language",
    ["English", "Hindi", "Marathi", "Gujarati","Tamil","Kannada","Malayalam"]
)

# ---------- PRICE AUTO ----------
price = None
if book_name:
    price_row = books_df[
        (books_df["Book Name"] == book_name) &
        (books_df["Language"] == language)
    ]
    if not price_row.empty:
        price = price_row.iloc[0]["Price"]

price = st.number_input("Price", value=price if price else 0)

quantity = st.number_input("Quantity Sold", min_value=1, step=1)

payment_type= st.selectbox(
    "Payment Mode",
    ["Cash", "Online"]
)


# ---------- SUBMIT ----------
if st.button("Submit Sale"):
    sales_sheet.append_row([
        current_time,
        book_name,
        language,
        quantity,
        price,
        devotee,
        payment_type
    ])
    st.success("✅ Sale recorded successfully")

