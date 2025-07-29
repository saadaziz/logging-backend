
# Logging Backend Service (JWT Enabled)

This microservice provides a simple logging API with JWT authentication issued by the `identity-backend` service.

---

## Setup

### Environment Variables
Set these in `.env` (for local) or in cPanel’s Python app environment:

```
JWT_SECRET_KEY=<same as identity-backend>
JWT_ISSUER=identity-backend
LOG_DB_URL=sqlite:///logs.db
```

---

### Requirements

Install dependencies:
```
pip install -r requirements.txt
```

Dependencies include:
- Flask
- SQLAlchemy
- PyJWT
- python-dotenv

---

### Deployment (cPanel)

1. Upload the code to `/logging-backend` directory.
2. Configure environment variables in **Setup Python App** (cPanel).
3. Run **pip install** from cPanel.
4. Restart Passenger:

```
touch tmp/restart.txt
```

---

## Health Check

Verify the service is running:

```
https://aurorahours.com/logging-backend/ping
```

Should return `OK`.

---

## Usage

### 1. Obtain JWT Token from Identity Service

```powershell
$resp = Invoke-RestMethod -Uri "https://aurorahours.com/identity-backend/token" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"sub":"careergpt-backend","aud":"logging-service"}'

$token = $resp.token
```

---

### 2. Access Logging Endpoints

#### Get Logs
```powershell
Invoke-RestMethod -Uri "https://aurorahours.com/logging-backend/logs" `
  -Headers @{Authorization = "Bearer $token"}
```

#### Write Log
```powershell
Invoke-RestMethod -Uri "https://aurorahours.com/logging-backend/log" `
  -Method POST `
  -Headers @{"Authorization"="Bearer $token"; "Content-Type"="application/json"} `
  -Body '{"service":"careergpt","level":"INFO","message":"Test log","context":{"user":"test123"}}'
```

#### Purge Logs
```powershell
Invoke-RestMethod -Uri "https://aurorahours.com/logging-backend/logs/purge" `
  -Method POST `
  -Headers @{Authorization = "Bearer $token"}
```

#### Download Logs
```
https://aurorahours.com/logging-backend/logs/download
```

(Include `Authorization` header in API clients or curl.)

---

## Notes

- JWTs expire based on settings in `identity-backend` (default 15 min).
- `JWT_SECRET_KEY` must match between identity and logging services.
- SQLite is used for simplicity; migrate to MySQL/Postgres for production.
