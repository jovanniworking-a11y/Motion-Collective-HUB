"use client";

import { Suspense, useState } from "react";
import { useSearchParams } from "next/navigation";

function safeNext(raw: string | null): string {
  return raw && raw.startsWith("/") && !raw.startsWith("//") && !raw.startsWith("/login") ? raw : "/";
}

function LoginForm() {
  const params = useSearchParams();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    setBusy(true);
    setError("");
    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: form.get("username"),
          password: form.get("password"),
          code: form.get("code"),
        }),
      });
      const data = (await res.json().catch(() => ({}))) as { ok?: boolean; error?: string };
      if (res.ok && data.ok) {
        window.location.assign(safeNext(params.get("next")));
        return;
      }
      setError(data.error || "Login failed.");
    } catch {
      setError("Network error.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="login panel" data-testid="login">
      <h1>MOTION Ops</h1>
      <p className="caps dim">Crew only · password + 6-digit code</p>
      <form onSubmit={onSubmit}>
        <label>
          Name
          <input name="username" autoComplete="username" required data-testid="login-user" />
        </label>
        <label>
          Password
          <input name="password" type="password" autoComplete="current-password" required data-testid="login-pass" />
        </label>
        <label>
          Authenticator code
          <input
            name="code"
            inputMode="numeric"
            pattern="[0-9]{6}"
            maxLength={6}
            autoComplete="one-time-code"
            required
            data-testid="login-code"
          />
        </label>
        {error ? (
          <p role="alert" className="login-error" data-testid="login-error">
            {error}
          </p>
        ) : null}
        <button type="submit" disabled={busy} data-testid="login-submit">
          {busy ? "Checking…" : "Log in"}
        </button>
      </form>
    </section>
  );
}

export default function LoginPage() {
  return (
    <Suspense>
      <LoginForm />
    </Suspense>
  );
}
