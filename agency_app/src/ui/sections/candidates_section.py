from src.db.repositories import candidate_repo
from src.ui.sections.base_crud import CrudSection


class CandidatesSection(CrudSection):
    section_key = "candidates"
    entity_type = "candidate"
    icon_name = "users"
    title = "Соискатели"
    subtitle = "Учёт кандидатов агентства"
    columns = ["id", "ФИО", "Телефон", "Email"]
    fields = [
        ("full_name", "ФИО"),
        ("phone", "Телефон"),
        ("email", "Email"),
    ]

    def fetch(self):
        return candidate_repo.get_all()

    def to_row(self, r):
        return [r["id"], r["full_name"], r["phone"], r["email"]]

    def fill_form_from_row(self, row):
        super().fill_form_from_row(row)
        if self.current_id is None:
            return
        for r in self.fetch():
            if r["id"] == self.current_id:
                self.set_values({k: r.get(k) for k in ("full_name", "phone", "email")})
                break

    def do_create(self):
        candidate_repo.create(
            self.value("full_name"), self.value("phone"), self.value("email"),
            user_login=self.login, user_role=self.role,
        )

    def do_update(self):
        candidate_repo.update(
            self.current_id,
            self.value("full_name"), self.value("phone"), self.value("email"),
            user_login=self.login, user_role=self.role,
        )

    def do_delete(self):
        candidate_repo.delete(self.current_id, user_login=self.login, user_role=self.role)
