// Usage: npm run auth:add-user -- <name>
// Prompts for a password, then prints the MOTION_AUTH_USERS entry and the
// authenticator setup key. Paste the entry into Vercel env vars; never commit it.
import { randomBytes, scryptSync } from "node:crypto";
import { createInterface } from "node:readline/promises";

const name = (process.argv[2] || "").trim().toLowerCase();
if (!/^[a-z0-9._-]{2,32}$/.test(name)) {
  console.error("Give a name: npm run auth:add-user -- jovanni");
  process.exit(1);
}
const rl = createInterface({ input: process.stdin, output: process.stdout });
const pw = process.env.MOTION_NEW_PASSWORD || (await rl.question("Password (12+ characters): "));
rl.close();
if (pw.length < 12) {
  console.error("Use at least 12 characters.");
  process.exit(1);
}
const salt = randomBytes(16);
const hash = scryptSync(pw, salt, 32, { N: 16384, r: 8, p: 1 });
const B32 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";
let bits = 0, value = 0, totp = "";
for (const b of randomBytes(20)) {
  value = (value << 8) | b; bits += 8;
  while (bits >= 5) { totp += B32[(value >>> (bits - 5)) & 31]; bits -= 5; }
}
const entry = { u: name, pw: `scrypt$16384$8$1$${salt.toString("base64")}$${hash.toString("base64")}`, totp };
console.log("\nMOTION_AUTH_USERS entry (put inside the [ ] list):\n" + JSON.stringify(entry));
console.log(`\nAuthenticator app → add account → enter setup key:\n  ${totp}`);
console.log(`or open: otpauth://totp/${encodeURIComponent("MOTION Ops:" + name)}?secret=${totp}&issuer=MOTION%20Ops`);
console.log("\nSession secret (once, for MOTION_SESSION_SECRET):\n  " + randomBytes(32).toString("base64url"));
