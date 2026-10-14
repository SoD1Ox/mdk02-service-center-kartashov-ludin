from src.db.repositories import employer_repo
from src.ui.sections.base_crud import CrudSection


class EmployersSection(CrudSection):
    section_key = "employers"
    entity_type = "employer"
    title = "Работодатели"
    subtitle = "Компании-заказчики вакансий"
    columns = ["id", "Название", "ИНН", "Контакт", "Телефон"]
    fields = [
        ("name", "Название"),
        ("inn", "ИНН"),
        ("contact_person", "Контактное лицо"),
        ("phone", "Телефон"),
    ]

    def fetch(self):
        return employer_repo.get_all()

    def to_row(self, r):
        return [r["id"], r["name"], r["inn"], r["contact_person"], r["phone"]]

    def fill_form_from_row(self, row):
        super().fill_form_from_row(row)
        if self.current_id is None:
            return
        for r in self.fetch():
            if r["id"] == self.current_id:
                self.set_values({k: r.get(k) for k in
                                 ("name", "inn", "contact_person", "phone")})
                break

    def do_create(self):
        employer_repo.create(
            self.value("name"), self.value("inn"),
            self.value("contact_person"), self.value("phone"),
            user_login=self.login, user_role=self.role,
        )

    def do_update(self):
        employer_repo.update(
            self.current_id,
            self.value("name"), self.value("inn"),
            self.value("contact_person"), self.value("phone"),
            user_login=self.login, user_role=self.role,
        )

    def do_delete(self):
        employer_repo.delete(self.current_id, user_login=self.login, user_role=self.role)
