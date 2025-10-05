#!/bin/bash
# fix_browser.sh - Start HTTP server and open browser to view PDF outputs
# This script makes port 8888 public and opens the outputs directory in the browser

echo "🌐 Starting HTTP server on port 8888..."
echo "📁 Serving workspace directory: $(pwd)"
echo ""

# Start the HTTP server in the background
python3 -m http.server 8888 --bind 0.0.0.0 &
SERVER_PID=$!

echo "✅ Server started (PID: $SERVER_PID)"
echo ""
echo "📋 To view your outputs:"
echo "   1. Go to the PORTS tab in VS Code"
echo "   2. Find port 8888"
echo "   3. Right-click and select 'Port Visibility' → 'Public'"
echo "   4. Click the globe icon to open in browser"
echo "   5. Navigate to /outputs/ to view PDF files"
echo ""
echo "🌐 Or use the forwarded URL and append '/outputs/first.pdf'"
echo ""
echo "To stop the server, run: kill $SERVER_PID"
echo "Or press Ctrl+C if running in foreground"

# Keep the script running so you can see the server logs
wait $SERVER_PID
