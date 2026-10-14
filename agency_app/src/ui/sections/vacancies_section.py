from src.db.repositories import vacancy_repo
from src.ui.sections.base_crud import CrudSection


class VacanciesSection(CrudSection):
    section_key = "vacancies"
    entity_type = "vacancy"
    title = "Вакансии"
    subtitle = "Открытые позиции работодателей"
    columns = ["id", "Работодатель", "Должность", "Требования", "Зарплата", "Статус"]
    fields = [
        ("employer_id", "ID работодателя"),
        ("title", "Должность"),
        ("requirements", "Требования"),
        ("salary", "Зарплата (₽)"),
        ("status", "Статус"),
    ]

    def fetch(self):
        return vacancy_repo.get_all()

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

    def do_create(self):
        vacancy_repo.create(
            int(self.value("employer_id")), self.value("title"),
            self.value("requirements"), int(self.value("salary") or 0),
            user_login=self.login, user_role=self.role,
        )

    def do_update(self):
        vacancy_repo.update(
            self.current_id,
            int(self.value("employer_id")), self.value("title"),
            self.value("requirements"), int(self.value("salary") or 0),
            self.value("status") or "Открыта",
            user_login=self.login, user_role=self.role,
        )

    def do_delete(self):
        vacancy_repo.delete(self.current_id, user_login=self.login, user_role=self.role)
