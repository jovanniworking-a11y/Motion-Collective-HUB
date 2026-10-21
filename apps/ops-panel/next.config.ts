import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    // Local dev only — never on Vercel (vercel.json handles routing there).
    // Proxies API calls to the FastAPI backend so `next dev` works standalone.
    if (process.env.VERCEL) return [];
    const api = process.env.MOTION_API_DEV_URL || "http://127.0.0.1:8787";
    // Bare collection routes. A `:path*` pattern does not match the path
    // with no extra segment, and the panel calls those roots directly.
    const roots = ["/api/agents", "/api/data", "/api/routing", "/api/sims", "/api/studio"];
    return [
      ...roots.map((source) => ({ source, destination: `${api}${source}` })),
      { source: "/api/agents/:path*", destination: `${api}/api/agents/:path*` },
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
