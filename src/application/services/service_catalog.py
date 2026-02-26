import re


SERVICE_ALIASES = {
    "odontopediatria (retorno)": "Odontopediatria (Consulta)",
    "odontopediatria (consulta)": "Odontopediatria (Consulta)",
    "para odontopediatria (consulta)": "Odontopediatria (Consulta)",
    "pacientes especiais (1ª vez)": "Paciente com necessidades especiais (1ª vez)",
    "pacientes especiais (retorno)": "Paciente com necessidades especiais (Consulta)",
    "paciente com necessidades especiais (retorno)": "Paciente com necessidades especiais (Consulta)",
    "paciente com necessidades especiais (consulta)": "Paciente com necessidades especiais (Consulta)",
}


def _normalize_service_key(service_name: str) -> str:
    normalized = (service_name or "").strip().lower()
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = re.sub(r"\(\s+", "(", normalized)
    normalized = re.sub(r"\s+\)", ")", normalized)
    return normalized


def canonicalize_service_name(service_name: str) -> str:
    cleaned = (service_name or "").strip()
    if not cleaned:
        return cleaned
    return SERVICE_ALIASES.get(_normalize_service_key(cleaned), cleaned)
