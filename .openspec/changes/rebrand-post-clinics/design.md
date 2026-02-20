# Design: Rebrand to POST Clinics

## Components

### 1. Database (`src/database.py`)
- Change `sqlite_file_name` string from `"noshow.db"` to `"post_clinics.db"`.

### 2. Agent (`src/agent.py`)
- Update `Agent` instantiation:
  ```python
  agent = Agent(name="PostClinicsReceptionist", ...)
  ```

### 3. API (`src/main.py`)
- Update the root endpoint logic:
  ```python
  @app.get("/")
  async def root():
      return {"message": "POST Clinics API is running"}
  ```

### 4. Documentation (`README.md`)
- Update Title to "POST Clinics".
