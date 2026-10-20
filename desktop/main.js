/**
 * MOTION Ops — Electron main process (Discord-like desktop shell).
 *
 * Target resolution order:
 * 1. MOTION_OPS_URL (explicit)
 * 2. apps/ops-panel on localhost:3000 when reachable (or MOTION_OPS_FALLBACK=panel)
 * 3. Local static server for repo ops/ Night-Of page
 * 4. Built-in shell/fallback.html placeholder
 *
 * Smoke: MOTION_OPS_SMOKE=1 boots, resolves target, exits 0 (no GUI required).
 */
const {
  app,
  BrowserWindow,
  Tray,
  Menu,
  nativeImage,
  shell,
  ipcMain,
  dialog,
} = require("electron");
const http = require("http");
const fs = require("fs");
const path = require("path");
const { pathToFileURL } = require("url");

const REPO_ROOT = path.resolve(__dirname, "..");
const OPS_DIR = path.join(REPO_ROOT, "ops");
const PANEL_DIR = path.join(REPO_ROOT, "apps", "ops-panel");
const FALLBACK_HTML = path.join(__dirname, "shell", "fallback.html");
const DEFAULT_PANEL_URL = process.env.MOTION_OPS_PANEL_URL || "http://localhost:3000";
const SMOKE = process.env.MOTION_OPS_SMOKE === "1";
const FORCE = (process.env.MOTION_OPS_FALLBACK || "").toLowerCase();

/** @type {BrowserWindow | null} */
let mainWindow = null;
/** @type {Tray | null} */
let tray = null;
/** @type {http.Server | null} */
let staticServer = null;
let resolvedTarget = { kind: "pending", url: "" };

const gotLock = app.requestSingleInstanceLock();
if (!gotLock) {
  app.quit();
} else {
  app.on("second-instance", () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.show();
      mainWindow.focus();
    }
  });
}

function mimeFor(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  return (
    {
      ".html": "text/html; charset=utf-8",
      ".js": "text/javascript; charset=utf-8",
      ".css": "text/css; charset=utf-8",
      ".json": "application/json",
      ".webmanifest": "application/manifest+json",
      ".svg": "image/svg+xml",
      ".png": "image/png",
      ".ico": "image/x-icon",
      ".woff2": "font/woff2",
    }[ext] || "application/octet-stream"
  );
}

function startStaticServer(rootDir) {
  return new Promise((resolve, reject) => {
    const server = http.createServer((req, res) => {
      try {
        const raw = decodeURIComponent((req.url || "/").split("?")[0]);
        let rel = raw === "/" ? "/index.html" : raw;
        const filePath = path.normalize(path.join(rootDir, rel));
        if (!filePath.startsWith(rootDir)) {
          res.writeHead(403);
          res.end("Forbidden");
          return;
        }
        if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
          res.writeHead(404);
          res.end("Not found");
          return;
        }
        res.writeHead(200, { "Content-Type": mimeFor(filePath) });
        fs.createReadStream(filePath).pipe(res);
      } catch (err) {
        res.writeHead(500);
        res.end(String(err));
      }
    });
    server.listen(0, "127.0.0.1", () => {
      const { port } = server.address();
      staticServer = server;
      resolve(`http://127.0.0.1:${port}/`);
    });
    server.on("error", reject);
  });
}

function httpReachable(url, timeoutMs = 800) {
  return new Promise((resolve) => {
    let settled = false;
    const done = (ok) => {
      if (settled) return;
      settled = true;
      resolve(ok);
    };
    try {
      const req = http.get(url, { timeout: timeoutMs }, (res) => {
        res.resume();
        done(res.statusCode !== undefined && res.statusCode < 500);
      });
      req.on("timeout", () => {
        req.destroy();
        done(false);
      });
      req.on("error", () => done(false));
    } catch {
      done(false);
    }
  });
}

async function resolveTarget() {
  if (process.env.MOTION_OPS_URL) {
    return { kind: "url", url: process.env.MOTION_OPS_URL };
  }

  if (FORCE === "shell") {
    return { kind: "shell", url: pathToFileURL(FALLBACK_HTML).href };
  }

  if (FORCE === "night-of" || FORCE === "ops") {
    if (fs.existsSync(path.join(OPS_DIR, "index.html"))) {
      const url = await startStaticServer(OPS_DIR);
      return { kind: "night-of", url };
    }
  }

  const panelExists = fs.existsSync(path.join(PANEL_DIR, "package.json"));
  if (FORCE === "panel" || (!FORCE && panelExists)) {
    if (await httpReachable(DEFAULT_PANEL_URL)) {
      return { kind: "panel", url: DEFAULT_PANEL_URL };
    }
    if (FORCE === "panel") {
      // Panel forced but not up yet — still open the URL so Electron can retry/reload.
      return { kind: "panel-waiting", url: DEFAULT_PANEL_URL };
    }
  }

  if (fs.existsSync(path.join(OPS_DIR, "index.html"))) {
    const url = await startStaticServer(OPS_DIR);
    return { kind: "night-of", url };
  }

  return { kind: "shell", url: pathToFileURL(FALLBACK_HTML).href };
}

function trayIcon() {
  // 16x16 red accent square on dark — readable in most trays without external assets.
  const size = 16;
  const buf = Buffer.alloc(size * size * 4);
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const i = (y * size + x) * 4;
      const edge = x === 0 || y === 0 || x === size - 1 || y === size - 1;
      if (edge) {
        buf[i] = 6;
        buf[i + 1] = 11;
        buf[i + 2] = 19;
        buf[i + 3] = 255;
      } else if (x >= 5 && x <= 10 && y >= 5 && y <= 10) {
        buf[i] = 255;
        buf[i + 1] = 59;
        buf[i + 2] = 48;
        buf[i + 3] = 255;
      } else {
        buf[i] = 26;
        buf[i + 1] = 36;
        buf[i + 2] = 51;
        buf[i + 3] = 255;
      }
    }
  }
  return nativeImage.createFromBuffer(buf, { width: size, height: size });
}

function buildTray() {
  tray = new Tray(trayIcon());
  tray.setToolTip("MOTION Ops");
  const menu = Menu.buildFromTemplate([
    {
      label: "Show MOTION Ops",
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.focus();
        }
      },
    },
    {
      label: "Reload",
      click: () => mainWindow && mainWindow.reload(),
    },
    { type: "separator" },
    {
      label: "Quit",
      click: () => {
        app.isQuitting = true;
        app.quit();
      },
    },
  ]);
  tray.setContextMenu(menu);
  tray.on("click", () => {
    if (!mainWindow) return;
    if (mainWindow.isVisible()) mainWindow.hide();
    else {
      mainWindow.show();
      mainWindow.focus();
    }
  });
}

function createWindow(targetUrl) {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 960,
    minHeight: 640,
    title: "MOTION Ops",
    backgroundColor: "#060B13",
    show: !SMOKE,
    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });

  mainWindow.on("close", (e) => {
    if (!app.isQuitting && !SMOKE && process.platform !== "darwin") {
      e.preventDefault();
      mainWindow.hide();
    }
  });

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: "deny" };
  });

  return mainWindow.loadURL(targetUrl);
}

ipcMain.handle("motion-ops:get-target", () => resolvedTarget);
ipcMain.handle("motion-ops:open-external", async (_e, url) => {
  if (typeof url === "string" && /^https?:/i.test(url)) {
    await shell.openExternal(url);
    return true;
  }
  return false;
});

async function boot() {
  app.setName("MOTION Ops");
  if (process.platform === "win32") {
    app.setAppUserModelId("collective.motion.ops");
  }

  resolvedTarget = await resolveTarget();
  console.log(
    `[MOTION Ops] target=${resolvedTarget.kind} url=${resolvedTarget.url}`
  );

  if (SMOKE) {
    // Headless / CI: prove main process + target resolution without needing a display.
    if (staticServer) {
      await new Promise((r) => staticServer.close(() => r()));
      staticServer = null;
    }
    console.log("[MOTION Ops] smoke OK");
    app.exit(0);
    return;
  }

  await createWindow(resolvedTarget.url);
  buildTray();

  if (resolvedTarget.kind === "panel-waiting") {
    dialog.showMessageBox(mainWindow, {
      type: "info",
      title: "MOTION Ops",
      message: "Ops panel not reachable yet",
      detail:
        `Start the Next app:\n  cd apps/ops-panel && npm run dev\n\nThen reload this window.\nExpected: ${DEFAULT_PANEL_URL}`,
    });
  }
}

app.whenReady().then(boot).catch((err) => {
  console.error("[MOTION Ops] boot failed", err);
  app.exit(1);
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    // Stay alive in tray like Discord unless quitting.
    if (app.isQuitting) app.quit();
  }
});

app.on("activate", () => {
  if (mainWindow) mainWindow.show();
});

app.on("before-quit", () => {
  app.isQuitting = true;
  if (staticServer) {
    staticServer.close();
    staticServer = null;
  }
});
