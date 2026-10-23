import { defineConfig, devices } from "@playwright/test";

const PORT = Number(process.env.PORT || 3100);
const BASE = `http://127.0.0.1:${PORT}`;

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: "list",
  use: {
    baseURL: BASE,
    trace: "on-first-retry",
    // Optional: point at a preinstalled browser when the bundled revision isn't downloaded.
    launchOptions: process.env.PW_CHROMIUM_PATH ? { executablePath: process.env.PW_CHROMIUM_PATH } : {},
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: {
    command: process.env.MOTION_E2E_AUTH
      ? `node e2e/auth-env.mjs npm run start -- -p ${PORT}`
      : `npm run start -- -p ${PORT}`,
    url: BASE,
    reuseExistingServer: !process.env.CI && !process.env.MOTION_E2E_AUTH,
    timeout: 120_000,
  },
});
