"""Сделки агентства: создаются по трудоустроенным откликам.

Логическая связь: сделка = закрывшийся отклик (соискатель → вакансия →
работодатель). Поле «отклик» — выпадающий список с понятными подписями,
а не голые ID.
"""
from src.db.repositories import deal_repo, response_repo
from src.ui.sections.base_crud import CrudSection


class DealsSection(CrudSection):
    section_key = "deals"
    entity_type = "deal"
    icon_name = "handshake"
    title = "Сделки"
    subtitle = "Закрытые сделки: соискатель → вакансия → работодатель"
    columns = ["id", "Соискатель", "Вакансия", "Работодатель", "Комиссия", "Налог", "Дата"]
    fields = [
        ("response_id", "Отклик (трудоустроенный)", "combo"),
        ("commission", "Комиссия (₽)"),
        ("tax", "Налог (₽)"),
    ]

    def fetch(self):
        return deal_repo.get_all()

    def field_options(self, name):
        if name == "response_id":
            # сделку можно закрыть только по трудоустроенному отклику,
            # по которому ещё нет сделки (response_id UNIQUE)
            done = {d["response_id"] for d in deal_repo.get_all()}
            return [
                f"{r['id']} — {r.get('candidate_name') or '?'} → "
                f"{r.get('vacancy_title') or '?'}"
                for r in response_repo.get_all()
                if r["status"] == "Трудоустроен" and r["id"] not in done
            ]
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
        return [r["id"], r.get("candidate_name"), r.get("vacancy_title"),
                r.get("employer_name"), r["commission"], r["tax"],
                r.get("closed_at")]

    def fill_form_from_row(self, row):
        super().fill_form_from_row(row)
        if self.current_id is None:
            return
        for r in self.fetch():
            if r["id"] == self.current_id:
                resp_label = f"{r.get('response_id')} — {r.get('candidate_name') or ''} → {r.get('vacancy_title') or ''}".strip()
                self.set_values({
                    "response_id": resp_label,
                    "commission": r.get("commission"),
                    "tax": r.get("tax"),
                })
                break

    def _response_id(self):
        rid = self._parse_id(self.value("response_id"))
        if rid is None:
            raise ValueError(
                "Нет доступных откликов: сделка закрывается по отклику "
                "со статусом «Трудоустроен» (смените статус в разделе «Отклики»)")
        if any(d["response_id"] == rid for d in deal_repo.get_all()):
            raise ValueError("По этому отклику сделка уже создана")
        return rid

    def do_create(self):
        deal_repo.create(self._response_id(),
                         int(self.value("commission") or 0),
                         int(self.value("tax") or 0),
                         user_login=self.login, user_role=self.role)

    def do_update(self):
        deal_repo.update(self.current_id, self._response_id(),
                         int(self.value("commission") or 0),
                         int(self.value("tax") or 0),
                         user_login=self.login, user_role=self.role)

    def do_delete(self):
        deal_repo.delete(self.current_id, user_login=self.login, user_role=self.role)
