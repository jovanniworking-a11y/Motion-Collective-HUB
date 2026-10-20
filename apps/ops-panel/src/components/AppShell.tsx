"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

const NAV = [
  { href: "/", label: "Dash", ico: "01" },
  { href: "/night-of", label: "Night", ico: "02" },
  { href: "/assist", label: "Claude", ico: "03" },
  { href: "/library", label: "Library", ico: "04" },
] as const;

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [online, setOnline] = useState(true);

  useEffect(() => {
    const sync = () => setOnline(navigator.onLine);
    sync();
    window.addEventListener("online", sync);
    window.addEventListener("offline", sync);
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.register("/sw.js").catch(() => {});
    }
    return () => {
      window.removeEventListener("online", sync);
      window.removeEventListener("offline", sync);
    };
  }, []);

  return (
    <div className="shell">
      <header className="app-head">
        <div className="head-row">
          <Link href="/" className="mark">
            MOTION <span>Ops</span>
          </Link>
          <div className="head-meta">
            <span className={`offline ${online ? "on" : "off"}`}>
              <i />
              {online ? "online" : "offline · local"}
            </span>
            <span className="caps dim">crew · draft only</span>
          </div>
        </div>
        <p className="head-sub">
          Devil&apos;s Night · AFTERIMAGE 001 · never publishes from this panel
        </p>
      </header>
      <main className="shell-main">{children}</main>
      <nav className="bottom-nav" aria-label="Ops sections">
        {NAV.map((item) => {
          const active =
            item.href === "/"
              ? pathname === "/"
              : pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              aria-current={active ? "page" : undefined}
              className={active ? "active" : undefined}
            >
              <span className="ico">{item.ico}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
