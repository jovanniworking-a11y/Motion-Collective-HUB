/**
 * Preload bridge for MOTION Ops desktop.
 * Keep the surface small; the web panel owns UI state.
 */
const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("motionOpsDesktop", {
  platform: process.platform,
  getTarget: () => ipcRenderer.invoke("motion-ops:get-target"),
  openExternal: (url) => ipcRenderer.invoke("motion-ops:open-external", url),
});
