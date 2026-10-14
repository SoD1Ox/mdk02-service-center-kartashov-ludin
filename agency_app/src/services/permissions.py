PERMISSIONS = {
    "admin": {
        "candidates": ["view", "add", "edit", "delete"],
        "resumes":    ["view", "add", "edit", "delete"],
        "skills":     ["view", "add", "edit", "delete"],
        "employers":  ["view", "add", "edit", "delete"],
        "vacancies":  ["view", "add", "edit", "delete"],
        "responses":  ["view", "add", "edit", "delete"],
        "deals":      ["view", "add", "edit", "delete"],
        "audit":      ["view", "view_all"],
    },
    "manager": {
        "candidates": ["view", "add", "edit", "delete"],
        "resumes":    ["view", "add", "edit", "delete"],
        "skills":     ["view", "add", "edit"],
        "employers":  ["view", "add", "edit"],
        "vacancies":  ["view", "add", "edit"],
        "responses":  ["view", "add", "edit"],
        "deals":      ["view", "add", "edit"],
        # менеджер видит действия администратора, директора, менеджеров и свои
        "audit":      ["view", "view_admin_director_manager"],
    },
    "director": {
        "candidates": ["view"],
        "resumes":    ["view"],
        "skills":     ["view"],
        "employers":  ["view"],
        "vacancies":  ["view"],
        "responses":  ["view"],
        "deals":      ["view"],
        # директор видит только свои действия
        "audit":      ["view", "view_own"],
    },
    "employer": {
        "vacancies":  ["view", "add", "edit"],
        "responses":  ["view"],
        "audit":      ["view", "view_own"],
    },
    "candidate": {
        "resumes":    ["view", "add", "edit"],
        "vacancies":  ["view"],
        "responses":  ["view", "add", "delete"],
        "audit":      ["view", "view_own"],
    },
}


def can(role: str, section: str, action: str) -> bool:
    return action in PERMISSIONS.get(role, {}).get(section, [])