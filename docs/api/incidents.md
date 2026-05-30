# Incidents API

Base path:

```text
/api/v1/incidents
```

---

## Create Incident

### Request

```http
POST /api/v1/incidents
Content-Type: application/json
```

### Body

```json
{
  "title": "Checkout API latency spike",
  "description": "p95 latency is above 2s",
  "severity": "sev2",
  "service_name": "checkout-api",
  "owner_team": "payments"
}
```

### Response

```http
201 Created
```

```json
{
  "id": "uuid",
  "title": "Checkout API latency spike",
  "description": "p95 latency is above 2s",
  "severity": "sev2",
  "status": "open",
  "service_name": "checkout-api",
  "owner_team": "payments"
}
```

---

## Get Incident

### Request

```http
GET /api/v1/incidents/{incident_id}
```

### Response

```http
200 OK
```

```json
{
  "id": "uuid",
  "title": "Checkout API latency spike",
  "description": "p95 latency is above 2s",
  "severity": "sev2",
  "status": "open",
  "service_name": "checkout-api",
  "owner_team": "payments"
}
```

---

## List Incidents

### Request

```http
GET /api/v1/incidents?limit=50&offset=0
```

### Response

```json
{
  "items": [],
  "limit": 50,
  "offset": 0,
  "count": 0
}
```

---

## Change Incident Severity

### Request

```http
PATCH /api/v1/incidents/{incident_id}/severity
Content-Type: application/json
```

### Body

```json
{
  "severity": "sev1"
}
```

### Response

```http
200 OK
```

```json
{
  "id": "uuid",
  "severity": "sev1"
}
```

---

## Change Incident Status

### Request

```http
PATCH /api/v1/incidents/{incident_id}/status
Content-Type: application/json
```

### Body

```json
{
  "status": "resolved"
}
```

### Response

```http
200 OK
```

```json
{
  "id": "uuid",
  "status": "resolved"
}
```

---

## Error Format

All API errors follow the same structure.

### Example

```json
{
  "error": "bad_request",
  "message": "Invalid incident id",
  "request_id": "req-123",
  "correlation_id": "corr-456"
}
```

---

## Request Tracing Headers

Supported request headers:

```text
X-Request-ID
X-Correlation-ID
```

Returned in responses to support distributed tracing.
