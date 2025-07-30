
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

#### **Add Log Entry**

**PowerShell**
```powershell
Invoke-RestMethod -Uri "https://aurorahours.com/logging-backend/log" `
  -Method POST `
  -Headers @{"Authorization"="Bearer $token"; "Content-Type"="application/json"} `
  -Body '{"service":"careergpt","level":"INFO","message":"New log entry from PS","context":{"user":"test123"}}'
```

**cURL**
```bash
curl -X POST "https://aurorahours.com/logging-backend/log"   -H "Authorization: Bearer $token"   -H "Content-Type: application/json"   -d '{"service":"careergpt","level":"INFO","message":"New log entry from curl","context":{"user":"test123"}}'
```

---

#### **Retrieve Latest Logs**

**PowerShell**
```powershell
Invoke-RestMethod -Uri "https://aurorahours.com/logging-backend/logs" `
  -Headers @{Authorization = "Bearer $token"}
```

**cURL**
```bash
curl -X GET "https://aurorahours.com/logging-backend/logs"   -H "Authorization: Bearer $token"
```

---

#### **Purge All Logs**

**PowerShell**
```powershell
Invoke-RestMethod -Uri "https://aurorahours.com/logging-backend/logs/purge" `
  -Method POST `
  -Headers @{Authorization = "Bearer $token"}
```

**cURL**
```bash
curl -X POST "https://aurorahours.com/logging-backend/logs/purge"   -H "Authorization: Bearer $token"
```

---

#### **Download Logs as Text File**

**Browser or cURL**
```
https://aurorahours.com/logging-backend/logs/download
```

Include Authorization header if using API client:

```bash
curl -X GET "https://aurorahours.com/logging-backend/logs/download"   -H "Authorization: Bearer $token" -o logs.txt
```

---

## Debugging 

### Make sure secrets match

```bash
Invoke-RestMethod -Uri "https://aurorahours.com/identity-backend/debug-env"
```

```bash
Invoke-RestMethod -Uri "https://aurorahours.com/logging-backend/debug-env"
```
## Notes

- JWTs expire based on settings in `identity-backend` (default 15 min).
- `JWT_SECRET_KEY` must match between identity and logging services.
- SQLite is used for simplicity; migrate to MySQL/Postgres for production.

---

## Coordinated Release Instructions

To ensure `identity-backend` and `logging-backend` are compatible during deployment:

1. Update both repos to use the same `JWT_SECRET_KEY` and `JWT_ISSUER`.
2. Tag each repo with the same release version (e.g., `v1.0.0`):
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
3. Deploy both services together to avoid mismatched secrets.

### Checking Out Matching Versions
```bash
git clone https://github.com/<your-org>/identity-backend.git
cd identity-backend
git checkout v1.0.0
```

```bash
git clone https://github.com/<your-org>/logging-backend.git
cd logging-backend
git checkout v1.0.0
```

---

## Notes

- JWTs expire based on settings in `identity-backend` (default 15 min).
- `JWT_SECRET_KEY` must match between identity and logging services.
- SQLite is used for simplicity; migrate to MySQL/Postgres for production.

### Environment Variables
Set the same JWT_SECRET_KEY and JWT_ISSUER in both services:
```bash
JWT_SECRET_KEY=your_shared_secret
JWT_ISSUER=identity-backend
```