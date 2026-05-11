import { rmSync } from "node:fs";

const paths = process.argv.slice(2);
const targets = paths.length ? paths : [".turbo", ".next", ".react-router", "node_modules", "dist", "build"];

for (const target of targets) {
  rmSync(target, { force: true, recursive: true });
  console.log(`removed: ${target}`);
}
