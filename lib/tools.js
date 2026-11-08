/**
 * dsh-research-suite v2 · tools
 *
 * 7 个只读工具。全部零宿主依赖：parameters 直接给编译好的 JSON Schema，
 * output.render 返回 ContentBlock[]，execute 返回 canonical 字符串。
 */

import fs from 'node:fs';
import os from 'node:os';
import { createVerify } from './verify.js';

const textOutput = () => ({
  schema: { type: 'string' },
  render: (_args, value) => [{ type: 'text', text: String(value ?? '') }],
});

function str(description) {
  return { type: 'string', description };
}

function int(description, min, max) {
  return { type: 'integer', description, minimum: min, maximum: max };
}

function makeTool(core, { name, description, parameters, run }) {
  return {
    name,
    description,
    parameters,
    output: textOutput(),
    async execute(args) {
      try {
        return await run(args ?? {});
      } catch (err) {
        return `[research-suite] ${name} 执行失败：${err && err.message ? err.message : String(err)}`;
      }
    },
  };
}

function bulletMembers(cap) {
  const lines = [];
  for (const m of cap.members ?? []) {
    lines.push(`  · ${m.skill}〔${m.verdict}〕`);
    if (m.best_at?.length) lines.push(`      擅长：${m.best_at.join('；')}`);
    if (m.limits?.length) lines.push(`      短板：${m.limits.join('；')}`);
    if (m.take?.length) lines.push(`      取用：${m.take.join('；')}`);
  }
  return lines;
}

function formatPlaybook(cap, hits) {
  const out = [];
  out.push(`■ ${cap.id} · ${cap.label}（域 ${cap.domain}／${cap.domainLabel}）`);
  if (hits?.length) out.push(`触发命中：${hits.join('、')}`);
  out.push(`接什么：${(cap.inputs ?? []).join('、') || '见协议'}`);
  out.push(`交什么：${cap.summary}`);
  out.push('');
  out.push('【融合协议·照此执行】');
  (cap.protocol ?? []).forEach((step, i) => {
    out.push(`${i + 1}. ${step.step}`);
    out.push(`   来源：${step.from}`);
    out.push(`   做法：${step.do}`);
    out.push(`   细则：${step.detail}`);
  });
  if (cap.decide?.length) {
    out.push('');
    out.push('【分歧点·怎么选】');
    for (const d of cap.decide) out.push(`- 当${d.when} → 用 ${d.use}，而不是 ${d.instead_of}。因为：${d.why}`);
  }
  if (cap.gates?.length) {
    out.push('');
    out.push('【判据与红线·交付前逐条核】');
    for (const g of cap.gates) out.push(`- ${g}`);
  }
  if (cap.outputs?.length) {
    out.push('');
    out.push(`交付物：${cap.outputs.join('；')}`);
  }
  if (cap.kb?.length) {
    out.push(`需要原文细节时：${cap.kb.map((k) => `research_kb_read name=${k}`).join(' 或 ')}（最多读 2 个）`);
  }
  out.push('');
  out.push('【成员账本·谁被取用了什么】');
  out.push(...bulletMembers(cap));
  return out.join('\n');
}

function formatGateSection(core, section) {
  const gates = core.gates;
  if (!gates) return '[research-suite] data/gates.json 不存在或不可解析。';
  const titles = {
    data: '数据六道闸门（统计数字落地前必过）',
    selfcheck: '交付自检',
    mutex: '技能互斥对（同一任务不要同时启用）',
    forbidden: '禁止事项',
    hard: '硬规则',
    handoffs: '交接物（角色/阶段之间传什么文件）',
  };
  const keys = {
    data: ['dataGates'],
    selfcheck: ['selfCheck'],
    mutex: ['mutex'],
    forbidden: ['forbidden'],
    hard: ['hardRules', 'hard'],
    handoffs: ['handoffs'],
  };
  const wanted = section && section !== 'all' ? [section] : Object.keys(titles);
  const out = [];
  for (const key of wanted) {
    const candidates = keys[key] ?? [key];
    let items = null;
    for (const k of candidates) {
      if (Array.isArray(gates[k])) {
        items = gates[k];
        break;
      }
    }
    out.push(`## ${titles[key] ?? key}`);
    if (!items) {
      out.push('（无）');
      out.push('');
      continue;
    }
    for (const item of items) {
      if (typeof item === 'string') {
        out.push(`- ${item}`);
        continue;
      }
      const label = item.name ?? item.id ?? item.rule ?? item.ask ?? item.a ?? '';
      const rest = Object.entries(item)
        .filter(([k]) => !['name', 'id', 'rule', 'ask', 'a'].includes(k))
        .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join('/') : String(v)}`)
        .join('｜');
      out.push(`- ${label}${rest ? `：${rest}` : ''}`);
    }
    out.push('');
  }
  return out.join('\n').trim();
}

export function createTools(core) {
  const verify = createVerify(core);
  return [
    makeTool(core, {
      name: 'research_playbook',
      description:
        '科研任务的第一步：把用户原话传进来，返回最匹配的能力卡（1～3 张）及其融合协议、判据、交付物与成员账本。识别到科研诉求（写作/润色/绘图/统计/文献/选题/审稿/幻灯）时必须先调用它，再动手。',
      parameters: {
        type: 'object',
        properties: {
          task: str('用户的原话或诉求摘要，尽量原样传入，不要自己改写成术语'),
          domain: str('可选：限定域，取值 writing/polish/figures/stats/literature/format/ideation/review/slides'),
          limit: int('可选：返回几张能力卡，默认 3', 1, 5),
        },
        required: ['task'],
        additionalProperties: false,
      },
      async run(args) {
        const domain = args.domain ? String(args.domain).trim() : undefined;
        const limit = Number.isInteger(args.limit) ? args.limit : 3;
        const res = core.matchCapabilities(String(args.task ?? ''), { limit, domain });
        if (res.negative && res.negative.length) {
          return [
            '【未接管】这句话不像科研任务：' + res.negative.join('；'),
            '',
            '若确实要做科研任务，请补一句科研语境（对象是什么、要交什么），我再接管；否则我不给协议，免得把非科研的活按科研流程做。',
          ].join('\n');
        }
        if (!res.takeover) {
          const lines = ['【未接管】' + res.reason];
          if (res.candidates.length) {
            lines.push('', '最接近的候选（仅供参考，我并没有按它执行）：');
            for (const c of res.candidates) {
              const keysStr = c.hitTriggers.join('、') || '—';
              lines.push('- ' + c.cap.id + '（' + c.cap.label + '）得分 ' + c.score + '｜命中：' + keysStr);
            }
          }
          for (const a of res.ambiguous) lines.push('', '需要你先定一件事：' + a.why + '；请说明 ' + a.ask);
          lines.push('', '请把诉求说得更具体（做什么、对象是什么、要交什么），或指定 domain 再调一次。现有域：' + core.domains.map((d) => d.domain + '(' + d.count + ')').join('、'));
          return lines.join('\n');
        }
        const blocks = res.matches.map((m) => formatPlaybook(m.cap, m.hitTriggers));
        const head =
          '【科研任务接管】置信度 ' + res.confidence + '｜得分 ' + res.score + '（领先第二名 ' + res.gap + '）｜命中：' + (res.hits.join('、') || '—');
        const tail =
          '\n\n执行要求：按【融合协议】逐步执行，不要压缩成一句结论；交付前对照【判据与红线】逐条核，并用 research_gate 复核。';
        const notes = [];
        for (const a of res.ambiguous) notes.push('\n\n注意：' + a.why + ' —— ' + a.ask);
        if (res.candidates.length > 1) {
          const alt = res.candidates[1];
          notes.push('\n\n次优候选：' + alt.cap.id + '（得分 ' + alt.score + '）。若你觉得上面那张卡对不上，告诉我换这张。');
        }
        return [head, '', ...blocks.map((b, i) => (i ? '\n──────────\n\n' + b : b))].join('\n') + notes.join('') + tail;
      },
    }),

    makeTool(core, {
      name: 'research_capability',
      description:
        '展开能力卡：给 id 返回该卡的完整内容（成员对比、协议、分歧点、判据、交付物）；给 domain 返回该域全部能力清单；都不给返回全域总览。',
      parameters: {
        type: 'object',
        properties: {
          id: str('能力 id，例如 stats.psm、polish.deai'),
          domain: str('域 id，例如 stats'),
        },
        required: [],
        additionalProperties: false,
      },
      async run(args) {
        const id = args.id ? String(args.id).trim() : '';
        const domain = args.domain ? String(args.domain).trim() : '';
        if (id) {
          const cap = core.capById.get(id);
          if (!cap) {
            const near = core.caps.filter((c) => c.id.includes(id.split('.').pop() ?? '')).slice(0, 6).map((c) => c.id);
            return `[research-suite] 没有能力卡 ${id}${near.length ? `；相近：${near.join('、')}` : ''}。可先调 research_capability domain=<域> 看清单。`;
          }
          return formatPlaybook(cap, []);
        }
        if (domain) {
          const list = core.capabilityList(domain);
          if (!list.length) return `[research-suite] 域 ${domain} 无能力卡。现有域：${core.domainDigest().join('、')}`;
          return [
            `域 ${domain} 共 ${list.length} 张能力卡：`,
            ...list.map((c) => `- ${c.id} · ${c.label}\n  触发：${c.triggers.slice(0, 6).join('、')}\n  成员：${c.members.join('、')}`),
          ].join('\n');
        }
        return [
          `dsh-research-suite v${core.stats.version}：${core.stats.domains} 个能力域 / ${core.stats.capabilities} 张能力卡 / ${core.stats.skills} 个源技能索引`,
          '',
          ...core.domains.map((d) => `- ${d.domain}（${d.label}）：${d.count} 张能力卡｜${d.summary}`),
          '',
          '另有 toolbox 索引桶：与科研写作不直接相关、但可能需要调用的工具类技能（科学计算库、ML 工程、格式转换等），只能通过 research_catalog domain=toolbox 检索。',
          '用 research_capability domain=<域> 看清单，或 id=<能力> 展开。',
        ].join('\n');
      },
    }),

    makeTool(core, {
      name: 'research_catalog',
      description:
        '在插件自带的原始科研技能目录（数百个技能全文）里检索：按名称与描述关键词匹配，返回 name/域/字节数/描述/路径。用于找"还有没有别的技能可用"，不必联网。',
      parameters: {
        type: 'object',
        properties: {
          query: str('关键词或自然语言短语，例如「倾向评分匹配」「nature 风格配色」'),
          domain: str('可选：限定域'),
          limit: int('可选：返回条数，默认 10', 1, 40),
        },
        required: ['query'],
        additionalProperties: false,
      },
      async run(args) {
        const hits = core.searchSkills(String(args.query ?? ''), {
          domain: args.domain ? String(args.domain) : undefined,
          limit: Number.isInteger(args.limit) ? args.limit : 10,
        });
        if (!hits.length) {
          return `[research-suite] 未检索到技能：${args.query}。可换同义词再试，或去掉 domain 限制。`;
        }
        return [
          `检索「${args.query}」命中 ${hits.length} 个技能（按相关度）：`,
          ...hits.map(
            (h) =>
              `- ${h.name}〔${h.domain}｜${Math.round(h.bytes / 1024)}KB${h.assets ? `｜附带 ${h.assets} 个 references/scripts 资产` : ''}〕\n  ${h.description}\n  路径：${h.path}`,
          ),
          '',
          '读全文：research_kb_read name=<技能名>；读它的脚本/模板：research_kb_read name=<技能名> asset=<相对路径>',
        ].join('\n');
      },
    }),

    makeTool(core, {
      name: 'research_kb_read',
      description:
        '读插件自带的技能原文、索引文件或技能自带资产（knowledge/ 下：skills/<域>/<slug>.md、INDEX.md、FUSION.md、以及技能的 references/scripts/templates）。支持分段读取；越界路径会被拒绝。不给 asset 时会告诉你该技能附带哪些脚本/模板。',
      parameters: {
        type: 'object',
        properties: {
          name: str('技能名，例如 paper-deweight'),
          file: str('可选：knowledge/ 下的相对路径，例如 INDEX.md；给了 file 就忽略 name'),
          asset: str('可选：技能自带资产里的相对路径，例如 scripts/plot.py；与 name 一起用'),
          offset: int('可选：起始字符偏移，默认 0', 0, 1000000),
          limit: int('可选：本次返回字符上限，默认 24000', 1000, 120000),
        },
        required: [],
        additionalProperties: false,
      },
      async run(args) {
        const file = args.file ? String(args.file).replace(/^[\\/]+/, '') : '';
        if (file) {
          const rel = file.startsWith('knowledge/') ? file : `knowledge/${file}`;
          const res = core.read(rel, { offset: args.offset, limit: args.limit });
          return [
            `文件：${res.path}（${res.bytes} 字节，${res.chars} 字符）`,
            `本次返回 ${res.returned} 字符${res.truncated ? `，未读完；继续读请传 offset=${res.nextOffset}` : '（已读完）'}`,
            '',
            res.text,
          ].join('\n');
        }
        const name = args.name ? String(args.name).trim() : '';
        if (!name) return '[research-suite] 需要 name（技能名）或 file（knowledge/ 下相对路径）之一。';
        const asset = args.asset ? String(args.asset).replace(/^[\\/]+/, '') : '';
        if (asset) {
          const res = core.readAsset(name, asset);
          return [
            `技能：${name}　资产：${res.path}（${res.bytes} 字节）`,
            `本次返回 ${res.returned} 字符${res.truncated ? `，未读完；继续读请传 offset=${res.nextOffset}` : '（已读完）'}`,
            '',
            res.text,
          ].join('\n');
        }
        const res = core.readSkill(name, { offset: args.offset, limit: args.limit });
        const head = [
          `技能：${res.skill}　文件：${res.path}（${res.bytes} 字节）`,
          `本次返回 ${res.returned} 字符${res.truncated ? `，未读完；继续读请传 offset=${res.nextOffset}` : '（已读完）'}`,
        ];
        const listing = core.listAssets(name);
        if (listing.included) {
          const shown = listing.files.slice(0, 12).map((f) => f.path);
          head.push(
            `该技能附带 ${listing.count} 个可读资产（脚本/模板/参考文档）：${shown.join('、')}${listing.count > shown.length ? ' …' : ''}`,
            `读其中某个：research_kb_read name=${name} asset=<上面任一路径>`,
          );
        } else if (listing.reason) {
          head.push(`（${listing.reason}）`);
        }
        return [...head, '', res.text].join('\n');
      },
    }),

    makeTool(core, {
      name: 'research_standard',
      description:
        '读插件内置的科研规范（references/ 下：期刊格式、参考文献 GB/T 7714、统计报告、图件规范、幻灯规范等）。不给参数则列出清单。',
      parameters: {
        type: 'object',
        properties: {
          name: str('规范文件名关键词或序号，例如「参考文献」「03」'),
          offset: int('可选：起始字符偏移', 0, 1000000),
          limit: int('可选：本次返回字符上限', 1000, 120000),
        },
        required: [],
        additionalProperties: false,
      },
      async run(args) {
        const list = core.standards;
        if (!list.length) return '[research-suite] references/ 为空。';
        const key = args.name ? String(args.name).trim() : '';
        if (!key) {
          return ['内置规范清单（用 research_standard name=<关键词> 读全文）：', ...list.map((s) => `- ${s.file}　${s.title}`)].join('\n');
        }
        const hit = list.find((s) => s.file.includes(key) || s.title.includes(key));
        if (!hit) return `[research-suite] 未找到规范「${key}」。现有：${list.map((s) => s.file).join('、')}`;
        const res = core.read(`references/${hit.file}`, { offset: args.offset, limit: args.limit });
        return [`规范：${hit.title}（${res.bytes} 字节）`, `本次返回 ${res.returned} 字符${res.truncated ? `，继续读请传 offset=${res.nextOffset}` : '（已读完）'}`, '', res.text].join('\n');
      },
    }),

    makeTool(core, {
      name: 'research_gate',
      description:
        '门禁与机械自检。section 取 data（统计六道闸门）/selfcheck（交付自检）/mutex/forbidden/hard/handoffs/all；另可传 text 对一段交付文本做机械检查（中文语境半角标点、引用编号上标待确认、AI 套话、绝对化措辞、文言虚词、数值单位空格），返回计数与逐条位置。',
      parameters: {
        type: 'object',
        properties: {
          section: {
            type: 'string',
            description: '可选：all/data/selfcheck/mutex/forbidden/hard/handoffs，默认 all',
            enum: ['all', 'data', 'selfcheck', 'mutex', 'forbidden', 'hard', 'handoffs'],
          },
          text: str('可选：要机械检查的交付文本（可只贴要检查的章节）'),
        },
        required: [],
        additionalProperties: false,
      },
      async run(args) {
        const section = args.section ? String(args.section) : 'all';
        const parts = [];
        if (args.text) {
          const text = String(args.text);
          if (text.length > 200000) return '[research-suite] text 过长（上限 20 万字符），请分块检查。';
          const report = core.checkText(text);
          const sm = report.summary ?? { error: 0, warn: 0, info: 0 };
          const lines = [
            '## 机械自检（' + text.length + ' 字符：必改 ' + sm.error + ' 处｜建议改 ' + sm.warn + ' 处｜仅提示 ' + sm.info + ' 处）',
          ];
          if (!sm.error && !sm.warn) lines.push('没有命中必改项。');
          const order = { error: 0, warn: 1, info: 2 };
          const label = { error: '必改', warn: '建议改', info: '仅提示' };
          const sorted = [...report.findings].sort((a, b) => (order[a.level] ?? 9) - (order[b.level] ?? 9));
          for (const f of sorted.slice(0, 60)) {
            lines.push('- [' + (label[f.level] ?? '提示') + '] ' + f.rule + (f.line ? ' 第 ' + f.line + ' 行' : '') + '：' + f.snippet + ' → ' + f.hint);
          }
          if (sorted.length > 60) lines.push('……另有 ' + (sorted.length - 60) + ' 处。');
          lines.push('');
          lines.push('口径：术语已在白名单内（完全缓解、首次给药、覆盖率/涵盖/遮盖等不再误报）；「绝对化措辞」只在高置信语境报警，info 级不要当错误去改本来正确的句子；标点与引用上标仍需按 references 规范人工核。');
          parts.push(lines.join('\n'));
        }        if (!args.text || section !== 'all') parts.push(formatGateSection(core, section));
        return parts.join('\n\n──────────\n\n');
      },
    }),

    makeTool(core, {
      name: 'research_suite_status',
      description: '装载自检：套件版本、域与能力卡数量、原始技能索引完整性、内置规范清单、包根路径。用于确认插件是否正常工作。',
      parameters: { type: 'object', properties: {}, required: [], additionalProperties: false },
      async run() {
        const s = core.stats;
        const byDomain = Object.entries(s.byDomain)
          .sort((a, b) => b[1] - a[1])
          .map(([d, n]) => `${d}:${n}`)
          .join('｜');
        const missing = core.domains.filter((d) => !core.domainSkillPath(d.skill)).map((d) => d.skill);
        return [
          '## dsh-research-suite v2 装载自检',
          '',
          `包根：${core.pluginRoot}`,
          `原始技能索引：${s.skills} 条（科研相关 ${s.researchSkills}）｜${byDomain}`,
          `能力域：${s.domains} 个｜能力卡：${s.capabilities} 张`,
          ...core.domains.map((d) => `  - ${d.domain}（${d.label}）${d.count} 张 → skills/${d.skill}.md`),
          `内置规范：${s.standards} 份${core.standards.length ? `（${core.standards.map((x) => x.file).join('、')}）` : ''}`,
          `门禁数据：${core.gates ? `有（version ${core.gates.version ?? '未知'}）` : '缺失'}`,
          missing.length ? `⚠ 缺少域技能文件：${missing.join('、')}` : '✓ 9 个域技能文件齐备',
        ].join('\n');
      },
    }),
    makeTool(core, {
      name: 'research_run',
      description:
        '真正执行一段 R 或 Python 代码并把 stdout/stderr 与产物文件清单回传。R 用本机 Rscript、Python 用本机 3.12；自动清理 locale 变量；拒绝 install/rm/curl 这类破坏性或联网命令。用于「算出来」而不是「说怎么做」。',
      parameters: {
        type: 'object',
        properties: {
          kind: { type: 'string', enum: ['r', 'python'], description: '执行器：r 或 python' },
          code: str('要执行的脚本正文（完整可运行代码，不要只给片段）'),
          workdir: str('可选：工作目录（必须在当前工作区或系统临时目录内）'),
          timeoutMs: int('可选：超时毫秒，默认 600000（10 分钟）', 1000, 1800000),
        },
        required: ['kind', 'code'],
        additionalProperties: false,
      },
      async run(args) {
        const workdir = args.workdir ? String(args.workdir) : os.tmpdir();
        const r = await verify.runScript({ kind: args.kind, code: String(args.code ?? ''), workdir, timeoutMs: args.timeoutMs });
        if (!r.ok) {
          const lines = ['执行未成功：' + (r.error || ('exit ' + r.exitCode))];
          if (r.hint) lines.push('提示：' + r.hint);
          if (r.command) lines.push('可直接粘贴执行的命令：' + r.command);
          if (r.stderr) lines.push('', 'stderr：', String(r.stderr).slice(0, 4000));
          if (r.script) lines.push('', '脚本已落盘：' + r.script);
          return lines.join('\n');
        }
        const lines = ['执行完成（exit 0，耗时 ' + r.durationMs + ' ms）'];
        if (r.script) lines.push('脚本：' + r.script);
        if (r.stdout) lines.push('', 'stdout：', String(r.stdout).slice(0, 6000));
        if (r.stderr) lines.push('', 'stderr（非空不代表失败，警告常在这里）：', String(r.stderr).slice(0, 3000));
        if (Array.isArray(r.files) && r.files.length) {
          lines.push('', '产物文件（' + r.files.length + ' 个）：');
          for (const f of r.files.slice(0, 30)) lines.push('- ' + (f.path || f));
        } else {
          lines.push('', '没有产生新文件：纯计算请把结果打印到 stdout。');
        }
        return lines.join('\n');
      },
    }),

    makeTool(core, {
      name: 'research_data_check',
      description:
        '对数据文件做机械校验（CSV/TSV）：列名重复、行宽不一致、缺失率、常量列、ID 重复、不可能值（年龄/负计数/百分比越界）、完全重复行、EPV 事件数比。这是统计六道闸门里能机械化的部分，出任何统计量之前先跑它。',
      parameters: {
        type: 'object',
        properties: {
          file: str('数据文件路径（.csv / .tsv）'),
          outcome: str('可选：结局变量列名（给了就计算事件数与 EPV）'),
          predictors: { type: 'array', items: { type: 'string' }, description: '可选：自变量列名列表（配合 outcome 算 EPV）' },
        },
        required: ['file'],
        additionalProperties: false,
      },
      async run(args) {
        const r = await verify.checkData({ file: String(args.file ?? ''), outcome: args.outcome, predictors: args.predictors });
        const lines = ['## 数据校验：' + (r.file || '(未给)'), ''];
        lines.push('行数 ' + r.rows + '｜列数 ' + r.cols + '｜分隔符 ' + (r.delimiter === '\t' ? 'TAB' : String(r.delimiter)));
        if (r.epv && r.epv.epv !== null && r.epv.epv !== undefined) lines.push('EPV = ' + r.epv.epv + '（' + r.epv.events + ' 事件 / ' + (r.epv.predictors ?? 0) + ' 自变量），≥10 才可建模');
        const errs = (r.findings || []).filter((f) => f.level === 'error');
        const warns = (r.findings || []).filter((f) => f.level !== 'error');
        lines.push('', '必改 ' + errs.length + ' 项｜提示 ' + warns.length + ' 项');
        for (const f of errs) lines.push('- [必改] ' + f.rule + '：' + f.detail);
        for (const f of warns) lines.push('- [提示] ' + f.rule + '：' + f.detail);
        if (!(r.findings || []).length) lines.push('结构层面没有可机械判定的问题。变量类型与业务含义仍需人工核。');
        return lines.join('\n');
      },
    }),

    makeTool(core, {
      name: 'research_output_check',
      description:
        '核验交付文件是否真能用：PNG 的 DPI（投稿 300+）、PDF 是否有文本层、DOCX 的 document.xml 与表格数、XLSX 的 workbook/sheet、CSV 行数、MD 字数。用来避免「说生成了其实坏了」。',
      parameters: {
        type: 'object',
        properties: {
          files: { type: 'array', items: { type: 'string' }, description: '文件路径列表（支持 png/pdf/docx/xlsx/csv/tsv/md）' },
        },
        required: ['files'],
        additionalProperties: false,
      },
      async run(args) {
        const r = await verify.checkOutputs({ files: Array.isArray(args.files) ? args.files : [] });
        const lines = ['## 交付物核验'];
        if (r.summary) lines.push('文件 ' + r.summary.files + ' 个｜可用 ' + r.summary.ok + ' 个｜含必改 ' + r.summary.error + ' 个｜含提示 ' + r.summary.warn + ' 个');
        for (const item of r.results || []) {
          const errs = (item.findings || []).filter((f) => f.level === 'error');
          const head = '\n### ' + (item.file || '(空路径)') + ' — ' + item.kind + (errs.length ? '（有问题）' : '（结构可用）');
          lines.push(head);
          const facts = Object.entries(item.facts || {}).map(([k, v]) => k + '=' + v).join('｜');
          if (facts) lines.push('  实测：' + facts);
          for (const f of item.findings || []) lines.push('  - [' + (f.level === 'error' ? '必改' : '提示') + '] ' + f.rule + '：' + f.detail);
        }
        return lines.join('\n');
      },
    }),

    makeTool(core, {
      name: 'research_doi_check',
      description:
        '联网核对 DOI 是否真实存在（Crossref）：返回每条的解析结果与题名/期刊/年份。这是防编造参考文献的硬核验，凡是参考文献都要过一遍。无网络时明确报 network 失败，不假装成功。',
      parameters: {
        type: 'object',
        properties: {
          dois: { type: 'array', items: { type: 'string' }, description: 'DOI 列表（可不带 https://doi.org/ 前缀）' },
        },
        required: ['dois'],
        additionalProperties: false,
      },
      async run(args) {
        const rows = await verify.checkDois({ dois: Array.isArray(args.dois) ? args.dois : [] });
        const list = Array.isArray(rows) ? rows : (rows && rows.results) || [];
        const okCount = list.filter((x) => x.ok).length;
        const lines = ['## DOI 核验（Crossref）'];
        lines.push('共 ' + list.length + ' 条｜解析成功 ' + okCount + ' 条｜未解析 ' + (list.length - okCount) + ' 条');
        for (const item of list) {
          if (item.ok) {
            const meta = [item.title, item.container, item.year].filter(Boolean).join('｜');
            lines.push('- 已存在 ' + item.doi + '｜' + meta);
          } else {
            const why = item.error || ('http_' + item.status);
            lines.push('- 未解析 ' + item.doi + '：' + why);
          }
        }
        lines.push('', '判定规则：Crossref 查不到的 DOI 不得进入交付；网络失败（error=network）不算文献不存在，但必须标注「未核验」。');
        return lines.join('\n');
      },
    }),

    makeTool(core, {
      name: 'research_ref_audit',
      description:
        '核对正文引用与文献表是否自洽：编号跳号/重复、正文最大编号与文献表条数是否一致、条目缺 DOI、年份晚于今年、同一文献重复列出、正文引用超出条目。防的是「引用了不存在的文献」。',
      parameters: {
        type: 'object',
        properties: {
          text: str('含正文与文献表的整段文本（可只贴参考文献部分）'),
          file: str('可选：从 .md/.txt 文件读入（与 text 二选一，file 优先）'),
        },
        required: [],
        additionalProperties: false,
      },
      async run(args) {
        let text = String(args.text ?? '');
        if (args.file) {
          try {
            text = fs.readFileSync(String(args.file), 'utf8');
          } catch (e) {
            return '[research-suite] 读文件失败：' + String(e && e.message ? e.message : e);
          }
        }
        const r = await verify.auditRefs({ text });
        const lines = ['## 引用自洽核验'];
        lines.push('正文引用次数 ' + (r.cites ? r.cites.length : 0) + '｜不同编号 ' + r.uniqueCites + ' 个｜文中 DOI ' + (r.dois ? r.dois.length : 0) + ' 个');
        const errs = (r.findings || []).filter((f) => f.level === 'error');
        const warns = (r.findings || []).filter((f) => f.level !== 'error');
        for (const f of errs) lines.push('- [必改] ' + f.rule + '：' + f.detail);
        for (const f of warns) lines.push('- [提示] ' + f.rule + '：' + f.detail);
        if (!(r.findings || []).length) lines.push('编号与条数层面自洽。条目本身的真实性仍需 research_doi_check 逐条核。');
        return lines.join('\n');
      },
    }),
  ];
}
