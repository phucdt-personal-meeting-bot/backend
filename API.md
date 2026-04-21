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

| Field   | Type   | Required | Description         |
| ------- | ------ | -------- | ------------------- |
| `token` | string | Yes      | Valid refresh token |

**Response** `200 OK`

```json
{
  "access_token": "<jwt>",
  "refresh_token": "<jwt>",
  "token_type": "bearer"
}
```

**Errors**

| Status | Detail                           |
| ------ | -------------------------------- |
| 401    | Invalid or expired refresh token |
| 401    | User not found                   |
| 403    | Account is disabled              |

---

### `GET /users/profile`

Get the current authenticated user's profile.

**Headers**

| Header          | Value                   |
| --------------- | ----------------------- |
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

| Status | Detail                   |
| ------ | ------------------------ |
| 401    | Invalid or expired token |
| 403    | Account is disabled      |

---

## Translation

All translation endpoints require authentication via `Authorization: Bearer <access_token>`.

### `POST /translation/upload`

Upload an Excel file and create a translation job.

**Headers**

| Header         | Value                 |
| -------------- | --------------------- |
| `Content-Type` | `multipart/form-data` |

**Form Fields**

| Field           | Type   | Required | Description                                        |
| --------------- | ------ | -------- | -------------------------------------------------- |
| `file`          | file   | Yes      | Excel file (`.xlsx` or `.xls`)                     |
| `language`      | string | Yes      | Target language: `vi`, `en`, or `ja`               |
| `prompt`        | string | Yes      | Overall prompt for the file                        |
| `sheet_prompts` | string | Yes      | JSON array of per-sheet prompts (see format below) |

`sheet_prompts` format:
```json
[
  { "sheet_name": "Sheet1", "prompt": "Translate product names" },
  { "sheet_name": "Sheet2", "prompt": "Translate descriptions" }
]
```

**Response** `201 Created`

```json
{
  "id": 1,
  "status": "pending",
  "language": "vi",
  "prompt": "Translate this document",
  "sheet_prompts": [
    { "sheet_name": "Sheet1", "prompt": "Translate product names" }
  ],
  "file_key": "translations/<uuid>/<filename>",
  "bucket": "meeting-bot",
  "result_file_key": null,
  "error": null,
  "created_at": "2026-04-15T00:00:00Z",
  "updated_at": "2026-04-15T00:00:00Z"
}
```

**Errors**

| Status | Detail                             |
| ------ | ---------------------------------- |
| 401    | Invalid or expired token           |
| 403    | Account is disabled                |
| 422    | Invalid file type or sheet_prompts |
| 502    | S3 upload failed                   |

---

### `GET /translation/jobs`

List all translation jobs for the current user, sorted newest to oldest.

**Query Parameters**

| Param       | Type    | Default | Constraints | Description       |
| ----------- | ------- | ------- | ----------- | ----------------- |
| `page`      | integer | `1`     | ≥ 1         | Page number       |
| `page_size` | integer | `20`    | 1–100       | Items per page    |

**Response** `200 OK`

```json
{
  "items": [ { "id": 1, "status": "pending", "..." } ],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "pages": 3
}
```

**Errors**

| Status | Detail                   |
| ------ | ------------------------ |
| 401    | Invalid or expired token |
| 403    | Account is disabled      |

---

### `GET /translation/jobs/{job_id}`

Get the status and details of a specific translation job.

**Path Parameters**

| Param    | Type    | Description |
| -------- | ------- | ----------- |
| `job_id` | integer | Job ID      |

**Response** `200 OK`

```json
{
  "id": 1,
  "status": "pending",
  "language": "vi",
  "prompt": "Translate this document",
  "sheet_prompts": [
    { "sheet_name": "Sheet1", "prompt": "Translate product names" }
  ],
  "file_key": "translations/<uuid>/<filename>",
  "bucket": "meeting-bot",
  "result_file_key": null,
  "error": null,
  "created_at": "2026-04-15T00:00:00Z",
  "updated_at": "2026-04-15T00:00:00Z"
}
```

**Errors**

| Status | Detail                   |
| ------ | ------------------------ |
| 401    | Invalid or expired token |
| 403    | Account is disabled      |
| 404    | Job not found            |
