import os

# Data Persistence Configuration
# Docker uses /app/data, Local uses . (current dir)
DATA_DIR = os.environ.get("DATA_DIR", "data")

CLINIC_CONFIG = {
    "name": "Espaço Interativo Reabilitare",
    "assistant_name": "Cora",
    "hours": (
        "Ortodontia: Segunda a Sexta 08:00–11:30 / 13:00–17:30\n"
        "Dra. Débora e Dr. Sidney: Segunda a Sexta 09:00–11:00 / 14:30–17:00\n"
        "Demais serviços: Segunda a Sexta 09:00–17:30\n"
        "Sábados (quinzenalmente): 09:00–13:00"
    ),
    "schedules": {
        "Ortodontia": {"blocks": [("08:00", "11:30"), ("13:00", "17:30")]},
        "default": {"blocks": [("09:00", "17:30")]},
        "saturday": {"blocks": [("09:00", "13:00")]},
    },
    "services": [
        {"name": "Odontopediatria (1ª vez)", "duration": 60},
        {"name": "Odontopediatria (Retorno)", "duration": 40},
        {"name": "Pacientes Especiais (1ª vez)", "duration": 60},
        {"name": "Pacientes Especiais (Retorno)", "duration": 40},
        {"name": "Implante", "duration": 40},
        {"name": "Clínica Geral", "duration": 40},
        {"name": "Ortodontia", "duration": 40, "note": "Apenas dias 24 e 25 de Fev"},
        {"name": "Fonoaudióloga miofuncional", "duration": 40}
    ],
    "cancellation_policy": "Cancelamentos devem ser feitos com 24h de antecedência.",
    "communication_flow": "Enviamos confirmação 1 dia antes e lembrete 3h antes da consulta."
}

Z_API_CONFIG = {
    "instance_id": os.environ.get("Z_API_INSTANCE_ID"),
    "token": os.environ.get("Z_API_TOKEN"),
    "client_token": os.environ.get("Z_API_CLIENT_TOKEN")
}

ANTISPAM_CONFIG = {
    "max_messages_per_minute": 10,
    "cooldown_seconds": 2,
    "dedup_window_seconds": 300,
}
