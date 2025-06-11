import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.auth.transport.requests import Request
import datetime

# === CONFIGURATION ===
SPREADSHEET_NAME = "DashboardData"

# === AUTH GOOGLE SHEET ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_dict = json.loads(st.secrets["service_account"])
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
gc = gspread.authorize(credentials)
# === LOAD DATA ===
worksheet = gc.open(SPREADSHEET_NAME).sheet1
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# === APP TITLE ===
st.title("🧠 Health & Wellness Dashboard")
st.write("Monitor & Update Your Daily Health Metrics")

# === DATA DISPLAY ===
st.subheader("📊 Current Data")
st.dataframe(df, use_container_width=True)

# === ADD NEW ENTRY ===
st.subheader("➕ Add New Record")
with st.form("new_entry"):
    today = datetime.date.today()
    date = st.date_input("Date", today)
    steps = st.number_input("Steps", min_value=0, step=100)
    calories = st.number_input("Calories", min_value=0)
    water = st.number_input("Water Intake (liters)", min_value=0.0, step=0.1)
    mood = st.selectbox("Mood", ["Excellent", "Good", "Neutral", "Bad", "Terrible"])
    submit = st.form_submit_button("Add Record")

if submit:
    new_row = [str(date), steps, calories, water, mood]
    worksheet.append_row(new_row)
    st.success("New record added!")

# === DATA EDITING ===
st.subheader("✏️ Edit Existing Record")
row_to_edit = st.number_input("Enter Row Number to Edit (starting from 2)", min_value=2, max_value=len(df)+1, step=1)
if st.button("Load Row"):
    row_data = worksheet.row_values(row_to_edit)
    with st.form("edit_entry"):
        edit_date = st.date_input("Date", datetime.datetime.strptime(row_data[0], "%Y-%m-%d").date())
        edit_steps = st.number_input("Steps", value=int(row_data[1]), min_value=0, step=100)
        edit_calories = st.number_input("Calories", value=int(row_data[2]), min_value=0)
        edit_water = st.number_input("Water Intake (liters)", value=float(row_data[3]), min_value=0.0, step=0.1)
        edit_mood = st.selectbox("Mood", ["Excellent", "Good", "Neutral", "Bad", "Terrible"], index=["Excellent", "Good", "Neutral", "Bad", "Terrible"].index(row_data[4]))
        update = st.form_submit_button("Update Record")
    
    if update:
        worksheet.update(f"A{row_to_edit}", [[str(edit_date), edit_steps, edit_calories, edit_water, edit_mood]])
        st.success("Record updated!")

# === SIMPLE VISUALIZATION ===
st.subheader("📈 Visualizations")
chart_option = st.selectbox("Select Chart", ["Steps Over Time", "Calories Over Time", "Water Intake Over Time"])

df["Date"] = pd.to_datetime(df["Date"])

df_sorted = df.sort_values("Date")
if chart_option == "Steps Over Time":
    st.line_chart(df_sorted.set_index("Date")["Steps"])
elif chart_option == "Calories Over Time":
    st.line_chart(df_sorted.set_index("Date")["Calories"])
else:
    st.line_chart(df_sorted.set_index("Date")["Water Intake"])

st.write("\n---\nBuilt with ❤️ using Streamlit + Google Spreadsheet")
