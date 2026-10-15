from src.db.connection import get_connection, DB_PATH


def _get_id(conn, table, where_field, where_value):
    row = conn.execute(
        f"SELECT id FROM {table} WHERE {where_field}=?", (where_value,)
    ).fetchone()
    return row[0] if row else None


def seed_data(db_path=DB_PATH):
    with get_connection(db_path) as conn:

        # --- USERS (5) ---
        for login, pwd, role in [
            ("admin", "admin123", "admin"),
            ("manager", "manager123", "manager"),
            ("director", "director123", "director"),
            ("employer", "employer123", "employer"),
            ("candidate", "candidate123", "candidate"),
        ]:
            conn.execute(
                "INSERT OR IGNORE INTO users (login, password_hash, role) VALUES (?, ?, ?)",
                (login, pwd, role),
            )

        # --- SKILLS (6) ---
        skill_ids = []
        for name, cat in [
            ("Python", "Программирование"),
            ("SQL", "Базы данных"),
            ("PyQt5", "Программирование"),
            ("Аналитика", "Менеджмент"),
            ("Тестирование", "QA"),
            ("Git", "Инструменты"),
        ]:
            skill_ids.append(conn.execute(
                "SELECT id FROM skills WHERE name=?", (name,)
            ).fetchone()[0] if conn.execute(
                "SELECT 1 FROM skills WHERE name=?", (name,)
            ).fetchone() else conn.execute(
                "INSERT INTO skills (name, category) VALUES (?, ?)",
                (name, cat),
            ).lastrowid)

        # --- CANDIDATES (3) ---
        candidate_ids = []
        for name, phone, email in [
            ("Иванов Иван", "+7-900-111-11-11", "candidate@agency.ru"),
            ("Петрова Мария", "+7-900-222-22-22", "petrova@example.com"),
            ("Сидоров Пётр", "+7-900-333-33-33", "sidorov@example.com"),
        ]:
            cur = conn.execute(
                "INSERT OR IGNORE INTO candidates (full_name, phone, email) VALUES (?, ?, ?)",
                (name, phone, email),
            )
            cid = cur.lastrowid
            if not cid:
                cid = _get_id(conn, "candidates", "email", email)
            candidate_ids.append(cid)

        # --- RESUMES (3) ---
        resume_ids = []
        for cid, title, exp, edu in [
            (candidate_ids[0], "Python-разработчик", 3, "МГТУ"),
            (candidate_ids[1], "Аналитик данных", 5, "МГУ"),
            (candidate_ids[2], "Тестировщик ПО", 2, "МТУСИ"),
        ]:
            cur = conn.execute(
                "INSERT INTO resumes (candidate_id, title, experience, education) VALUES (?, ?, ?, ?)",
                (cid, title, exp, edu),
            )
            resume_ids.append(cur.lastrowid)

        # --- EMPLOYERS (3) ---
        employer_ids = []
        for name, inn, contact, phone in [
            ("ООО Ромашка", "7701234567", "employer@romashka.ru", "+7-495-111-11-11"),
            ("АО ТехноСофт", "7709876543", "Белова Н.", "+7-495-222-22-22"),
            ("ИП Смирнов", "7705555555", "Смирнов И.", "+7-495-333-33-33"),
        ]:
            cur = conn.execute(
                "INSERT OR IGNORE INTO employers (name, inn, contact_person, phone) VALUES (?, ?, ?, ?)",
                (name, inn, contact, phone),
            )
            eid = cur.lastrowid
            if not eid:
                eid = _get_id(conn, "employers", "inn", inn)
            employer_ids.append(eid)

        # --- VACANCIES (3) ---
        vacancy_ids = []
        for eid, title, req, salary in [
            (employer_ids[0], "Python-разработчик", "Python, SQL, PyQt5", 150000),
            (employer_ids[1], "Аналитик данных", "SQL, аналитика", 120000),
            (employer_ids[2], "QA-инженер", "тестирование, Git", 100000),
        ]:
            cur = conn.execute(
                "INSERT INTO vacancies (employer_id, title, requirements, salary) VALUES (?, ?, ?, ?)",
                (eid, title, req, salary),
            )
            vacancy_ids.append(cur.lastrowid)

        # --- RESUME_SKILLS ---
        for rid, sid in [
            (resume_ids[0], skill_ids[0]), (resume_ids[0], skill_ids[1]), (resume_ids[0], skill_ids[2]),
            (resume_ids[1], skill_ids[1]), (resume_ids[1], skill_ids[3]),
            (resume_ids[2], skill_ids[4]), (resume_ids[2], skill_ids[5]),
        ]:
            conn.execute(
                "INSERT OR IGNORE INTO resume_skills (resume_id, skill_id) VALUES (?, ?)",
                (rid, sid),
            )

        # --- VACANCY_SKILLS ---
        for vid, sid in [
            (vacancy_ids[0], skill_ids[0]), (vacancy_ids[0], skill_ids[1]), (vacancy_ids[0], skill_ids[2]),
            (vacancy_ids[1], skill_ids[1]), (vacancy_ids[1], skill_ids[3]),
            (vacancy_ids[2], skill_ids[4]), (vacancy_ids[2], skill_ids[5]),
        ]:
            conn.execute(
                "INSERT OR IGNORE INTO vacancy_skills (vacancy_id, skill_id) VALUES (?, ?)",
                (vid, sid),
            )

        # --- RESPONSES (3) ---
        response_ids = []
        for cid, vid, status in [
            (candidate_ids[0], vacancy_ids[0], "На рассмотрении"),
            (candidate_ids[1], vacancy_ids[1], "Собеседование"),
            (candidate_ids[2], vacancy_ids[2], "Трудоустроен"),
        ]:
            cur = conn.execute(
                "INSERT OR IGNORE INTO responses (candidate_id, vacancy_id, status) VALUES (?, ?, ?)",
                (cid, vid, status),
            )
            rid = cur.lastrowid
            if not rid:
                row = conn.execute(
                    "SELECT id FROM responses WHERE candidate_id=? AND vacancy_id=?",
                    (cid, vid),
                ).fetchone()
                rid = row[0] if row else None
            response_ids.append(rid)

        # --- DEALS (3) ---
        for rid, comm, tax in [
            (response_ids[0], 10000, 1300),
            (response_ids[1], 8000, 1040),
            (response_ids[2], 5000, 650),
        ]:
            if rid is None:
                continue
            # проверяем, что отклик существует
            exists = conn.execute(
                "SELECT 1 FROM responses WHERE id=?", (rid,)
            ).fetchone()
            if not exists:
                continue
            conn.execute(
                "INSERT OR IGNORE INTO deals (response_id, commission, tax) VALUES (?, ?, ?)",
                (rid, comm, tax),
            )

        # --- ATTEMPTS (3) ---
        for login, success in [
            ("admin", 1),
            ("manager", 1),
            ("admin", 0),
        ]:
            conn.execute(
                "INSERT INTO attempts (login, success) VALUES (?, ?)",
                (login, success),
            )