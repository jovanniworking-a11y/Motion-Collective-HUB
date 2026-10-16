import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MOTION — CH31 Production",
  description: "The working plan: equipment, workflow and a considered production budget.",
  other: {
    "codex-preview": "development",
  },
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
