IT Help Desk Ticketing System Simulation



Overview

This project simulates an IT Help Desk ticketing workflow using Google Forms, Google Sheets, Python, and Streamlit. 

It demonstrates how tickets can be automatically created, processed, and visualized in a real-world IT support environment.



Workflow

1\. A user submits an IT issue through a Google Form.

2\. The responses are stored in a linked Google Sheet.

3\. The Python script (read\_tickets.py) processes new tickets:

&nbsp;  - Assigns a unique Ticket ID

&nbsp;  - Blocks duplicate/unresolved tickets

&nbsp;  - Sends confirmation emails

&nbsp;  - Tracks ticket status and sends updates

&nbsp;  - Auto-closes tickets after 24 hours if marked Resolved

4\. The Streamlit dashboard (dashboard.py) allows IT staff to:

&nbsp;  - Search tickets by name, email, or ID

&nbsp;  - Filter by ticket status

&nbsp;  - Sort by urgency

&nbsp;  - View ticket summary statistics

&nbsp;  - Export filtered tickets as CSV



Features

\- Automatic ticket ID generation

\- Blocks duplicate/unresolved tickets

\- Email confirmations, updates, and closure notices

\- Auto-close policy after 24 hours if Resolved

\- Interactive Streamlit dashboard for ticket management



Setup Instructions

1\. Clone this repository:

&nbsp;  git clone https://github.com/sayedtushar123/Help-desk-ticket-system

&nbsp;  cd help-desk-ticket-system



2\. Create a virtual environment (recommended):

&nbsp;  python -m venv venv

&nbsp;  venv\\Scripts\\activate   (Windows)

&nbsp;  source venv/bin/activate   (Linux/Mac)



3\. Install dependencies:

&nbsp;  pip install -r requirements.txt



4\. Add your Google Service Account JSON file in the project directory.

&nbsp;  Name it exactly: help-desk-ticket-system-68cdc2847e50.json



5\. Configure email settings inside read\_tickets.py:

&nbsp;  Replace EMAIL\_ADDRESS with your Gmail address

&nbsp;  Replace EMAIL\_PASSWORD with your Gmail App Password



Usage

\- Step 1: Submit a new ticket using the Google Form linked to Sheet.

\- Step 2: Run the ticket processor to assign IDs and send notifications:

&nbsp; python read\_tickets.py

\- Step 3: Launch the dashboard to view and manage tickets:

&nbsp; streamlit run dashboard.py



Notes

\- The project uses a Google Form linked to a Google Sheet for ticket intake.

\- Sensitive credentials (Google JSON, Gmail password) must be kept private and not shared publicly.

\- For real-world deployment, environment variables should be used instead of hardcoding credentials.





