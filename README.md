# SmartScan Attend: QR-Based Smart Attendance System

**Developed by:** Apur Apasna & Aryani Arige  
**Institution:** Stanley College of Engineering and Technology for Women

---

## 🧠 Project Overview

**SmartScan Attend** is an intelligent QR-based attendance system built to streamline classroom attendance for faculty and students. Instead of shouting names and updating registers manually, faculty can now allow students to mark attendance themselves by scanning a QR — all within the campus network and in a single click.

---

## 🎯 Problem Statement

Traditional attendance methods waste time and energy. Faculty have to call out each student's name, mark presence manually, and update it later in internal systems. This is inefficient, especially in large classrooms.

---

## 💡 Solution Highlights

✅ A QR is placed in the classroom.  
✅ Students scan it to open the attendance system (Streamlit web app).  
✅ The system verifies that the request comes from the college IP (for anti-proxy).  
✅ Only one attendance per hour is allowed.  
✅ Faculty can also view, edit, and add entries manually if needed.

---

## 🧰 Tech Stack

- **Frontend:** Streamlit (Python)
- **Backend:** SQLite3 Database
- **IP Restriction:** Verified using external IP fetch
- **CSV Uploads:** Student list input
- **QR Code Access:** Restricted to specific campus IP

---

## 📅 Features

- Student & Faculty login portals  
- Live class detection based on real-time clock  
- Subject-wise attendance summary  
- Upcoming class view  
- Weekly timetable with current class highlight  
- Manual entry and editing by faculty  
- Download attendance reports as CSV  
- Smart filtering and duplicate prevention  
- Leaderboard, calendar, and future-ready dashboard (in progress)

---



---

## 🔐 Access Policy

- Students can mark attendance only from campus Wi-Fi IP (`192.168.0.103`)  
- Prevents proxy or fake submissions  
- Faculty can override/add/edit records when needed

---

---

## 📌 Future Improvements

- Add face detection for student validation  
- Real-time visual dashboard with charts  
- Cloud-based backup and analytics  
- SMS/email alert integration for attendance drops

---

## 🙏 Acknowledgements

This project was submitted for the **Digital Mavericks 2025** contest under the domain of **Education Technology** and **Smart Campus Automation**.



