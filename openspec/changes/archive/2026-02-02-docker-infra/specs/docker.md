# Docker Infrastructure Specs

### Requirement: Application Containerization
The application runs inside a Docker container.

#### Scenario: Build Image
- **WHEN** I run `docker-compose build`
- **THEN** The build completes successfully without missing dependency errors.
- **AND** The image size is reasonable (based on slim variant).

#### Scenario: Run Container
- **WHEN** I run `docker-compose up -d`
- **THEN** The container starts and stays running (no immediate exit).
- **AND** The application responds to health check at `http://localhost:8000/`.

### Requirement: Data Persistence
Application data survives container lifecycle.

#### Scenario: Persistent Volume
- **WHEN** I configured `DATA_DIR=/app/data` env var
- **AND** I restart the container after creating a session
- **THEN** The previous session data is still available in the database.
