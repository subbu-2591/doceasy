#!/bin/bash

# This script helps redeploy the backend with the CORS fixes

echo "Deploying DocEasy backend with CORS fixes..."

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "Git is not installed. Please install git first."
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree &> /dev/null; then
    echo "Initializing git repository..."
    git init
fi

# Add all changes
git add .

# Commit changes
git commit -m "Fix CORS issues for frontend-backend communication"

# Check if render CLI is installed (optional)
if command -v render &> /dev/null; then
    echo "Using Render CLI to deploy..."
    render deploy
    echo "Deployment triggered via Render CLI."
else
    echo "Render CLI not found. Please manually deploy by pushing to your Git repository connected to Render."
    echo "Instructions:"
    echo "1. Push your changes to your Git repository"
    echo "2. Render will automatically deploy the changes"
    echo ""
    echo "Or you can manually deploy from the Render dashboard:"
    echo "1. Go to https://dashboard.render.com/"
    echo "2. Select your backend service"
    echo "3. Click 'Manual Deploy' and select 'Deploy latest commit'"
fi

echo ""
echo "CORS Configuration Summary:"
echo "- Added explicit CORS headers to auth endpoints"
echo "- Added preflight request handling for OPTIONS requests"
echo "- Added https://doc-easy.onrender.com to allowed origins"
echo ""
echo "After deployment, test the connection between frontend and backend."
echo "The frontend should now be able to communicate with the backend API." 