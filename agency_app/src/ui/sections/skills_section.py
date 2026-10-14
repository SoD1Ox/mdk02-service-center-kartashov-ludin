from src.db.repositories import skill_repo
from src.ui.sections.base_crud import CrudSection


class SkillsSection(CrudSection):
    section_key = "skills"
    entity_type = "skill"
    title = "Навыки"
    subtitle = "Справочник навыков для резюме и вакансий"
    columns = ["id", "Название", "Категория"]
    fields = [
        ("name", "Название"),
        ("category", "Категория"),
    ]

    def fetch(self):
        return skill_repo.get_all()

    def to_row(self, r):
        return [r["id"], r["name"], r["category"]]

    def fill_form_from_row(self, row):
        super().fill_form_from_row(row)
        if self.current_id is None:
            return
        for r in self.fetch():
            if r["id"] == self.current_id:
                self.set_values({"name": r.get("name"), "category": r.get("category")})
                break

    def do_create(self):
        skill_repo.create(self.value("name"), self.value("category"),
                          user_login=self.login, user_role=self.role)

    def do_update(self):
        skill_repo.update(self.current_id, self.value("name"), self.value("category"),
                          user_login=self.login, user_role=self.role)

    def do_delete(self):
        skill_repo.delete(self.current_id, user_login=self.login, user_role=self.role)
