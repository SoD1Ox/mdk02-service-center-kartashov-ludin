from src.db.repositories import resume_repo
from src.ui.sections.base_crud import CrudSection


class ResumesSection(CrudSection):
    section_key = "resumes"
    entity_type = "resume"
    title = "Резюме"
    subtitle = "Резюме соискателей"
    columns = ["id", "Соискатель", "Должность", "Опыт", "Образование"]
    fields = [
        ("candidate_id", "ID соискателя"),
        ("title", "Должность"),
        ("experience", "Опыт (лет)"),
        ("education", "Образование"),
    ]

    def fetch(self):
        return resume_repo.get_all()

    def to_row(self, r):
        return [r["id"], r.get("candidate_name"), r["title"], r["experience"], r["education"]]

    def fill_form_from_row(self, row):
        super().fill_form_from_row(row)
        if self.current_id is None:
            return
        for r in self.fetch():
            if r["id"] == self.current_id:
                self.set_values({
                    "candidate_id": r.get("candidate_id"),
                    "title": r.get("title"),
                    "experience": r.get("experience"),
                    "education": r.get("education"),
                })
                break

    def do_create(self):
        resume_repo.create(
            int(self.value("candidate_id")), self.value("title"),
            int(self.value("experience") or 0), self.value("education"),
            user_login=self.login, user_role=self.role,
        )

    def do_update(self):
        resume_repo.update(
            self.current_id,
            int(self.value("candidate_id")), self.value("title"),
            int(self.value("experience") or 0), self.value("education"),
            user_login=self.login, user_role=self.role,
        )

    def do_delete(self):
        resume_repo.delete(self.current_id, user_login=self.login, user_role=self.role)
