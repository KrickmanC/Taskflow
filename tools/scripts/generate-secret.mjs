import { randomBytes } from "node:crypto";

const size = Number.parseInt(process.argv[2] ?? "48", 10);
const bytes = Number.isFinite(size) && size > 0 ? size : 48;

console.log(randomBytes(bytes).toString("base64url"));
