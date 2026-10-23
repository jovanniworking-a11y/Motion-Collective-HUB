// Starts the panel with a throwaway test login for the auth e2e (never used outside tests).
import { spawn } from "node:child_process";
import { randomBytes, scryptSync } from "node:crypto";

const salt = randomBytes(16);
const pw = `scrypt$16384$8$1$${salt.toString("base64")}$${scryptSync("e2e-password-123", salt, 32, { N: 16384, r: 8, p: 1 }).toString("base64")}`;
const env = {
  ...process.env,
  MOTION_SESSION_SECRET: randomBytes(32).toString("hex"),
  MOTION_AUTH_USERS: JSON.stringify([{ u: "crewtest", pw, totp: process.env.E2E_TOTP }]),
  MOTION_INSECURE_COOKIE: "1",
};
const [cmd, ...args] = process.argv.slice(2);
spawn(cmd, args, { stdio: "inherit", env }).on("exit", (c) => process.exit(c ?? 0));
