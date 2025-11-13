# How to use curl with Authentication

## Step 1: Login to get access token

```bash
curl -X POST 'http://127.0.0.1:8003/auth/login/' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "your@email.com",
    "password": "yourpassword"
  }'
```

This will return:
```json
{
  "message": "Login successful",
  "access_token": "eyJhbGciOiJIUzI1NiIsImtpZCI6InI5RnM1RVlFT1U4emZ6R0...",
  "user": {...}
}
```

## Step 2: Use the access_token in Authorization header

```bash
# Copy the access_token from Step 1 and use it here
curl -X POST 'http://127.0.0.1:8003/calculate-rizz/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN_HERE' \
  -F 'file=@test1.jpeg;type=image/jpeg'
```

## Complete Example (One-liner)

```bash
# Get token and use it
TOKEN=$(curl -s -X POST 'http://127.0.0.1:8003/auth/login/' \
  -H 'Content-Type: application/json' \
  -d '{"email":"your@email.com","password":"yourpassword"}' | \
  grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

# Use token to calculate rizz
curl -X POST 'http://127.0.0.1:8003/calculate-rizz/' \
  -H 'Authorization: Bearer '"$TOKEN" \
  -F 'file=@test1.jpeg;type=image/jpeg'
```

## Important Notes

- Replace `YOUR_ACCESS_TOKEN_HERE` with the actual token from login
- The Authorization header must be: `Bearer <token>` (with space after "Bearer")
- Make sure your server is running on port 8003
- The file path `test1.jpeg` should be relative to where you run curl, or use full path


