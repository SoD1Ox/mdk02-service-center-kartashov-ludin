from src.db.repositories import deal_repo
from src.ui.sections.base_crud import CrudSection


class DealsSection(CrudSection):
    section_key = "deals"
    entity_type = "deal"
    icon_name = "handshake"
    title = "Сделки"
    subtitle = "Закрытые сделки агентства (комиссия и налог)"
    columns = ["id", "ID отклика", "Комиссия", "Налог", "Дата"]
    fields = [
        ("response_id", "ID отклика"),
        ("commission", "Комиссия (₽)"),
        ("tax", "Налог (₽)"),
    ]

    def fetch(self):
        return deal_repo.get_all()

    def to_row(self, r):
        return [r["id"], r.get("response_id"), r["commission"], r["tax"],
                r.get("closed_at")]

    def fill_form_from_row(self, row):
        super().fill_form_from_row(row)
        if self.current_id is None:
            return
        for r in self.fetch():
            if r["id"] == self.current_id:
                self.set_values({
                    "response_id": r.get("response_id"),
                    "commission": r.get("commission"),
                    "tax": r.get("tax"),
                })
                break

    def do_create(self):
        deal_repo.create(
            int(self.value("response_id")),
            int(self.value("commission") or 0), int(self.value("tax") or 0),
            user_login=self.login, user_role=self.role,
        )

    def do_update(self):
        deal_repo.update(
            self.current_id,
            int(self.value("response_id")),
            int(self.value("commission") or 0), int(self.value("tax") or 0),
            user_login=self.login, user_role=self.role,
        )

    def do_delete(self):
        deal_repo.delete(self.current_id, user_login=self.login, user_role=self.role)
