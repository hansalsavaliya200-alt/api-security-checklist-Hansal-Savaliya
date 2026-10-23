# Safe Request / Response Design: Examples

All data is **fictional**. The API ran only on `127.0.0.1:5000` (see `app.py`).
The outputs below are real captures from `run_demo.sh` (see `../screenshots/demo_run_output.txt`).
Note: `request_id` values and tokens differ on every run.

## 1. Unauthenticated request is refused

```http
GET /api/v1/notes HTTP/1.1
```
```http
HTTP/1.1 401 UNAUTHORIZED
WWW-Authenticate: Bearer

{"error":{"code":"unauthenticated","message":"Authentication required.","request_id":"857872504e81"}}
```
Design points: default deny, a `WWW-Authenticate` hint, generic text, and a request ID for log correlation.

## 2. Valid create: server decides ownership, response returns only public fields

```http
POST /api/v1/notes HTTP/1.1
Content-Type: application/json
Authorization: Bearer <short-lived signed token>

{"title":"Groceries","body":"milk, eggs"}
```
```http
HTTP/1.1 201 CREATED
Location: /api/v1/notes/b8701643-626e-4127-91e4-9aad8f4947ae
X-Request-ID: d8be5694ae86

{"body":"milk, eggs","created_at":1792001399,"id":"b8701643-626e-4127-91e4-9aad8f4947ae","title":"Groceries"}
```
Design points: the owner is taken from the token, IDs are random UUIDs, and the stored internal fields (`owner_id`, `internal_flag`) are not returned.

## 3. Mass-assignment attempt is rejected

```http
POST /api/v1/notes
{"title":"x","owner_id":"u-1002"}
```
```http
HTTP/1.1 400 BAD REQUEST

{"error":{"code":"validation_error","message":"Unknown field(s) not allowed.","request_id":"368713bb92de"}}
```
Design points: allow-list schema; unexpected fields are an error rather than silently ignored.

## 4. Object-level authorisation (BOLA/IDOR) check

Bob requests a note that belongs to Alice:

```http
GET /api/v1/notes/b8701643-626e-4127-91e4-9aad8f4947ae
Authorization: Bearer <bob's token>
```
```http
HTTP/1.1 404 NOT FOUND

{"error":{"code":"not_found","message":"Resource not found.","request_id":"ac45173ab1dc"}}
```
Design points: the ownership check runs on every request, and "not yours" looks the same as "does not exist" so IDs cannot be enumerated.

## 5. Deprecated version announces its retirement

```http
GET /api/v0/notes
```
```http
HTTP/1.1 200 OK
Deprecation: @1767225600
Sunset: Wed, 31 Mar 2027 23:59:59 GMT
Link: </api/v1/notes>; rel="successor-version"
```
The dates are fictional.

## 6. Rate limit

Login allows 5 attempts per minute per client IP. In the captured run, the two successful logins in step 2 of the script already used 2 of the 5, so the 4th wrong attempt (the 6th login call in total) was answered with 429:

```
attempt 1 -> 401
attempt 2 -> 401
attempt 3 -> 401
attempt 4 -> 429
attempt 5 -> 429
attempt 6 -> 429
```
The 429 response includes a `Retry-After` header.

## 7. Unexpected server error (verified by automated test)

The test `test_unexpected_exception_hides_details` forces an internal exception. The client receives only:

```json
{"error":{"code":"internal_error","message":"Something went wrong.","request_id":"..."}}
```
and the exception text appears only in the server log.
