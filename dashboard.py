import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# === Google Sheets API Auth ===
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("help-desk-ticket-system-68cdc2847e50.json", scope)
client = gspread.authorize(creds)

# === Load Data from Google Sheet ===
sheet = client.open("IT Help Desk Ticket Form (Responses)").sheet1
data = sheet.get_all_records()
df = pd.DataFrame(data)

# === Streamlit Dashboard UI ===
st.title("🎫 IT Help Desk Ticket Dashboard")

# 🔍 Search Bar
search_query = st.text_input("Search tickets by Name, Email, or Ticket ID")
if search_query:
    df = df[df.apply(
        lambda row: search_query.lower() in str(row["Full Name"]).lower()
        or search_query.lower() in str(row["Email address"]).lower()
        or search_query.lower() in str(row["Ticket ID"]).lower(),
        axis=1
    )]

# 🎛️ Filter by Status
status_filter = st.selectbox("Filter by Status", ["All"] + sorted(df["Status"].unique()))
if status_filter != "All":
    df = df[df["Status"] == status_filter]

# 🔽 Optional: Sort by Urgency
if "Urgency Level" in df.columns:
    sort_urgency = st.checkbox("Sort by Urgency Level (High → Low)")
    if sort_urgency:
        urgency_order = {"High": 1, "Medium": 2, "Low": 3}
        df["Urgency Sort"] = df["Urgency Level"].map(urgency_order)
        df = df.sort_values(by="Urgency Sort")

# 📋 Show Ticket Table
st.dataframe(df)

# 📊 Status Summary
st.markdown("### Ticket Summary")
st.write(df["Status"].value_counts())

# 📥 Export Section
st.markdown("---")
st.subheader("Download Tickets")
st.download_button(
    label="⬇️ Download filtered tickets as CSV",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="tickets_export.csv",
    mime="text/csv"
)
