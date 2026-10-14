from src.db.repositories import response_repo
from src.ui.sections.base_crud import CrudSection


class ResponsesSection(CrudSection):
    section_key = "responses"
    entity_type = "response"
    title = "Отклики"
    subtitle = "Отклики соискателей на вакансии"
    columns = ["id", "Соискатель", "Вакансия", "Статус"]
    fields = [
        ("candidate_id", "ID соискателя"),
        ("vacancy_id", "ID вакансии"),
        ("status", "Статус"),
    ]

    def fetch(self):
        return response_repo.get_all()

    def to_row(self, r):
        return [r["id"], r.get("candidate_name"), r.get("vacancy_title"), r["status"]]

    def fill_form_from_row(self, row):
        super().fill_form_from_row(row)
        if self.current_id is None:
            return
        for r in self.fetch():
            if r["id"] == self.current_id:
                self.set_values({
                    "candidate_id": r.get("candidate_id"),
                    "vacancy_id": r.get("vacancy_id"),
                    "status": r.get("status"),
                })
                break

    def do_create(self):
        response_repo.create(
            int(self.value("candidate_id")), int(self.value("vacancy_id")),
            self.value("status") or "На рассмотрении",
            user_login=self.login, user_role=self.role,
        )

    def do_update(self):
        response_repo.update(
            self.current_id,
            int(self.value("candidate_id")), int(self.value("vacancy_id")),
            self.value("status") or "На рассмотрении",
            user_login=self.login, user_role=self.role,
        )

    def do_delete(self):
        response_repo.delete(self.current_id, user_login=self.login, user_role=self.role)
