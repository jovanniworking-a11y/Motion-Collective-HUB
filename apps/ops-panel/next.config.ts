import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Standalone output for Docker / Fly / Railway Node images.
  // Vercel ignores this and uses its own builder.
  output: process.env.DOCKER_BUILD === "1" ? "standalone" : undefined,
};

export default nextConfig;
