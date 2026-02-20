# Design: Ngrok Integration

## Architecture
We will add a new service to `docker-compose.yml` using the official `ngrok/ngrok` image.

### Docker Compose
*   **Service Name**: `ngrok`
*   **Image**: `ngrok/ngrok:latest`
*   **Command**: `http --domain=<optional_static_domain> app:8000`
    *   *Note*: If no static domain is available, we use `http app:8000`.
*   **Environment Variables**:
    *   `NGROK_AUTHTOKEN`: Required from user.
*   **Dependencies**: Depends on `app` service.

### Environment Management
*   **`.env`**: Add `NGROK_AUTHTOKEN`.
*   **`.env.example`**: Add placeholder for token.

## Considerations
*   **Token Requirement**: Ngrok v3+ requires an account and token. We must ask the user for this.
*   **Ephemeral URLs**: Without a paid plan/static domain, the URL changes every restart. We need to print the URL or instruct the user where to find it (`http://localhost:4040` dashboard is often available if we expose it).

## Alternative
If running `ngrok` as a container is too heavy, we can just supply a `start_tunnel.bat` script, but containerized is requested ("rodar tbm o ngrok... no docker").
