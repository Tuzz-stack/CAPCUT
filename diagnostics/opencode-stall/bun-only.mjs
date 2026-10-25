import { spawn } from 'node:child_process';
import { readFileSync, appendFileSync } from 'node:fs';
const catalogText = readFileSync('/diag/catalog-only.json', 'utf8');
let completed = 0, pending = [], finished = false, failed = null, started = false;
const runtime = { bun: Bun.version, arch: process.arch, pid: process.pid };
function run() {
  return new Promise((resolve, reject) => {
    const proc = spawn('git', ['status', '--short'], { cwd: '/workspace', detached: true, stdio: ['ignore', 'pipe', 'pipe'] });
    pending.push(proc.pid);
    proc.stdout.resume(); proc.stderr.resume();
    proc.on('error', reject);
    proc.on('close', (code, signal) => {
      pending = pending.filter(p => p !== proc.pid);
      if (code !== 0) reject(new Error(`git closed code=${code} signal=${signal}`));
      else { completed++; resolve(); }
    });
  });
}
async function exercise() {
  try {
    await Promise.all(Array.from({length:4}, async () => {
      for (let i=0; i<150; i++) await run();
    }));
    finished = true;
  } catch (e) { failed = String(e); }
}
setInterval(() => appendFileSync('/out/bun-heartbeat.jsonl', JSON.stringify({at:Date.now(),completed,pending,finished,failed})+'\n'), 1000);
Bun.serve({ hostname:'127.0.0.1', port:4096, fetch(request) {
  const path = new URL(request.url).pathname;
  if (path === '/global/health') return Response.json({healthy:true,version:Bun.version});
  if (path === '/progress') return Response.json({runtime,completed,pending,finished,failed});
  if (path === '/start') { if (!started) { started=true; void exercise(); } return Response.json({started}); }
  if (path === '/config/providers') return Response.json(JSON.parse(catalogText));
  return Response.json([]);
}});
console.log(JSON.stringify(runtime));
