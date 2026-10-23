"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

const NAV = [
  { href: "/", label: "Dash", ico: "01" },
  { href: "/night-of", label: "Night", ico: "02" },
  { href: "/agents", label: "Agents", ico: "#" },
  { href: "/usage", label: "Usage", ico: "◉" },
  { href: "/activity", label: "Live", ico: "◎" },
  { href: "/muse", label: "Muse", ico: "◇" },
  { href: "/data", label: "Data", ico: "▣" },
  { href: "/library", label: "Library", ico: "04" },
  { href: "/assist", label: "Claude", ico: "03" },
] as const;

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const bare = pathname === "/login";
  const [online, setOnline] = useState(true);
  const [apiOk, setApiOk] = useState<boolean | null>(null);

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

  useEffect(() => {
    let cancelled = false;
    api
      .health()
      .then(() => {
        if (!cancelled) setApiOk(true);
      })
      .catch(() => {
        if (!cancelled) setApiOk(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function logout() {
    await fetch("/api/auth/logout", { method: "POST" }).catch(() => {});
    if ("caches" in window) {
      const keys = await caches.keys().catch(() => [] as string[]);
      await Promise.all(keys.map((k) => caches.delete(k)));
    }
    window.location.assign("/login");
  }

  if (bare) return <main className="shell-main">{children}</main>;

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
            <span className="caps dim">
              api {apiOk === null ? "…" : apiOk ? "up" : "down"}
            </span>
            <span className="caps dim">crew · draft only</span>
            <button type="button" className="caps dim logout" onClick={logout} data-testid="logout">
              log out
            </button>
          </div>
        </div>
        <p className="head-sub">
          Devil&apos;s Night · AFTERIMAGE 001 · control plane · never publishes
        </p>
      </header>
      <main className="shell-main">{children}</main>
      <nav className="bottom-nav" aria-label="Ops sections">
        {NAV.map((item) => {
          const active =
            item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
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
