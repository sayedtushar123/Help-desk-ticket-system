import gspread
from oauth2client.service_account import ServiceAccountCredentials
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

EMAIL_ADDRESS = "example@gmail.com"
EMAIL_PASSWORD = "hfjdskjfbhdjskjc"

# === Google Sheets Auth ===
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("help-desk-ticket-system-68cdc2847e50.json", scope)
client = gspread.authorize(creds)

sheet = client.open("IT Help Desk Ticket Form (Responses)").sheet1
data = sheet.get_all_values()
headers = data[0]

try:
    ticket_id_col = headers.index("Ticket ID") + 1
    status_col = headers.index("Status") + 1
    last_notified_col = headers.index("Last Notified Status") + 1
except ValueError as e:
    print(f"[Error] Missing expected column: {e}")
    exit()

now = datetime.now()

# === Blocked Tickets Sheet ===
try:
    blocked_sheet = client.open("IT Help Desk Ticket Form (Responses)").worksheet("Blocked Tickets")
except:
    spreadsheet = client.open("IT Help Desk Ticket Form (Responses)")
    spreadsheet.add_worksheet(title="Blocked Tickets", rows="1000", cols="20")
    blocked_sheet = spreadsheet.worksheet("Blocked Tickets")
    blocked_sheet.append_row(headers)

# === Process Tickets from Bottom Up ===
for i in reversed(range(1, len(data))):
    row_number = i + 1
    row = data[i]

    timestamp_str = row[0].strip()
    email = row[1].strip()
    name = row[2].strip()
    issue_type = row[3].strip()
    description = row[4].strip()
    urgency = row[5].strip()
    ticket_id = row[ticket_id_col - 1].strip() if len(row) > ticket_id_col - 1 else ""
    status = row[status_col - 1].strip() if len(row) > status_col - 1 else ""
    last_status = row[last_notified_col - 1].strip() if len(row) > last_notified_col - 1 else ""

    # === Check latest older ticket for same email ===
    if not ticket_id:
        latest_old_ts = None
        latest_old_status = None

        for j in range(1, i):  # Only look at earlier rows
            row_j = data[j]
            email_j = row_j[1].strip()
            status_j = row_j[status_col - 1].strip() if len(row_j) > status_col - 1 else ""
            ts_str_j = row_j[0].strip()
            try:
                ts_j = datetime.strptime(ts_str_j, "%d/%m/%Y %H:%M:%S")
            except:
                continue

            if email_j.lower() == email.lower():
                if latest_old_ts is None or ts_j > latest_old_ts:
                    latest_old_ts = ts_j
                    latest_old_status = status_j

        if latest_old_status and latest_old_status not in ["Closed", "Resolved"]:
            print(f"[Blocked] Row {row_number}: {email} has unresolved ticket — logging & deleting.")
            blocked_sheet.append_row(row)
            sheet.delete_rows(row_number)
            continue

    # === Assign Ticket ID ===
    if not ticket_id:
        ticket_id = f"TKT-{i:04d}"
        sheet.update_cell(row_number, ticket_id_col, ticket_id)
        print(f"[OK] Ticket ID assigned: {ticket_id}")

    # === Set status ===
    if not status:
        status = "Open"
        sheet.update_cell(row_number, status_col, status)

    # === Confirmation Email ===
    if last_status == "":
        subject = f"Your Ticket ID: {ticket_id}"
        body = f"""
Hello {name},

Your support ticket has been received.

Issue Type: {issue_type}
Description: {description}
Urgency Level: {urgency}
Ticket ID: {ticket_id}

Regards,  
IT Help Desk
"""
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, email, msg.as_string())
            server.quit()
            sheet.update_cell(row_number, last_notified_col, status)
            print(f"[Email] Confirmation sent to {email}")
        except Exception as e:
            print(f"[Error] Email failed: {e}")

    # === Auto-Close After 24 Hours ===
    if status == "Resolved":
        try:
            ticket_time = datetime.strptime(timestamp_str, "%d/%m/%Y %H:%M:%S")
            if now - ticket_time > timedelta(hours=24):
                sheet.update_cell(row_number, status_col, "Closed")
                status = "Closed"
                print(f"[Auto-Close] Ticket {ticket_id} marked Closed (Resolved > 24h)")

                subject = f"Your Ticket {ticket_id} Has Been Closed"
                body = f"""
Hello {name},

We have closed your ticket as it was marked Resolved more than 24 hours ago.

Ticket ID: {ticket_id}
Final Status: Closed

Thank you,  
IT Help Desk
"""
                msg = MIMEMultipart()
                msg["From"] = EMAIL_ADDRESS
                msg["To"] = email
                msg["Subject"] = subject
                msg.attach(MIMEText(body, "plain"))

                try:
                    server = smtplib.SMTP("smtp.gmail.com", 587)
                    server.starttls()
                    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                    server.sendmail(EMAIL_ADDRESS, email, msg.as_string())
                    server.quit()
                    sheet.update_cell(row_number, last_notified_col, "Closed")
                except Exception as e:
                    print(f"[Error] Closure email failed: {e}")
        except Exception as e:
            print(f"[Warning] Timestamp issue on row {row_number}: {e}")

    # === Follow-Up Email on Status Change ===
    if last_status and status != last_status:
        subject = f"Update on Your Ticket {ticket_id}"
        body = f"""
Hello {name},

There has been an update on your ticket.

Ticket ID: {ticket_id}
New Status: {status}

Thank you,  
IT Help Desk
"""
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, email, msg.as_string())
            server.quit()
            sheet.update_cell(row_number, last_notified_col, status)
            print(f"[Follow-Up] Sent to {email}")
        except Exception as e:
            print(f"[Error] Follow-up email failed: {e}")
