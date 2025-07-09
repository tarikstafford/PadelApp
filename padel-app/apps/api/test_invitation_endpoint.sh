#!/bin/bash

echo "Testing Game Invitation Endpoint"
echo "================================"

# Test token from user
TOKEN="r1D6pEsTGh4xmouDDzKfFBhLbw4cNfAflVf8caD7Ovg"
URL="https://padelgo-backend-production.up.railway.app/api/v1/games/invitations/${TOKEN}/info"

echo "Testing URL: $URL"
echo ""

# Make the request with verbose output
echo "Response:"
curl -v "$URL" 2>&1 | grep -E "(< HTTP|< |{|detail)"

echo ""
echo "================================"
echo "Testing with a fake token to see error handling:"
FAKE_TOKEN="fake-token-123"
FAKE_URL="https://padelgo-backend-production.up.railway.app/api/v1/games/invitations/${FAKE_TOKEN}/info"

echo "Testing URL: $FAKE_URL"
echo ""
curl -s "$FAKE_URL" | jq .

echo ""
echo "================================"
echo "Testing root endpoint to verify API is running:"
curl -s "https://padelgo-backend-production.up.railway.app/" | jq .