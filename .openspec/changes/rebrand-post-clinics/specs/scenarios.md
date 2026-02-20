# Scenarios: Rebrand to POST Clinics

## Scenario A: Database Persistence
**Given** the application starts
**When** the database engine initializes
**Then** it should create/connect to `post_clinics.db` instead of `noshow.db`.

## Scenario B: API Identity
**Given** the API is running
**When** a user accesses the root path `/`
**Then** the response should contain "POST Clinics API".

## Scenario C: Agent Identity
**Given** the agent is instantiated
**When** checking its `name` attribute
**Then** it should be `PostClinicsReceptionist`.
