#!/bin/bash

echo "🔐 Fetching secrets from AWS..."

# Fetch secrets and export as env variables
export $(aws secretsmanager get-secret-value \
  --secret-id prod/capstone/db_credentials \
  --region eu-north-1 \
  --query SecretString \
  --output text | jq -r 'to_entries|map("\(.key)=\(.value)")|.[]')

echo "✅ Secrets loaded"

# Debug (optional)
echo "DB_HOST=$DB_HOST"
echo "DB_USER=$DB_USER"

echo "🚀 Starting Docker containers..."

docker-compose up -d --build
