"""Резюме соискателей.

Для соискателя раздел называется «Моё резюме» и показывает только его
резюме; кандидат подставляется автоматически по логину.
"""
from src.db.repositories import resume_repo, candidate_repo, user_repo
from src.ui.sections.base_crud import CrudSection


class ResumesSection(CrudSection):
    section_key = "resumes"
    entity_type = "resume"
    icon_name = "doc"
    title = "Резюме"
    subtitle = "Резюме соискателей"
    columns = ["id", "Соискатель", "Должность", "Опыт", "Образование"]
    fields = [
        ("candidate_id", "Соискатель", "combo"),
        ("title", "Должность"),
        ("experience", "Опыт (лет)"),
        ("education", "Образование"),
    ]

    def __init__(self, role="manager", login="", parent=None):
        self._my_candidate_id = None
        if role == "candidate":
            self.title = "Моё резюме"
            self.subtitle = "Ваши резюме — видят только менеджеры агентства"
            self._my_candidate_id = user_repo.get_candidate_id_by_login(login)
        super().__init__(role=role, login=login, parent=parent)
        if role == "candidate" and self._my_candidate_id is not None:
            from src.db.repositories import candidate_repo
            me = next((c for c in candidate_repo.get_all()
                       if c["id"] == self._my_candidate_id), None)
            if me:
                self.set_values({"candidate_id": f"{me['id']} — {me['full_name']}"})

    def fetch(self):
        rows = resume_repo.get_all()
        if self.role == "candidate":
            if self._my_candidate_id is not None:
                rows = [r for r in rows
                        if r["candidate_id"] == self._my_candidate_id]
        return rows

    def field_options(self, name):
        if name == "candidate_id":
            if self.role == "candidate":
                return []  # только для чтения
            return [f"{c['id']} — {c['full_name']}" for c in candidate_repo.get_all()]
        return []

    @staticmethod
    def _parse_id(text):
        num = ""
        for ch in text.strip():
            if ch.isdigit():
                num += ch
            else:
                break
        return int(num) if num else None

    def to_row(self, r):
        return [r["id"], r.get("candidate_name"), r["title"],
                r["experience"], r["education"]]

    def fill_form_from_row(self, row):
        super().fill_form_from_row(row)
        if self.current_id is None:
            return
        for r in self.fetch():
            if r["id"] == self.current_id:
                self.set_values({
                    "candidate_id": f"{r.get('candidate_id')} — {r.get('candidate_name') or ''}".strip(),
                    "title": r.get("title"),
                    "experience": r.get("experience"),
                    "education": r.get("education"),
                })
                break

    def _candidate_id(self):
        if self.role == "candidate":
            if self._my_candidate_id is None:
                raise ValueError(
                    f"Для логина «{self.login}» нет карточки кандидата "
                    "(email должен начинаться с логина)")
            return self._my_candidate_id
        cid = self._parse_id(self.value("candidate_id"))
        if cid is None:
            raise ValueError("Выберите соискателя из списка")
        return cid

    def do_create(self):
        resume_repo.create(
            self._candidate_id(), self.value("title"),
            int(self.value("experience") or 0), self.value("education"),
            user_login=self.login, user_role=self.role,
        )

    def do_update(self):
        resume_repo.update(
            self.current_id, self._candidate_id(), self.value("title"),
            int(self.value("experience") or 0), self.value("education"),
            user_login=self.login, user_role=self.role,
        )

    def do_delete(self):
        resume_repo.delete(self.current_id, user_login=self.login, user_role=self.role)
