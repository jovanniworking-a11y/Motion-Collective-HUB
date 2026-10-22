import type { Metadata } from "next";
import { CounterDemoClient } from "@/components/counter-demo/CounterDemoClient";

export const metadata: Metadata = {
  title: "MOTION · People Counter",
  description: "Live in-browser people counter demo. Frames never leave the device.",
};

export default function CounterDemoPage() {
  return <CounterDemoClient />;
}
