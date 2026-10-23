import { NextResponse, type NextRequest } from "next/server";
import { SESSION_COOKIE, authMode, verifySession } from "@/lib/auth/session";

const PUBLIC = new Set(["/login", "/api/auth/login", "/manifest.webmanifest", "/sw.js", "/favicon.ico"]);

export async function middleware(req: NextRequest) {
  const mode = authMode();
  if (mode === "off") return NextResponse.next();

  const { pathname, search } = req.nextUrl;
  if (PUBLIC.has(pathname)) return NextResponse.next();

  const isApi = pathname.startsWith("/api/");
  if (mode === "misconfigured") {
    // On Vercel without a proper secret, nothing is served.
    return new NextResponse("Login is not configured (MOTION_SESSION_SECRET).", { status: 503 });
  }

  const session = await verifySession(req.cookies.get(SESSION_COOKIE)?.value, process.env.MOTION_SESSION_SECRET || "");
  if (session) return NextResponse.next();

  if (isApi) return NextResponse.json({ ok: false, error: "login required" }, { status: 401 });
  const url = req.nextUrl.clone();
  url.pathname = "/login";
  url.search = `?next=${encodeURIComponent(pathname + search)}`;
  return NextResponse.redirect(url);
}

export const config = {
  matcher: ["/((?!_next/static|_next/image).*)"],
};
