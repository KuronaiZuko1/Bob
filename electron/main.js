const { app, BrowserWindow, shell, ipcMain } = require('electron')
const path  = require('path')
const { spawn } = require('child_process')

// ── Config ──────────────────────────────────────────────────
const BACKEND_PORT = 8000
const FRONTEND_DEV_URL = 'http://localhost:5173'
const IS_DEV = process.env.NODE_ENV === 'development' || !app.isPackaged

let mainWindow = null
let backendProcess = null

// ── Backend startup ──────────────────────────────────────────
function startBackend() {
  // Resolve paths relative to the workspace root
  const workspaceRoot = IS_DEV
    ? path.resolve(__dirname, '..')           // electron/ → workspace root
    : path.resolve(process.resourcesPath, 'backend')

  const pythonExe = IS_DEV
    ? path.join(workspaceRoot, '.venv', 'Scripts', 'python.exe')
    : path.join(workspaceRoot, '.venv', 'Scripts', 'python.exe')

  const runScript = path.join(workspaceRoot, 'backend', 'run.py')

  console.log('[BOB] Starting backend…')
  console.log('[BOB] Python:', pythonExe)
  console.log('[BOB] Script:', runScript)

  backendProcess = spawn(pythonExe, [runScript], {
    cwd: workspaceRoot,
    env: { ...process.env },
    stdio: ['ignore', 'pipe', 'pipe'],
  })

  backendProcess.stdout.on('data', (data) => {
    process.stdout.write(`[backend] ${data}`)
  })

  backendProcess.stderr.on('data', (data) => {
    process.stderr.write(`[backend] ${data}`)
  })

  backendProcess.on('close', (code) => {
    console.log(`[BOB] Backend exited with code ${code}`)
    backendProcess = null
  })

  backendProcess.on('error', (err) => {
    console.error('[BOB] Failed to start backend:', err.message)
  })
}

// ── Wait for backend to be ready ─────────────────────────────
function waitForBackend(retries = 20, delay = 500) {
  return new Promise((resolve, reject) => {
    const http = require('http')
    let attempt = 0

    function tryConnect() {
      attempt++
      const req = http.get(`http://127.0.0.1:${BACKEND_PORT}/api/health`, (res) => {
        resolve()
      })
      req.on('error', () => {
        if (attempt < retries) {
          setTimeout(tryConnect, delay)
        } else {
          reject(new Error('Backend did not start in time'))
        }
      })
      req.setTimeout(1000, () => { req.destroy(); if (attempt < retries) setTimeout(tryConnect, delay) })
    }

    tryConnect()
  })
}

// ── Create main window ───────────────────────────────────────
async function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 820,
    minWidth: 900,
    minHeight: 600,
    backgroundColor: '#0d1117',
    titleBarStyle: 'default',
    title: 'BOB — Job Agent',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: false,
    },
    show: false,
  })

  mainWindow.once('ready-to-show', () => {
    mainWindow.show()
  })

  mainWindow.on('closed', () => { mainWindow = null })

  if (IS_DEV) {
    console.log('[BOB] Development mode — loading Vite dev server')
    await mainWindow.loadURL(FRONTEND_DEV_URL)
    mainWindow.webContents.openDevTools({ mode: 'detach' })
  } else {
    const indexPath = path.join(__dirname, '..', 'frontend', 'dist', 'index.html')
    await mainWindow.loadFile(indexPath)
  }
}

// ── IPC handlers ─────────────────────────────────────────────
ipcMain.handle('open-external', async (_event, url) => {
  await shell.openExternal(url)
})

ipcMain.handle('get-app-version', () => app.getVersion())

// ── App lifecycle ────────────────────────────────────────────
app.whenReady().then(async () => {
  startBackend()

  try {
    console.log('[BOB] Waiting for backend to start…')
    await waitForBackend(30, 500)
    console.log('[BOB] Backend is ready')
  } catch (err) {
    console.warn('[BOB] Backend not ready, loading UI anyway:', err.message)
  }

  await createWindow()
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    if (backendProcess) {
      backendProcess.kill()
    }
    app.quit()
  }
})

app.on('activate', async () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    await createWindow()
  }
})

app.on('before-quit', () => {
  if (backendProcess) {
    console.log('[BOB] Shutting down backend…')
    backendProcess.kill()
  }
})
