# CORS Fix Instructions for DocEasy

This document provides instructions for fixing the CORS (Cross-Origin Resource Sharing) issue between the frontend and backend of DocEasy.

## Problem

The frontend deployed at `https://doc-easy.onrender.com` cannot communicate with the backend deployed at `https://doceasy1.onrender.com` due to CORS restrictions. This results in errors like:

```
Access to fetch at 'https://doceasy1.onrender.com/api/auth/ping' from origin 'https://doc-easy.onrender.com' has been blocked by CORS policy: Response to preflight request doesn't pass access control check: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## Solution

We've made the following changes to fix the CORS issue:

1. Added `https://doc-easy.onrender.com` to the allowed origins in the CORS configuration
2. Added explicit CORS headers to critical endpoints
3. Added proper handling for OPTIONS preflight requests
4. Created a CORS configuration helper module
5. Ensured the `sys` module is imported (required for the `--without-threads` argument)

## Files Modified

1. `app.py` - Updated CORS configuration and added after_request/before_request handlers
2. `routes.py` - Added OPTIONS method and CORS headers to critical endpoints
3. Created `cors_config.py` - Helper functions for CORS headers

## Deployment Instructions

### Option 1: Using Render Dashboard

1. Commit your changes to your Git repository
2. Push the changes to your repository connected to Render
3. Render will automatically deploy the changes

Or manually trigger a deployment:

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Select your backend service
3. Click "Manual Deploy" and select "Deploy latest commit"

### Option 2: Using Render CLI (if installed)

Run the following command:

```bash
render deploy
```

## Testing the Fix

After deployment, test the connection between frontend and backend:

1. Open the frontend at `https://doc-easy.onrender.com`
2. Open browser developer tools (F12)
3. Check the Network tab
4. Verify that API calls to `https://doceasy1.onrender.com` succeed without CORS errors

## Troubleshooting

If you encounter a "sys is not defined" error:
1. Verify that `import sys` is at the top of your app.py file
2. Redeploy the application
3. Check the Render logs for any additional errors

## Additional CORS Resources

- [MDN Web Docs: CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [Flask-CORS Documentation](https://flask-cors.readthedocs.io/en/latest/)
- [Render CORS Configuration Guide](https://render.com/docs/cors) 