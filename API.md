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

| Field       | Type   | Required | Description         |
| ----------- | ------ | -------- | ------------------- |
| `email`     | string | Yes      | Valid email address |
| `full_name` | string | Yes      | User's full name    |
| `password`  | string | Yes      | User's password     |

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

---

### `POST /users/login`

Authenticate a user and return access and refresh tokens.

**Request Body**

| Field      | Type   | Required | Description         |
| ---------- | ------ | -------- | ------------------- |
| `email`    | string | Yes      | Valid email address |
| `password` | string | Yes      | User's password     |

**Response** `200 OK`

```json
{
  "access_token": "<jwt>",
  "refresh_token": "<jwt>",
  "token_type": "bearer"
}
```

**Errors**

| Status | Detail                    |
| ------ | ------------------------- |
| 401    | Invalid email or password |
| 403    | Account is disabled       |

---

### `POST /users/refresh`

Exchange a refresh token for a new token pair.

**Request Body**

| Field   | Type   | Required | Description           |
| ------- | ------ | -------- | --------------------- |
| `token` | string | Yes      | Valid refresh token   |

**Response** `200 OK`

```json
{
  "access_token": "<jwt>",
  "refresh_token": "<jwt>",
  "token_type": "bearer"
}
```

**Errors**

| Status | Detail                          |
| ------ | ------------------------------- |
| 401    | Invalid or expired refresh token |
| 401    | User not found                  |
| 403    | Account is disabled             |

---

### `GET /users/profile`

Get the current authenticated user's profile.

**Headers**

| Header          | Value                  |
| --------------- | ---------------------- |
| `Authorization` | `Bearer <access_token>` |

**Response** `200 OK`

```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true
}
```

**Errors**

| Status | Detail              |
| ------ | ------------------- |
| 401    | Invalid or expired token |
| 403    | Account is disabled |
