"""Отклики соискателей на вакансии.

Роли:
- manager/admin — видят все отклики, меняют статусы;
- employer («Отклики») — видит только отклики на СВОИ вакансии и
  двигает их статусы (BR-02: каждое изменение — в историю);
- candidate («Мои отклики») — видит только свои отклики и может
  отозвать его (статус «Отозван» / удаление).
"""
from PyQt5.QtWidgets import QMessageBox

from src.db.repositories import response_repo, vacancy_repo, user_repo
from src.ui.sections.base_crud import CrudSection


class ResponsesSection(CrudSection):
    section_key = "responses"
    entity_type = "response"
    icon_name = "mail"
    title = "Отклики"
    subtitle = "Отклики соискателей на вакансии"
    columns = ["id", "Соискатель", "Вакансия", "Статус"]
    fields = [
        ("candidate_id", "Соискатель", "combo"),
        ("vacancy_id", "Вакансия", "combo"),
        ("status", "Статус", "combo"),
    ]

    def __init__(self, role="manager", login="", parent=None):
        self._my_candidate_id = None
        self._my_employer_id = None
        if role == "candidate":
            self.title = "Мои отклики"
            self.subtitle = "Ваши отклики и их статусы (обновляются менеджером/работодателем)"
            self._my_candidate_id = user_repo.get_candidate_id_by_login(login)
        if role == "employer":
            self._my_employer_id = user_repo.get_employer_id_by_name(login)
            self.subtitle = "Отклики соискателей на ваши вакансии"
        super().__init__(role=role, login=login, parent=parent)

    # ---------- данные с учётом роли ----------
    def fetch(self):
        rows = response_repo.get_all()
        if self.role == "candidate":
            if self._my_candidate_id is not None:
                rows = [r for r in rows if r["candidate_id"] == self._my_candidate_id]
        elif self.role == "employer" and self._my_employer_id is not None:
            my_vac = {v["id"] for v in vacancy_repo.get_all()
                      if v["employer_id"] == self._my_employer_id}
            rows = [r for r in rows if r["vacancy_id"] in my_vac]
        return rows

    def _candidates_options(self):
        from src.db.repositories import candidate_repo
        return [f"{c['id']} — {c['full_name']}" for c in candidate_repo.get_all()]

    def _vacancies_options(self):
        rows = vacancy_repo.get_all()
        if self.role == "employer" and self._my_employer_id is not None:
            rows = [v for v in rows if v["employer_id"] == self._my_employer_id]
        return [f"{v['id']} — {v['title']} ({v.get('employer_name') or ''})"
                for v in rows]

    def field_options(self, name):
        if name == "status":
            from src.business_rules import STATUSES_RESPONSE
            if self.role == "candidate":
                # соискатель может только отозвать свой отклик
                return ["Отозван"]
            return STATUSES_RESPONSE
        if name == "candidate_id":
            if self.role in ("candidate", "employer"):
                return []  # поле только для чтения, заполняется автоматически
            return self._candidates_options()
        if name == "vacancy_id":
            if self.role == "candidate":
                return []
            return self._vacancies_options()
        return []

    @staticmethod
    def _parse_id(text):
        """Из строки '12 — Иванов И.И.' достать числовой id."""
        t = text.strip()
        num = ""
        for ch in t:
            if ch.isdigit():
                num += ch
            else:
                break
        return int(num) if num else None

    def to_row(self, r):
        return [r["id"], r.get("candidate_name"), r.get("vacancy_title"), r["status"]]

    def fill_form_from_row(self, row):
        super().fill_form_from_row(row)
        if self.current_id is None:
            return
        for r in self.fetch():
            if r["id"] == self.current_id:
                self.set_values({
                    "candidate_id": f"{r.get('candidate_id')} — {r.get('candidate_name') or ''}".strip(),
                    "vacancy_id": f"{r.get('vacancy_id')} — {r.get('vacancy_title') or ''}".strip(),
                    "status": r.get("status"),
                })
                break

    # ---------- CRUD ----------
    def do_create(self):
        cid = self._my_candidate_id if self.role == "candidate" \
            else self._parse_id(self.value("candidate_id"))
        vid = self._parse_id(self.value("vacancy_id"))
        if cid is None or vid is None:
            raise ValueError("Выберите соискателя и вакансию из списка")
        response_repo.create(cid, vid, self.value("status") or "На рассмотрении",
                             user_login=self.login, user_role=self.role)

    def do_update(self):
        cid = self._my_candidate_id if self.role == "candidate" \
            else self._parse_id(self.value("candidate_id"))
        vid = self._parse_id(self.value("vacancy_id"))
        if cid is None or vid is None:
            raise ValueError("Выберите соискателя и вакансию из списка")
        response_repo.update(self.current_id, cid, vid,
                             self.value("status") or "На рассмотрении",
                             user_login=self.login, user_role=self.role)

    def do_delete(self):
        if self.role == "candidate":
            # соискатель не удаляет запись, а отзывает отклик
            r = next((x for x in self.fetch() if x["id"] == self.current_id), None)
            if r:
                response_repo.update(self.current_id, r["candidate_id"],
                                     r["vacancy_id"], "Отозван",
                                     user_login=self.login, user_role=self.role)
                QMessageBox.information(self, "Отозвано",
                                        "Отклик отмечен как «Отозван».")
                self.load_data()
            return
        response_repo.delete(self.current_id, user_login=self.login, user_role=self.role)
