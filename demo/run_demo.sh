#!/usr/bin/env bash
# Local walkthrough against the demo API (start it first: python app.py)
# Uses only the fictional demo users. Run from any shell with curl and python3.
BASE=http://127.0.0.1:5000
J='Content-Type: application/json'
pp() { python3 -m json.tool 2>/dev/null || cat; }

echo "== 1. No token -> 401"
curl -si $BASE/api/v1/notes | sed -n '1p;/WWW-Authenticate/p;$p'

echo; echo "== 2. Login as alice"
TOKEN_A=$(curl -s -X POST $BASE/api/v1/login -H "$J" -d '{"username":"alice","password":"demo-password-alice"}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')
TOKEN_B=$(curl -s -X POST $BASE/api/v1/login -H "$J" -d '{"username":"bob","password":"demo-password-bob"}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')
echo "got tokens (not printed)"

echo; echo "== 3. Create a note as alice (valid)"
curl -si -X POST $BASE/api/v1/notes -H "$J" -H "Authorization: Bearer $TOKEN_A" -d '{"title":"Groceries","body":"milk, eggs"}' | tee /tmp/create.out | sed -n '1p;/Location/p;/X-Request-ID/p'
NOTE_ID=$(tail -n1 /tmp/create.out | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')
tail -n1 /tmp/create.out | pp

echo; echo "== 4. Mass-assignment attempt (extra field) -> 400"
curl -s -X POST $BASE/api/v1/notes -H "$J" -H "Authorization: Bearer $TOKEN_A" -d '{"title":"x","owner_id":"u-1002"}' | pp

echo; echo "== 5. Bob tries to read alice's note -> 404 (same as missing)"
curl -s $BASE/api/v1/notes/$NOTE_ID -H "Authorization: Bearer $TOKEN_B" | pp

echo; echo "== 6. Alice reads her own note -> 200, only public fields"
curl -s $BASE/api/v1/notes/$NOTE_ID -H "Authorization: Bearer $TOKEN_A" | pp

echo; echo "== 7. Deprecated v0 shows Deprecation/Sunset headers"
curl -si $BASE/api/v0/notes -H "Authorization: Bearer $TOKEN_A" | sed -n '1p;/^Deprecation/p;/^Sunset/p;/^Link/p'

echo; echo "== 8. Rate limit on login (6 quick bad attempts)"
for i in 1 2 3 4 5 6; do
  curl -s -o /dev/null -w "attempt $i -> %{http_code}\n" -X POST $BASE/api/v1/login -H "$J" -d '{"username":"alice","password":"wrong"}'
done
