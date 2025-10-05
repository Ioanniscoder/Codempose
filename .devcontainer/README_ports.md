Devcontainer port forwarding and server

This devcontainer forwards two ports:
- 8888: used by the devcontainer start helper to serve outputs/ by default
- 8000: recommended alternate port for ad-hoc servers (also forwarded)

Behavior:
- The devcontainer `postStartCommand` runs `.devcontainer/devcontainer-start.sh` which generates outputs and starts an HTTP server on port 8888 serving `outputs/`.
- Workspace settings request that forwarded ports 8000 and 8888 be opened in the browser automatically.

If you want to run a custom server instead of the devcontainer helper:

```bash
# example: run a simple python server on 8000
nohup python3 -m http.server 8000 --bind 0.0.0.0 --directory outputs > /tmp/outputs_http.log 2>&1 &
```

Security note:
- Forwarding ports makes them accessible to your Codespace/devcontainer UI and (if made public) to the internet. Only expose what you intend to share.
