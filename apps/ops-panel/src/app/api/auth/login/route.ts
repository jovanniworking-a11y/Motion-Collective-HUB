import { NextResponse } from "next/server";
import { SESSION_COOKIE, SESSION_TTL_SEC, authMode, signSession } from "@/lib/auth/session";
import { verifyTotp } from "@/lib/auth/totp";
import { loadUsers, verifyPassword } from "@/lib/auth/users";
import { clearFails, isLocked, recordFail, stepReplayed } from "@/lib/auth/limits";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const DENIED = { ok: false, error: "Wrong name, password or code." };

export async function POST(req: Request) {
  if (authMode() !== "on") {
    return NextResponse.json({ ok: false, error: "Login is not configured." }, { status: 503 });
  }
  let body: { username?: unknown; password?: unknown; code?: unknown };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json(DENIED, { status: 400 });
  }
  const username = typeof body.username === "string" ? body.username.trim().toLowerCase() : "";
  const password = typeof body.password === "string" ? body.password : "";
  const code = typeof body.code === "string" ? body.code.replace(/\s/g, "") : "";
  const ip = (req.headers.get("x-forwarded-for") || "").split(",")[0].trim() || "local";
  const keys = [`ip:${ip}`, `u:${username}`];

  if (keys.some((k) => isLocked(k))) {
    return NextResponse.json({ ok: false, error: "Too many tries. Wait 15 minutes." }, { status: 429 });
  }

  const user = loadUsers().find((u) => u.u.toLowerCase() === username);
  const pwOk = verifyPassword(password, user?.pw);
  const step = user && pwOk ? verifyTotp(user.totp, code) : null;
  if (!user || !pwOk || step === null || stepReplayed(user.u, step)) {
    keys.forEach((k) => recordFail(k));
    return NextResponse.json(DENIED, { status: 401 });
  }
  keys.forEach((k) => clearFails(k));

  const token = await signSession(user.u, process.env.MOTION_SESSION_SECRET || "");
  const res = NextResponse.json({ ok: true, user: user.u });
  res.cookies.set(SESSION_COOKIE, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production" && !process.env.MOTION_INSECURE_COOKIE,
    sameSite: "strict",
    path: "/",
    maxAge: SESSION_TTL_SEC,
  });
  return res;
}
