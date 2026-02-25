SERVICE_ALIASES = {
    "odontopediatria (retorno)": "Odontopediatria (Consulta)",
}


def canonicalize_service_name(service_name: str) -> str:
    cleaned = (service_name or "").strip()
    if not cleaned:
        return cleaned
    return SERVICE_ALIASES.get(cleaned.lower(), cleaned)
