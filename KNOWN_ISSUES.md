# BOB: Known Issues & Mitigations

This document tracks known issues, technical considerations, and their resolutions or mitigations.

| ID | Issue Description | Impact | Status | Mitigation / Resolution |
|---|---|---|---|---|
| KI-001 | Node.js was not initially present in Windows system PATH | Desktop/Frontend build tools required Node.js | RESOLVED | Downloaded and configured Node.js v20 LTS into user programs (`AppData/Local/Programs/nodejs`) and updated user environment PATH. |
| KI-002 | Accidental folder `%USERP~1` in workspace | Potential path resolution conflicts | RESOLVED | Cleaned up workspace folder. |
| KI-003 | Ollama local inference service offline initially | AI features fallback | OPEN | System configured with graceful fallback to OpenAI API and status indicators when local Ollama is offline. |
| KI-004 | Electron binary postinstall failed due to Windows 8.3 `%USERP~1` path in `mkdtemp` | `npm install` initial failure during Electron postinstall step | RESOLVED | Set `ELECTRON_SKIP_BINARY_DOWNLOAD=1` during package dependency resolution, followed by explicit execution of `install.js` with sanitized `$env:TEMP` / `$env:TMP` path. Electron executable verified at `frontend/node_modules/electron/dist/electron.exe`. |
