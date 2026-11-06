#!/usr/bin/env node
/**
 * crawl_kb.cjs - enumerate folder tree + item titles of IMA knowledge bases.
 * Self-contained: calls ima.qq.com directly (creds from ~/.config/ima).
 * Usage: node crawl_kb.cjs <kb_id> <kb_name> <max_pages_per_folder> <out_file>
 *
 * Why titles only: subscribed KBs answer 220030 ("no permission ... via skill")
 * for get_media_info, so this is the deepest reachable layer.
 */
const fs = require('fs');
const os = require('os');
const path = require('path');

const BASE = 'https://ima.qq.com';
const clientId = fs.readFileSync(path.join(os.homedir(), '.config/ima/client_id'), 'utf8').trim();
const apiKey   = fs.readFileSync(path.join(os.homedir(), '.config/ima/api_key'), 'utf8').trim();
let skillVersion = '1.0.0';
try { skillVersion = JSON.parse(fs.readFileSync(path.join(__dirname, 'meta.json'), 'utf8')).version || skillVersion; } catch {}

const [kbId, kbName, rootPagesArg, subPagesArg, outFile] = process.argv.slice(2);
if (!kbId || !outFile) { console.error('args: kb_id kb_name root_maxpages sub_maxpages out_file'); process.exit(1); }
const ROOTP = parseInt(rootPagesArg || '20', 10);
const SUBP  = parseInt(subPagesArg || '2', 10);
const DELAY_MS = parseInt(process.env.IMA_CRAWL_DELAY_MS || '1300', 10);

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function api(apiPath, body) {
  for (let attempt = 1; attempt <= 5; attempt++) {
    let r;
    try {
      const res = await fetch(`${BASE}/${apiPath}`, {
        method: 'POST',
        headers: {
          'ima-openapi-clientid': clientId,
          'ima-openapi-apikey': apiKey,
          'ima-openapi-ctx': `skill_version=${skillVersion}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      });
      r = JSON.parse(await res.text());
    } catch (e) {
      if (attempt === 5) throw e;
      await sleep(3000 * attempt);
      continue;
    }
    // 200001 = rate limited -> back off and retry
    if (r.code === 200001) { await sleep(5000 * attempt); continue; }
    return r;
  }
  return { code: 200001, msg: 'rate limited after retries' };
}

const items = [], folders = [];
let apiCalls = 0, failed = 0;

async function listFolder(folderId, depth, label) {
  const maxp = folderId ? SUBP : ROOTP;
  let cursor = '';
  for (let page = 0; page < maxp; page++) {
    const body = { knowledge_base_id: kbId, cursor, limit: 50 };
    if (folderId) body.folder_id = folderId;
    let r;
    try { r = await api('openapi/wiki/v1/get_knowledge_list', body); apiCalls++; await sleep(DELAY_MS); }
    catch (e) { failed++; console.error('  EXC', String(e).slice(0, 100)); break; }
    if (r.code !== 0) {
      failed++;
      console.error(`  FAIL folder=${folderId || 'ROOT'} page=${page} code=${r.code} msg=${r.msg}`);
      break;
    }
    const list = (r.data && r.data.knowledge_list) || [];
    for (const x of list) {
      const rec = { title: x.title, mt: x.media_type, mid: x.media_id,
                    parent: String(x.parent_folder_id || folderId || 'ROOT'),
                    depth, path: label };
      if (x.media_type === 99) {
        rec.folder_id = String(x.media_id);   // NOTE: keep the "folder_" prefix -
        folders.push(rec);                    // stripping it yields code 222000
      }
      items.push(rec);
    }
    if (r.data.is_end || !r.data.next_cursor) break;
    cursor = r.data.next_cursor;
  }
}

(async () => {
  await listFolder(null, 0, 'ROOT');
  let qi = 0;
  while (qi < folders.length && apiCalls < 5000) {
    const f = folders[qi++];
    await listFolder(f.folder_id, f.depth + 1,
                     (f.path === 'ROOT' ? '' : f.path + ' / ') + f.title);
  }
  const out = { kb_id: kbId, kb_name: kbName, crawled_at: new Date().toISOString(),
                api_calls: apiCalls, failed_calls: failed,
                root_pages: ROOTP, sub_pages: SUBP,
                item_count: items.length,
                folder_count: items.filter(i => i.mt === 99).length,
                items };
  fs.writeFileSync(outFile, JSON.stringify(out, null, 1), 'utf8');
  console.error(`[${kbName}] items=${out.item_count} folders=${out.folder_count} calls=${apiCalls} failed=${failed}`);
})();
