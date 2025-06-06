#!/bin/bash

# Restart script for the backend service on Render

echo "Restarting DocEasy backend service..."

# For Render, manual restart is done via the dashboard or API
echo "Please visit your Render dashboard and manually restart the service."
echo "URL: https://dashboard.render.com/"
echo ""
echo "Alternatively, if you have the Render CLI installed, you can use:"
echo "render restart srv-xxxx"
echo ""
echo "Important checks after restart:"
echo "1. Check if the root path (/) returns a proper JSON response"
echo "2. Check if /api/register redirects correctly"
echo "3. Verify CORS is working with your frontend"
echo ""
echo "If you're still seeing 404s, make sure the app is properly detecting port 10000 (as seen in logs)"
echo "Add this to your app.py start code if needed:"
echo 'port = int(os.getenv("PORT", 10000))'
echo ""
echo "Remember to commit and push any changes before redeploying!" 