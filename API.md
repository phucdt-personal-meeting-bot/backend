# API Reference

## Health

### `GET /health`

Health check endpoint.

**Response** `200 OK`

```json
{
  "status": "ok"
}
```

---

## Users

### `POST /users/register`

Register a new user.

**Request Body**

| Field       | Type   | Required | Description          |
| ----------- | ------ | -------- | -------------------- |
| `email`     | string | Yes      | Valid email address  |
| `full_name` | string | Yes      | User's full name     |
| `password`  | string | Yes      | User's password      |

Password requirements:
- At least 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 digit

**Response** `201 Created`

```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true
}
```

**Errors**

| Status | Detail                   |
| ------ | ------------------------ |
| 409    | Email already registered |
| 422    | Validation error         |
