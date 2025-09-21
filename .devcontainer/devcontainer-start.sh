#!/usr/bin/env bash
set -euo pipefail

# Devcontainer start helper:
# - run the generation step (project_template.py)
# - start a background http.server bound to 0.0.0.0:8888 if not already running
# - write logs to .devcontainer/devcontainer-start.log and PID to .devcontainer/devcontainer-server.pid

LOGFILE=".devcontainer/devcontainer-start.log"
PIDFILE=".devcontainer/devcontainer-server.pid"

mkdir -p .devcontainer
echo "Starting devcontainer start helper: $(date)" >> "$LOGFILE"

echo "Generating score (project_template.py) ..." | tee -a "$LOGFILE"
if python3 project_template.py >> "$LOGFILE" 2>&1; then
  echo "Generation completed successfully." | tee -a "$LOGFILE"
else
  echo "Generation failed; see $LOGFILE for details. Continuing to server start." | tee -a "$LOGFILE"
fi

# Check if a server is already listening on 8888
if ss -ltnp 2>/dev/null | grep -q ":8888"; then
  echo "HTTP server already running on port 8888." | tee -a "$LOGFILE"
else
  echo "Starting HTTP server on 0.0.0.0:8888 ..." | tee -a "$LOGFILE"
  # Start server in background and record PID
  nohup python3 -m http.server 8888 --bind 0.0.0.0 >> "$LOGFILE" 2>&1 &
  echo $! > "$PIDFILE"
  echo "HTTP server started (PID $(cat $PIDFILE))." | tee -a "$LOGFILE"
fi

echo "Devcontainer start helper finished: $(date)" >> "$LOGFILE"

exit 0
