import { readFile } from "fs/promises";
import path from "path";

/** Booth dashboard. Next does not serve public/hq/index.html at /hq. */
export async function GET() {
  const html = await readFile(
    path.join(process.cwd(), "public", "hq", "index.html"),
    "utf8",
  );
  return new Response(html, {
    headers: {
      "content-type": "text/html; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}
