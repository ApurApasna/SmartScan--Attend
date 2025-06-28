# ----------------------------- app.py ---------------------------------
import streamlit as st
import sqlite3, pandas as pd, base64
from datetime import datetime, timedelta
from pathlib import Path
from streamlit_js_eval import streamlit_js_eval

# ---------------------------------------------------------------------
# PAGE CONFIG & CONSTANTS
# ---------------------------------------------------------------------
st.set_page_config(page_title="SmartScan Attend", layout="centered")

ALLOWED_HOSTS = ["192.168.92.127", "localhost"]
ADMIN_CREDENTIALS = {"admin": "admin"}
DB_PATH = "attendance.db"
CLASSLIST_CSV = "classlist.csv"
LOGO_FILE = "logo.png"

# ---------------------------------------------------------------------
# IP VALIDATION
# ---------------------------------------------------------------------
client_host = streamlit_js_eval(js_expressions="window.location.hostname", key="host")
if client_host is None:
    st.stop()

if client_host not in ALLOWED_HOSTS:
    st.error(f"\u274c Access Denied! Your host/IP is `{client_host}`.")
    st.stop()

# ---------------------------------------------------------------------
# HEADER UI
# ---------------------------------------------------------------------
logo_b64 = ""
if Path(LOGO_FILE).exists():
    logo_b64 = base64.b64encode(Path(LOGO_FILE).read_bytes()).decode()

st.markdown(f"""
    <style>
    .header {{
        display: flex;
        align-items: center;
        padding: 1rem;
        background: #e6f0ff;
        border-radius: 10px;
    }}
    .header img {{ height: 60px; margin-right: 1rem; }}
    .title {{ font-weight: 600; color: #004080; }}
    </style>
    <div class="header">
        <img src="data:image/png;base64,{logo_b64}" />
        <div class="title">
            SmartScan Attend<br/>
            A QR-based Smart Attendance System
        </div>
    </div>""", unsafe_allow_html=True)

# ---------------------------------------------------------------------
# DATABASE SETUP
# ---------------------------------------------------------------------
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_number TEXT,
        email TEXT,
        class_name TEXT,
        timestamp TEXT,
        host TEXT,
        status TEXT
    )
""")
conn.commit()

# ---------------------------------------------------------------------
# LOAD STUDENTS CSV
# ---------------------------------------------------------------------
try:
    students = pd.read_csv(CLASSLIST_CSV)
    students.columns = students.columns.str.strip().str.lower().str.replace(" ", "_")
    students = students.rename(columns={"email_id": "email"})
except Exception as e:
    st.error(f"\u26a0\ufe0f Error loading student list: {e}")
    st.stop()

# ---------------------------------------------------------------------
# TIMETABLE SETUP
# ---------------------------------------------------------------------
timetable = {
    "Monday": ["OS", "ALC", "Short Break", "CN", "MEFA", "Lunch Break", "DBMS LAB", "DBMS LAB"],
    "Tuesday": ["ALC", "TALENTIO", "Short Break", "TALENTIO", "TALENTIO", "Lunch Break", "SPORTS", "CN"],
    "Wednesday": ["CN LAB", "CN LAB", "Short Break", "DBMS", "ALC", "Lunch Break", "OS LAB", "OS LAB"],
    "Thursday": ["MEFA", "CN", "Short Break", "ES", "OS", "Lunch Break", "MENTORING", "DBMS"],
    "Friday": ["DBMS", "OS", "Short Break", "MEFA", "ES", "Lunch Break", "TALENTIO", "TALENTIO"],
    "Saturday": ["ALC", "DBMS", "Short Break", "OS", "CN", "Lunch Break", "LIBRARY", "MEFA"]
}
time_slots = [
    "9:00 – 10:00", "10:00 – 11:00", "11:00 – 11:10", "11:10 – 12:10",
    "12:10 – 1:10", "1:10 – 1:40", "1:40 – 2:40", "2:40 – 3:40"
]

# ---------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------
def current_class():
    now = datetime.now()
    h, m = now.hour, now.minute
    day = now.strftime("%A")
    if 9 <= h < 10:
        idx = 0
    elif 10 <= h < 11:
        idx = 1
    elif h == 11 and m < 10:
        return "Break"
    elif 11 <= h < 12:
        idx = 3
    elif 12 <= h < 13:
        idx = 4
    elif h == 13 and m < 40:
        return "Break"
    elif 13 <= h < 14 or (h == 14 and m < 40):
        idx = 6
    elif h == 14 and m >= 40 or h == 15:
        idx = 7
    else:
        return "No Class"
    return timetable.get(day, [""] * 8)[idx]

def already_marked(email):
    lookback = datetime.now() - timedelta(hours=1)
    cur.execute("SELECT 1 FROM attendance WHERE email=? AND timestamp > ?", (email, lookback.isoformat()))
    return cur.fetchone() is not None

def save_attendance(roll, email, cls, host, status):
    cur.execute("""
        INSERT INTO attendance (roll_number, email, class_name, timestamp, host, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (roll, email, cls, datetime.now().isoformat(), host, status))
    conn.commit()

def update_attendance_status(entry_id, new_status):
    cur.execute("UPDATE attendance SET status=? WHERE id=?", (new_status, entry_id))
    conn.commit()

# ---------------------------------------------------------------------
# LOGIN & DASHBOARD
# ---------------------------------------------------------------------
st.sidebar.title("\U0001f512 Login")
user_type = st.sidebar.radio("I am a:", ["Student", "Faculty"])

if user_type == "Student":
    st.subheader("\U0001f4cb Student Attendance")
    roll = st.selectbox("\U0001f393 Select Roll Number", students["roll_number"].unique(), index=None)
    if roll:
        email = students[students["roll_number"] == roll]["email"].values[0]
        cls = current_class()
        st.markdown(f"**Current Class:** {cls}")
        st.markdown(f"**Email ID:** `{email}`")
        if st.button("\u2705 Submit Attendance"):
            if cls in {"Break", "No Class"}:
                st.warning("\u23f3 Attendance not required now.")
            elif already_marked(email):
                st.warning("\u26a0\ufe0f Already marked recently.")
                save_attendance(roll, email, cls, client_host, "duplicate")
            else:
                save_attendance(roll, email, cls, client_host, "present")
                st.success("\u2705 Attendance recorded!")

        with st.expander("\U0001f4c5 Timetable"):
            df_tt = pd.DataFrame(timetable, index=time_slots).T
            st.dataframe(df_tt, use_container_width=True)

        with st.expander("\U0001f4c8 Attendance Percentage"):
            subject_count = {}
            for day in timetable:
                for subj in timetable[day]:
                    if subj not in ["Short Break", "Lunch Break", "Break"]:
                        subject_count[subj] = subject_count.get(subj, 0) + 1
            cur.execute("SELECT class_name, status FROM attendance WHERE email=?", (email,))
            records = cur.fetchall()
            attended = {k: 0 for k in subject_count}
            for cls, status in records:
                if status == "present" and cls in attended:
                    attended[cls] += 1
            percent = [
                {"Subject": s, "Attended": attended[s], "Total": subject_count[s],
                 "%": f"{round(attended[s]/subject_count[s]*100, 2)}%"}
                for s in subject_count
            ]
            st.dataframe(pd.DataFrame(percent))

if user_type == "Faculty":
    st.subheader("\U0001f468\u200d\U0001f3eb Faculty Login")
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if not st.session_state.logged_in:
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if ADMIN_CREDENTIALS.get(user) == pwd:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("\u274c Invalid credentials")
        st.stop()

    tab1, tab2, tab3 = st.tabs(["\U0001f4ca Records", "\u2795 Manual Entry", "\u270f\ufe0f Edit Entry"])

    with tab1:
        df = pd.read_sql("SELECT * FROM attendance ORDER BY timestamp DESC", conn)
        st.dataframe(df, use_container_width=True)
        st.download_button("\U0001f4c5 Download CSV", df.to_csv(index=False), "attendance.csv")

    with tab2:
        roll_m = st.selectbox("\U0001f393 Roll Number", students["roll_number"], key="man_roll")
        class_options = sorted(set(c for v in timetable.values() for c in v if "Break" not in c))
        cls_m = st.selectbox("Class", class_options)
        status = st.selectbox("Status", ["present", "manual", "absent"])
        if st.button("\u2795 Add Entry"):
            email_m = students[students["roll_number"] == roll_m]["email"].values[0]
            save_attendance(roll_m, email_m, cls_m, "FACULTY", status)
            st.success("Added!")

    with tab3:
        df_edit = pd.read_sql("SELECT * FROM attendance ORDER BY timestamp DESC", conn)
        st.dataframe(df_edit, use_container_width=True)
        entry_id = st.number_input("Entry ID", step=1)
        new_status = st.selectbox("New Status", ["present", "manual", "absent", "duplicate"])
        if st.button("\u270f\ufe0f Update"):
            update_attendance_status(entry_id, new_status)
            st.success("Updated!")

# ---------------------------------------------------------------------
# FOOTER
# ---------------------------------------------------------------------
st.write("""
    <div style='text-align:center;color:#888;margin-top:2rem;font-size:0.9rem;'>
    \ud83d\udd52 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/><br/>
    \ud83d\udccd Stanley College of Engineering & Technology for Women, Abids, Hyderabad – 500001
    </div>""", unsafe_allow_html=True)
