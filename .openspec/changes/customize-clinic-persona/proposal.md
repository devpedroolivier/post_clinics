# Proposal: Customize Clinic Persona

## Change Description
Transform the static "NoShowReceptionist" agent into a dynamic, configurable entity capable of representing specific clinics with unique branding, services, and operational rules.

## Why
To support multiple clinics (SaaS model) and ensure the agent stays within operational bounds (hours, service types), reducing hallucinations and improving user experience.

## Objectives
- Create a configuration structure (`CLINIC_CONFIG`) for clinic details.
- Implement a dynamic prompt builder `get_agent_instructions`.
- Enforce business rules (opening hours, service list) in the system prompt.
