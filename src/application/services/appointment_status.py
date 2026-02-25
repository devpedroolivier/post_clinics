from typing import Any


STATUS_METADATA = {
    "confirmed": {
        "label": "Confirmado",
        "color": "#16A34A",
        "description": "Consulta confirmada pelo paciente.",
    },
    "scheduled": {
        "label": "Pendente",
        "color": "#F59E0B",
        "description": "Aguardando confirmação do paciente.",
    },
    "rescheduled": {
        "label": "Reagendado",
        "color": "#2563EB",
        "description": "Consulta reagendada e aguardando validação final.",
    },
    "cancelled": {
        "label": "Cancelado",
        "color": "#DC2626",
        "description": "Consulta cancelada.",
    },
}

STATUS_ALIASES = {
    "pendente": "scheduled",
    "aguardando": "scheduled",
    "awaiting_confirmation": "scheduled",
    "reagendado": "rescheduled",
    "confirmado": "confirmed",
    "cancelado": "cancelled",
}


def normalize_status(status: str | None, default: str = "scheduled") -> str:
    if not status:
        return default
    key = status.strip().lower()
    canonical = STATUS_ALIASES.get(key, key)
    return canonical if canonical in STATUS_METADATA else default


def get_status_metadata(status: str | None) -> dict[str, Any]:
    canonical = normalize_status(status)
    return {
        "status": canonical,
        **STATUS_METADATA[canonical],
    }


def build_status_legend_description(status: str | None) -> str:
    current = get_status_metadata(status)
    return (
        f"Status atual: {current['label']} ({current['color']}). "
        "Legenda: "
        "Confirmado=#16A34A, "
        "Pendente=#F59E0B, "
        "Reagendado=#2563EB, "
        "Cancelado=#DC2626."
    )
