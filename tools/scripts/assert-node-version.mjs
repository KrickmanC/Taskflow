const required = [22, 18, 0];
const current = process.versions.node.split(".").map((part) => Number.parseInt(part, 10));

let ok = true;
for (let index = 0; index < required.length; index += 1) {
  if (current[index] > required[index]) {
    break;
  }
  if (current[index] < required[index]) {
    ok = false;
    break;
  }
}

if (!ok) {
  console.error(`Node.js ${required.join(".")} or newer is required. Current version: ${process.versions.node}`);
  process.exit(1);
}

console.log(`Node.js ${process.versions.node} satisfies >=${required.join(".")}`);
