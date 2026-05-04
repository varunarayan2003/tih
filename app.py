import streamlit as st
import sqlite3
import pandas as pd
import os

DB_NAME = "student_portal.db"

# -----------------------------
# DATABASE CONNECTION
# -----------------------------
def get_conn():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

# -----------------------------
# CREATE TABLES
# -----------------------------
def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        usn TEXT PRIMARY KEY,
        name TEXT,
        branch TEXT,
        semester INTEGER,
        section TEXT,
        email TEXT,
        phone TEXT,
        password TEXT,
        photo TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS marks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usn TEXT,
        semester INTEGER,
        subject_code TEXT,
        subject_name TEXT,
        internal INTEGER,
        external INTEGER,
        total INTEGER,
        grade TEXT,
        result TEXT
    );
    """)

    conn.commit()
    conn.close()

# -----------------------------
# GRADE FUNCTION
# -----------------------------
def calculate_grade(total):
    if total >= 90: return "S"
    elif total >= 80: return "A"
    elif total >= 70: return "B"
    elif total >= 60: return "C"
    elif total >= 50: return "D"
    else: return "F"

# -----------------------------
# INSERT YOUR DATA
# -----------------------------
def seed_data():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM students WHERE usn=?", ("506EC21028",))
    if cur.fetchone():
        conn.close()
        return

    # STUDENT
    cur.execute("""
    INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "506EC21028",
        "BALAJI K N",
        "ECE",
        6,
        "A",
        "balaji@example.com",
        "9876543210",
        "1234",
        "profile.png"
    ))

    data = [

    # SEM 1
    (1,"21EC01M","Engineering Maths I",20,65),
    (1,"21EC01T","Applied Science",19,80),
    (1,"21EC01T","Basic Electrical & Electronics",15,50),
    (1,"21EC01P","Applied Science Lab",20,40),
    (1,"21EC01P","BEEE Lab",19,30),
    (1,"21EC01P","Computer Concepts Lab",22,30),

    # SEM 2
    (2,"21EC02M","Engineering Maths II",23,75),
    (2,"21EC02E","Communication English",20,84),
    (2,"21EC02T","Semiconductor Devices",19,55),
    (2,"21EC02P","Semiconductor Lab",22,43),
    (2,"21EC02P","Digital Electronics Lab",19,35),
    (2,"21EC12P","Maths Simulation Lab",22,36),

    # SEM 3
    (3,"21EC31T","Analog Circuits",23,95),
    (3,"21EC32T","Digital Electronics",19,55),
    (3,"21EC33T","EMI",20,78),
    (3,"21EC34T","Analog Communication",23,74),
    (3,"21EC35P","Analog Lab",21,44),
    (3,"21EC36P","Digital Lab",19,35),
    (3,"21EC37P","C Lab",22,46),

    # SEM 4
    (4,"21EC41T","Microcontroller",18,75),
    (4,"21EC42T","Digital Communication",18,75),
    (4,"21EC43T","Data Communication",19,77),
    (4,"21EC44T","Professional Ethics",22,83),
    (4,"21EC45P","DC Lab",23,46),
    (4,"21EC46P","Practice Lab",24,48),
    (4,"21EC47P","Microcontroller Lab",24,48),

    # SEM 5
    (5,"21EC51T","Entrepreneurship",21,81),
    (5,"21EC52T","ARM Controller",22,65),
    (5,"21EC53T","AD Communication",19,74),
    (5,"21EC54T","Applications of ECE",24,84),
    (5,"21EC55P","Applications Lab",23,41),
    (5,"21EC56P","PCB Lab",21,45),
    (5,"21EC57P","Electrical Servicing",22,40),

    # SEM 6
    (6,"15CS61T","Industrial Automation",24,96),
    (6,"15CS62T","Embedded Systems",24,69),
    (6,"15CS63T","Medical Electronics",20,77),
    (6,"15CS64P","Automation Lab",17,41),
    (6,"15CS65P","Verilog Lab",21,40),
    (6,"15CS66P","Project Work",22,35),
    ]

    for sem, code, name, internal, external in data:
        total = internal + external
        grade = calculate_grade(total)
        result = "PASS" if total >= 40 else "FAIL"

        cur.execute("""
        INSERT INTO marks VALUES (NULL,?,?,?,?,?,?,?,?,?)
        """, (
            "506EC21028",
            sem,
            code,
            name,
            internal,
            external,
            total,
            grade,
            result
        ))

    conn.commit()
    conn.close()

# -----------------------------
# LOGIN PAGE
# -----------------------------
def login():
    st.title("🎓 Student Login")

    usn = st.text_input("USN")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("SELECT * FROM students WHERE usn=? AND password=?", (usn, password))
        user = cur.fetchone()
        conn.close()

        if user:
            st.session_state["usn"] = usn
            st.rerun()
        else:
            st.error("Invalid USN or Password")

# -----------------------------
# DASHBOARD
# -----------------------------
def dashboard():
    usn = st.session_state["usn"]
    conn = get_conn()

    student = pd.read_sql("SELECT * FROM students WHERE usn=?", conn, params=(usn,))
    marks = pd.read_sql("SELECT * FROM marks WHERE usn=?", conn, params=(usn,))
    conn.close()

    st.title("🎓 Student Dashboard")

    # PROFILE SECTION
    col1, col2 = st.columns([1,3])

    with col1:
        if os.path.exists("profile.png"):
            st.image("profile.png", width=150)

    with col2:
        st.subheader(student.loc[0, "name"])
        st.write("USN:", usn)
        st.write("Branch:", student.loc[0, "branch"])

    st.markdown("---")

    # SEMESTER DROPDOWN
    semesters = sorted(marks["semester"].unique())
    selected_sem = st.selectbox("📚 Select Semester", semesters)

    sem_data = marks[marks["semester"] == selected_sem]

    st.dataframe(
        sem_data[["subject_code","subject_name","internal","external","total","grade","result"]],
        use_container_width=True
    )

    # RESULTS
    sgpa = round(sem_data["total"].mean() / 10, 2)
    cgpa = round(marks["total"].mean() / 10, 2)

    st.success(f"📊 SGPA: {sgpa}")
    st.success(f"🎯 CGPA: {cgpa}")

    if st.button("Logout"):
        del st.session_state["usn"]
        st.rerun()

# -----------------------------
# MAIN
# -----------------------------
init_db()
seed_data()

if "usn" not in st.session_state:
    login()
else:
    dashboard()