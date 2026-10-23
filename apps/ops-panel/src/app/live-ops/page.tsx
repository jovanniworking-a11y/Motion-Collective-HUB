import type { Metadata } from "next";
import { LiveOpsClient } from "@/components/live-ops/LiveOpsClient";

export const metadata: Metadata = {
  title: "MOTION · Live Ops",
  description: "Night-of live ops: door counter status, zone counts, HQ, run of show.",
};

export default function LiveOpsPage() {
  return <LiveOpsClient />;
}
