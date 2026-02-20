# Scenarios: Customize Clinic Persona

## Scenario A: Identity and Tone
**Given** `CLINIC_CONFIG` name is "Espaço Interativo Reavilitare"
**When** the user asks "Quem é você?"
**Then** the agent should reply "Sou a Carol, recepcionista virtual da Espaço Interativo Reavilitare." (or configured name).

## Scenario B: Service Rules & Durations
**Given** configured services include "Odontopediatria" with variable duration
**When** the user asks "Quero marcar odontopediatria"
**Then** the agent should ask "É sua primeira consulta ou retorno?" to determine if it's 60min or 40min.

## Scenario C: Specific Date Restrictions
**Given** Ortodontia is only available on Feb 24th and 25th
**When** the user asks "Tem ortodontista para amanhã?" (if not Feb 24/25)
**Then** the agent should inform that Orthodontia is only available on specific dates (24/25 Feb).

## Scenario D: Availability Check
**Given** operating hours end at 17:30
**When** the user asks "Tem horário as 17:00?"
**Then** the agent should check if the service duration (e.g., 40min) fits before closing (17:40 > 17:30) and potentially refuse or warn.
