import { expect, test } from "@playwright/test";

// T-036 · Night-Of readiness: cap 70, counts survive a reload, the door works offline.
test.skip(!!process.env.MOTION_E2E_AUTH, "runs in the open (no-login) e2e pass");

const KEY = "motion-night-ops-v1";

test("door cap is 70 passes, confirmed", async ({ page }) => {
  await page.goto("/night-of");
  await expect(page.getByTestId("checkin-panel")).toBeVisible();
  await expect(page.getByTestId("pass-70")).toBeVisible();
  await expect(page.getByTestId("pass-71")).toHaveCount(0);
  await expect(page.locator("#statIn")).toContainText("of 70 cap");
  await expect(page.locator("#statIn")).toContainText(/confirmed/i);
});

test("check-ins survive a reload", async ({ page }) => {
  await page.goto("/night-of");
  await page.evaluate((k) => localStorage.removeItem(k), KEY);
  await page.reload();
  await page.getByTestId("pass-12").click();
  await page.getByTestId("pass-13").click();
  await expect(page.getByTestId("count-in")).toHaveText("2");
  await page.reload();
  await expect(page.getByTestId("count-in")).toHaveText("2");
  await expect(page.getByTestId("pass-12")).toHaveAttribute("aria-pressed", "true");
});

test("at cap: room left 0, tile goes hot", async ({ page }) => {
  await page.goto("/night-of");
  await page.evaluate((k) => {
    const checked = Array.from({ length: 70 }, (_, i) => i + 1);
    localStorage.setItem(k, JSON.stringify({ checked, welfareLog: {}, clockMode: "live", clockOffsetMin: 0 }));
  }, KEY);
  await page.reload();
  await expect(page.getByTestId("count-in")).toHaveText("70");
  await expect(page.locator("#statIn")).toHaveClass(/hot/);
  await expect(page.locator(".stat").nth(1)).toContainText("0");
});

test("door keeps working offline after one visit", async ({ page, context }) => {
  await page.goto("/night-of");
  await page.evaluate(async () => {
    await navigator.serviceWorker.ready;
  });
  // Second load goes through the service worker and caches the page.
  await page.reload();
  await page.waitForFunction(async () => {
    const keys = await caches.keys();
    for (const k of keys) {
      const c = await caches.open(k);
      if (await c.match("/night-of")) return true;
    }
    return false;
  });
  await context.setOffline(true);
  await page.reload();
  await expect(page.getByTestId("checkin-panel")).toBeVisible();
  await page.getByTestId("pass-40").click();
  await expect(page.getByTestId("pass-40")).toHaveAttribute("aria-pressed", "true");
  await context.setOffline(false);
});
