"""Вакансии.

Для работодателя — «Мои вакансии»: показывает только его компании,
ID работодателя подставляется автоматически (логическая связь:
логин работодателя входит в название его компании).

Для соискателя — кнопка «Откликнуться»: отклик создаётся на выбранную
вакансию от имени его карточки кандидата (email вида login@...).
"""
from PyQt5.QtWidgets import QMessageBox

from src.db.repositories import vacancy_repo, response_repo, user_repo
from src.ui.sections.base_crud import CrudSection


class VacanciesSection(CrudSection):
    section_key = "vacancies"
    entity_type = "vacancy"
    icon_name = "briefcase"
    title = "Вакансии"
    subtitle = "Открытые позиции работодателей"
    columns = ["id", "Работодатель", "Должность", "Требования", "Зарплата", "Статус"]
    fields = [
        ("employer_id", "Работодатель (id)"),
        ("title", "Должность"),
        ("requirements", "Требования"),
        ("salary", "Зарплата (₽)"),
        ("status", "Статус", "combo"),
    ]

    def __init__(self, role="manager", login="", parent=None):
        self._my_employer_id = None
        if role == "employer":
            self._my_employer_id = user_repo.get_employer_id_by_name(login)
            self.title = "Мои вакансии"
            self.subtitle = "Вакансии вашей компании"
        if role == "candidate":
            self.action_button_text = "Откликнуться на выбранную вакансию"
            self.action_button_icon = "send"
            self.readonly_message = (
                "Выберите вакансию и нажмите «Откликнуться» — "
                "отклик появится в разделе «Мои отклики»")
        super().__init__(role=role, login=login, parent=parent)
        if role == "employer" and self._my_employer_id is not None:
            from src.db.repositories import employer_repo
            me = next((e for e in employer_repo.get_all()
                       if e["id"] == self._my_employer_id), None)
            if me:
                self.set_values({"employer_id": f"{me['id']} — {me['name']}"})

    # ---------- данные с учётом роли ----------
    def fetch(self):
        rows = vacancy_repo.get_all()
        if self.role == "employer" and self._my_employer_id is not None:
            rows = [r for r in rows if r["employer_id"] == self._my_employer_id]
        return rows

    def field_options(self, name):
        if name == "status":
            from src.business_rules import STATUSES_VACANCY
            return STATUSES_VACANCY
        return []

    def to_row(self, r):
        return [r["id"], r.get("employer_name"), r["title"],
                r["requirements"], r["salary"], r["status"]]

    def fill_form_from_row(self, row):
        super().fill_form_from_row(row)
        if self.current_id is None:
            return
        for r in self.fetch():
            if r["id"] == self.current_id:
                self.set_values({
                    "employer_id": r.get("employer_id"),
                    "title": r.get("title"),
                    "requirements": r.get("requirements"),
                    "salary": r.get("salary"),
                    "status": r.get("status"),
                })
                break

    # ---------- CRUD ----------
    def do_create(self):
        if self.role == "employer" and self._my_employer_id is not None:
            emp_id = self._my_employer_id       # своя компания — без ручного ввода
        else:
            emp_id = self._parse_num(self.value("employer_id"))
        if emp_id is None:
            raise ValueError("Укажите работодателя (id)")
        vacancy_repo.create(
            int(emp_id), self.value("title"),
            self.value("requirements"), int(self.value("salary") or 0),
            user_login=self.login, user_role=self.role,
        )

    @staticmethod
    def _parse_num(text):
        num = ""
        for ch in text.strip():
            if ch.isdigit():
                num += ch
            else:
                break
        return int(num) if num else None

    def do_update(self):
        emp_id = self._my_employer_id if (self.role == "employer"
                                          and self._my_employer_id is not None)             else self._parse_num(self.value("employer_id"))
        if emp_id is None:
            raise ValueError("Укажите работодателя (id)")
        vacancy_repo.update(
            self.current_id,
            int(emp_id), self.value("title"),
            self.value("requirements"), int(self.value("salary") or 0),
            self.value("status") or "Открыта",
            user_login=self.login, user_role=self.role,
        )

    def do_delete(self):
        vacancy_repo.delete(self.current_id, user_login=self.login, user_role=self.role)

    # ---------- отклик соискателя ----------
    def on_action_button(self):
        if self.current_id is None:
            QMessageBox.information(
                self, "Выбор не сделан",
                "Сначала выберите вакансию в таблице, "
                "затем нажмите «Откликнуться».")
            return
        cid = user_repo.get_candidate_id_by_login(self.login)
        if cid is None:
            QMessageBox.warning(
                self, "Нет карточки кандидата",
                f"Для логина «{self.login}» не найдена карточка соискателя "
                "(email должен начинаться с логина). Обратитесь к менеджеру агентства.")
            return
        vac = next((r for r in self.fetch() if r["id"] == self.current_id), None)
        try:
            response_repo.create(
                cid, self.current_id, "На рассмотрении",
                user_login=self.login, user_role=self.role,
            )
        except Exception as e:
            if "UNIQUE" in str(e).upper():
                QMessageBox.warning(
                    self, "Уже откликнуты",
                    "Вы уже откликались на эту вакансию — смотрите раздел «Мои отклики».")
                return
            QMessageBox.critical(self, "Ошибка", str(e))
            return
        QMessageBox.information(
            self, "Отправлено",
            f"Отклик отправлен на вакансию "
            f"«{vac['title'] if vac else self.current_id}». "
            "Статус отклика виден в разделе «Мои отклики».")
        self.clear_form()
