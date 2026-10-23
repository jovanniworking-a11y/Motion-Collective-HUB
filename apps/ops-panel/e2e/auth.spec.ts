import { expect, test } from "@playwright/test";
import { createHmac } from "node:crypto";

// Runs only via `npm run test:e2e:auth` (server started with a test user; see playwright.config.ts).
test.skip(!process.env.MOTION_E2E_AUTH, "auth e2e runs with MOTION_E2E_AUTH=1");

const B32 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";
function code(secretB32: string, offsetSteps = 0): string {
  let bits = 0, value = 0;
  const bytes: number[] = [];
  for (const ch of secretB32) {
    value = (value << 5) | B32.indexOf(ch); bits += 5;
    if (bits >= 8) { bytes.push((value >>> (bits - 8)) & 255); bits -= 8; }
  }
  const msg = Buffer.alloc(8);
  msg.writeBigUInt64BE(BigInt(Math.floor(Date.now() / 30000) + offsetSteps));
  const h = createHmac("sha1", Buffer.from(bytes)).update(msg).digest();
  const o = h[h.length - 1] & 15;
  return String((h.readUInt32BE(o) & 0x7fffffff) % 1e6).padStart(6, "0");
}

const TOTP = process.env.E2E_TOTP || "";

test.describe.configure({ mode: "serial" });

test("locked out without a session", async ({ page, request }) => {
  await page.goto("/night-of");
  await expect(page).toHaveURL(/\/login\?next=%2Fnight-of/);
  await expect(page.getByTestId("login")).toBeVisible();
  expect((await request.get("/api/claude")).status()).toBe(401);
  for (const path of ["/live-ops", "/hq", "/counter-demo", "/data", "/hq/index.html"]) {
    const res = await request.get(path, { maxRedirects: 0 });
    expect([307, 308], path).toContain(res.status());
    expect(res.headers()["location"] || "", path).toContain("/login");
  }
});

test("wrong code is refused", async ({ page }) => {
  await page.goto("/login");
  await page.getByTestId("login-user").fill("crewtest");
  await page.getByTestId("login-pass").fill("e2e-password-123");
  await page.getByTestId("login-code").fill("000000");
  await page.getByTestId("login-submit").click();
  await expect(page.getByTestId("login-error")).toBeVisible();
  await expect(page).toHaveURL(/\/login/);
});

test("password + code logs in, logout locks again", async ({ page }) => {
  await page.goto("/login?next=/night-of");
  await page.getByTestId("login-user").fill("crewtest");
  await page.getByTestId("login-pass").fill("e2e-password-123");
  await page.getByTestId("login-code").fill(code(TOTP));
  await page.getByTestId("login-submit").click();
  await expect(page).toHaveURL(/\/night-of$/);
  await expect(page.getByTestId("checkin-panel")).toBeVisible();
  await page.getByTestId("logout").click();
  await expect(page).toHaveURL(/\/login/);
  await page.goto("/");
  await expect(page).toHaveURL(/\/login/);
});
