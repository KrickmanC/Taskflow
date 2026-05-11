import { existsSync, readFileSync, writeFileSync } from "node:fs";

const [, , file, assignment] = process.argv;

if (!file || !assignment || !assignment.includes("=")) {
  console.error("Usage: node tools/scripts/set-env.mjs <env-file> KEY=VALUE");
  process.exit(1);
}

const [key, ...valueParts] = assignment.split("=");
const value = valueParts.join("=");
const line = `${key}=${JSON.stringify(value)}`;
const lines = existsSync(file) ? readFileSync(file, "utf8").split(/\r?\n/) : [];
let replaced = false;

const next = lines.map((existing) => {
  if (existing.startsWith(`${key}=`)) {
    replaced = true;
    return line;
  }
  return existing;
});

if (!replaced) {
  next.push(line);
}

writeFileSync(file, `${next.filter(Boolean).join("\n")}\n`);
console.log(`${key} updated in ${file}`);
