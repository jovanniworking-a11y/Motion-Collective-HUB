// @agent-provenance [2026-10-24T21:04:59Z] [agent:claude-code] [status:completed/verified_passed] [trace:tr_2dc2267e68024731]
// @summary: Close the four provenance limits: shared leases, guest denylist, coverage gate, agent registry
// @handoff: Jovanni: set MOTION_AGENT_TOKEN on Vercel api + GitHub secrets MOTION_API_URL/MOTION_AGENT_TOKEN; optional GUEST_DENYLIST
import { expect, test } from "@playwright/test";

// Activity shows cross-machine leases and the agent work log (API mocked; the API has its own tests).
test.skip(!!process.env.MOTION_E2E_AUTH, "runs in the open (no-login) e2e pass");

test("activity lists who is editing what and recent agent stamps", async ({ page }) => {
  const now = Date.now() / 1000;
  await page.route("**/api/activity", (r) =>
    r.fulfill({ json: { feed: [], board_count: 3, outbox_count: 1, live_count: 0, label: "confirmed" } }),
  );
  await page.route("**/api/agentops/leases", (r) =>
    r.fulfill({
      json: {
        leases: [
          { resource: "live-ops/fader/server.py", owner: "grok-jerry", lease_id: "ls_1", acquired_at: now, expires_at: now + 300, ttl: 900 },
        ],
      },
    }),
  );
  await page.route("**/api/agentops/stamps**", (r) =>
    r.fulfill({
      json: {
        source: "database",
        stamps: [
          {
            timestamp_utc: "2026-10-24T20:00:00.000Z", agent_id: "cursor", target_uri: "apps/ops-panel/src/lib/api.ts",
            status: "completed", verification_status: "verified_passed", intent: "Same-origin API base",
            trace_id: "tr_abc", next: "Re-run e2e after deploy", failure_reason: null,
          },
        ],
      },
    }),
  );
  await page.goto("/activity");
  await expect(page.getByTestId("agent-leases")).toContainText("live-ops/fader/server.py");
  await expect(page.getByTestId("agent-leases")).toContainText("@grok-jerry");
  await expect(page.getByTestId("agent-stamps")).toContainText("Same-origin API base");
  await expect(page.getByTestId("agent-stamps")).toContainText("completed / passed");
  await page.screenshot({ path: "test-results/activity.png", fullPage: true });
});
