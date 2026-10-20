import { NextResponse } from "next/server";
import {
  liveAssist,
  mockAssist,
  resolveMode,
  type AssistRequest,
} from "@/lib/claude";

export const runtime = "nodejs";

export async function POST(req: Request) {
  let body: AssistRequest;
  try {
    body = (await req.json()) as AssistRequest;
  } catch {
    return NextResponse.json(
      { ok: false, mode: resolveMode(), error: "Invalid JSON" },
      { status: 400 },
    );
  }

  const message = typeof body.message === "string" ? body.message : "";
  if (!message.trim()) {
    return NextResponse.json(
      { ok: false, mode: resolveMode(), error: "message required" },
      { status: 400 },
    );
  }

  const mode = resolveMode();

  if (mode === "mock") {
    return NextResponse.json({
      ok: true,
      mode: "mock",
      reply: mockAssist(message),
    });
  }

  try {
    const { reply, model } = await liveAssist(message, body.history);
    return NextResponse.json({ ok: true, mode: "live", reply, model });
  } catch (err) {
    const error = err instanceof Error ? err.message : "Claude request failed";
    /* Fall back to mock so the panel stays usable without spend/failures. */
    return NextResponse.json({
      ok: true,
      mode: "mock",
      reply: `${mockAssist(message)}\n\n(live call failed: ${error})`,
    });
  }
}

export async function GET() {
  return NextResponse.json({
    ok: true,
    mode: resolveMode(),
    hook: "POST /api/claude { message, history? }",
  });
}
