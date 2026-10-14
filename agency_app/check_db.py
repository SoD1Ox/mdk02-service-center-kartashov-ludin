import sqlite3

conn = sqlite3.connect("agency.db")

tables = ["users", "attempts", "candidates", "resumes", "skills",
          "resume_skills", "employers", "vacancies", "vacancy_skills",
          "responses", "deals"]

for t in tables:
    count = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"{t}: {count}")

conn.close()