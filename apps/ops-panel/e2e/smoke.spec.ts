import { expect, test } from "@playwright/test";

test.describe("MOTION ops panel smoke", () => {
  test("dashboard loads with brand + status tiles", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: /Devil/i })).toBeVisible();
    await expect(page.getByTestId("status-tiles")).toBeVisible();
    await expect(page.getByTestId("doors-countdown")).toBeVisible();
  });

  test("check-in increments count", async ({ page }) => {
    await page.goto("/night-of");
    await expect(page.getByTestId("checkin-panel")).toBeVisible();
    const before = Number(await page.getByTestId("count-in").innerText());
    await page.getByTestId("pass-3").click();
    await expect(page.getByTestId("count-in")).toHaveText(String(before + 1));
    await expect(page.getByTestId("pass-3")).toHaveAttribute(
      "aria-pressed",
      "true",
    );
  });

  test("welfare log marks a round done", async ({ page }) => {
    await page.goto("/night-of");
    await page.getByRole("tab", { name: "Welfare" }).click();
    await expect(page.getByTestId("welfare-panel")).toBeVisible();
    await page.getByTestId("log-round").click();
    await expect(page.locator(".round.done").first()).toBeVisible();
  });

  test("Claude assist route returns 200", async ({ request, page }) => {
    const health = await request.get("/api/claude");
    expect(health.status()).toBe(200);
    const body = await health.json();
    expect(body.ok).toBe(true);

    const post = await request.post("/api/claude", {
      data: { message: "What is the budget pool?" },
    });
    expect(post.status()).toBe(200);
    const data = await post.json();
    expect(data.ok).toBe(true);
    expect(String(data.reply)).toMatch(/450/);

    await page.goto("/assist");
    await expect(page.getByTestId("pro-bridge")).toBeVisible();
    await expect(page.getByTestId("pro-bridge-open")).toBeVisible();
    await expect(page.getByTestId("pro-bridge-copy")).toBeVisible();
    await expect(page.getByTestId("claude-mode")).toContainText(/Pro bridge|API/i);
    await page.getByTestId("claude-input").fill("lineup order");
    await page.getByTestId("claude-send").click();
    await expect(page.getByTestId("chat-log")).toContainText(/iamariology|Rohan Rali|HE\/\//i, {
      timeout: 10_000,
    });
  });
});
