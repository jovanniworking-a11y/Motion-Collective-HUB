// @agent-provenance [2026-10-24T21:04:59Z] [agent:claude-code] [status:completed/verified_passed] [trace:tr_9d45d0d3268c46b3]
// @summary: Close the four provenance limits: shared leases, guest denylist, coverage gate, agent registry
// @handoff: Jovanni: set MOTION_AGENT_TOKEN on Vercel api + GitHub secrets MOTION_API_URL/MOTION_AGENT_TOKEN; optional GUEST_DENYLIST
import type { NextConfig } from "next";

const securityHeaders = [
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "X-Frame-Options", value: "SAMEORIGIN" },
  { key: "Referrer-Policy", value: "same-origin" },
  { key: "Strict-Transport-Security", value: "max-age=31536000; includeSubDomains" },
  { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
  { key: "X-Robots-Tag", value: "noindex, nofollow" },
];

const nextConfig: NextConfig = {
  poweredByHeader: false,
  async headers() {
    return [{ source: "/(.*)", headers: securityHeaders }];
  },
  async rewrites() {
    // Local dev only — never on Vercel (vercel.json handles routing there).
    // Proxies API calls to the FastAPI backend so `next dev` works standalone.
    if (process.env.VERCEL) return [];
    const api = process.env.MOTION_API_DEV_URL || "http://127.0.0.1:8787";
    // Bare collection routes. A `:path*` pattern does not match the path
    // with no extra segment, and the panel calls those roots directly.
    const roots = ["/api/agents", "/api/agentops", "/api/data", "/api/routing", "/api/sims", "/api/studio"];
    return [
      ...roots.map((source) => ({ source, destination: `${api}${source}` })),
      { source: "/api/agents/:path*", destination: `${api}/api/agents/:path*` },
      { source: "/api/agentops/:path*", destination: `${api}/api/agentops/:path*` },
      { source: "/api/data/:path*", destination: `${api}/api/data/:path*` },
      { source: "/api/routing/:path*", destination: `${api}/api/routing/:path*` },
      { source: "/api/sims/:path*", destination: `${api}/api/sims/:path*` },
      { source: "/api/studio/:path*", destination: `${api}/api/studio/:path*` },
      { source: "/api/activity", destination: `${api}/api/activity` },
      { source: "/api/usage", destination: `${api}/api/usage` },
      { source: "/health", destination: `${api}/health` },
      { source: "/studio/embed", destination: `${api}/studio/embed` },
    ];
  },
};

export default nextConfig;
