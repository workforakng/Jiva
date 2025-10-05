#!/bin/bash

cd mobile-app

if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo "📱 Starting Expo on http://localhost:19006"
echo "📲 Scan QR code with Expo Go app"
echo ""

npm start
