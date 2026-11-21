const { contextBridge, ipcRenderer } = require('electron')

// Expose only the APIs we explicitly whitelist
contextBridge.exposeInMainWorld('electronAPI', {
  openExternal: (url) => ipcRenderer.invoke('open-external', url),
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
})
