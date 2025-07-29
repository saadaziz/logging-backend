# Logging Microservice (MVP)

This microservice provides centralized logging functionality for internal applications (e.g., CareerGPT backend, future e-commerce service). It is designed to be lightweight, easy to deploy on cPanel, and supports future upgrades to JWT-based authentication.

---

## Features

- `POST /log` – Accepts JSON payloads for logging (`service`, `level`, `message`, `context`).
- `GET /logs` – Returns latest logs in JSON format.
- `GET /logs/download` – Downloads logs as a text file.
- `POST /logs/purge` – Purges all logs (admin use).

An admin UI (`logs.html`) is included for easy viewing, downloading, and purging of logs.

---

## Security Overview

### Current MVP (Static Key)

- **Authentication**: Protected with a single API key (`LOG_SERVICE_KEY`) passed via Bearer token.
- **Transport**: All endpoints are served over HTTPS.
- **Usage**: Intended for *internal microservice-to-microservice* calls (e.g., backend → logging).

### Pros

- Simple to configure (single environment variable).
- Low overhead, good for MVP and rapid iteration.
- Works well when deployed **behind a firewall** or restricted by IP.

### Cons (To be addressed in next phase)

- Single shared secret – if leaked, all access is compromised.
- No per-service or per-user identity (no audit trail).
- No expiration or token rotation.

---

## Future Security (Planned)

Next phase will integrate `identity-backend` for **JWT-based service authentication**:

- Signed JWTs issued by identity-backend.
- Claims include service identity, audience, and expiry.
- Short-lived tokens, revocable without redeploying services.

---

## Deployment Context

### Internal Use

- Safe to deploy behind a firewall or VPC.
- Ideal for private networks (e.g., internal company infrastructure).

### External Use (Not Recommended)

- Do **not** expose `/log`, `/logs`, or `/purge` endpoints publicly in current form.
- If external exposure is required, wait for JWT integration phase or use reverse proxy with IP whitelisting.

---

## Environment Variables

Set these in cPanel or `.env` for local dev:

```
LOG_SERVICE_KEY=<your-secret-key>
LOG_DB_URL=sqlite:///logs.db
```

---

## Local Development

1. Clone repo and create virtual environment
2. Install dependencies (`pip install -r requirements.txt`)
3. Set `LOG_SERVICE_KEY` in `.env`
4. Run locally: `flask run --port 5001`

---

## Roadmap

- [x] MVP with static key
- [ ] JWT integration with identity-backend
- [ ] Role-based access and claims
- [ ] Log filtering, pagination, and analytics

---
