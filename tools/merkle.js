// Builds the WL and FCFS Merkle roots for SBN13th.setRoots.
//   npm i ethers@6 && node tools/merkle.js        (reads tools/wl.txt and tools/fcfs.txt, one wallet address per line)
// Copy wl.txt and fcfs.txt next to web/mint.html too: the mint page builds each buyer's proof from the same lists.
const fs = require("fs"), path = require("path");
const { keccak256, getAddress, concat } = require("ethers");

function tree(addrs) {
  let level = [...new Set(addrs.map(a => getAddress(a.trim())))].map(a => keccak256(a)).sort();
  const layers = [level];
  while (level.length > 1) {
    const next = [];
    for (let i = 0; i < level.length; i += 2) {
      if (i + 1 === level.length) { next.push(level[i]); continue; }
      const [a, b] = [level[i], level[i + 1]].sort();
      next.push(keccak256(concat([a, b])));
    }
    layers.push(level = next);
  }
  return layers;
}
function proof(layers, addr) {
  let idx = layers[0].indexOf(keccak256(getAddress(addr)));
  if (idx < 0) return null;
  const out = [];
  for (const level of layers.slice(0, -1)) {
    const sib = idx ^ 1;
    if (sib < level.length) out.push(level[sib]);
    idx >>= 1;
  }
  return out;
}
module.exports = { tree, proof };

if (require.main === module) {
  for (const list of ["wl", "fcfs"]) {
    const f = path.join(__dirname, list + ".txt");
    const addrs = fs.existsSync(f) ? fs.readFileSync(f, "utf8").split(/\s+/).filter(a => a.startsWith("0x")) : [];
    const layers = addrs.length ? tree(addrs) : null;
    console.log(`${list}: ${addrs.length} wallets, root ${layers ? layers.at(-1)[0] : "0x" + "0".repeat(64)}`);
  }
}
