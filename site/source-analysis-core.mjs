/**
 * Star Cyber Audit — deterministic, browser-first static source analysis.
 * No network requests, no eval, no upload. Heuristics, not proven vulnerabilities.
 * The same module is tested in Node.js without a browser or target server.
 */
export const ENGINE_VERSION = "2.1.0";
export const MAX_FILES = 32;
export const MAX_FILE_BYTES = 2 * 1024 * 1024;
export const MAX_TOTAL_BYTES = 16 * 1024 * 1024;
export const ACCEPTED = /\.(?:js|mjs|cjs|jsx|ts|tsx|py|html)$/i;

const RULES = [
  {id:"SC-EVAL",level:"high",title:"تنفيذ شيفرة ديناميكية",pattern:/\beval\s*\(|\bnew\s+Function\s*\(/,fix:"راجع مصدر الإدخال واستبدل التنفيذ الديناميكي بواجهة آمنة.",ext:/\.(?:js|mjs|cjs|jsx|ts|tsx)$/i},
  {id:"SC-HTML",level:"medium",title:"نقطة حقن محتوى HTML محتملة",pattern:/\.\s*(?:innerHTML|outerHTML)\s*=/,fix:"افحص مصدر البيانات واستخدم textContent أو ترميزًا سياقيًا مناسبًا.",ext:/\.(?:js|mjs|cjs|jsx|ts|tsx)$/i},
  {id:"SC-STORAGE",level:"medium",title:"تخزين رمز حساس في المتصفح",pattern:/\b(?:localStorage|sessionStorage)\.setItem\s*\(\s*['"](?:token|jwt|access_token|refresh_token|auth|session)['"]/,fix:"راجع دورة حياة الرمز ومخاطر XSS وبدائل الحفظ.",ext:/\.(?:js|mjs|cjs|jsx|ts|tsx)$/i},
  {id:"SC-DOM",level:"medium",title:"استخدام document.write",pattern:/\bdocument\.write\s*\(/,fix:"استبدل الكتابة إلى DOM بواجهات محددة وآمنة.",ext:/\.(?:js|mjs|cjs|jsx|ts|tsx|html)$/i},
  {id:"SC-TLS",level:"high",title:"تعطيل التحقق من TLS محتمل",pattern:/\bverify\s*=\s*False\b|\brejectUnauthorized\s*:\s*false\b/,fix:"أبقِ التحقق من شهادات TLS فعالًا في بيئة الإنتاج."},
  {id:"SC-SHELL",level:"medium",title:"تشغيل shell من Python",pattern:/\bshell\s*=\s*True\b/,fix:"استخدم مصفوفة معاملات بدلاً من تمرير أوامر نصية غير موثوقة إلى shell.",ext:/\.py$/i},
  {id:"SC-QR",level:"medium",title:"اعتماد QR على قيمة بديلة في الواجهة",pattern:/\bqr_code\s*\|\|/,fix:"تحقق من توقيع QR في الخادم؛ البدائل في الواجهة ليست دليل مصادقة.",ext:/\.(?:js|mjs|cjs|jsx|ts|tsx)$/i},
  {id:"SC-POSTMSG",level:"medium",title:"postMessage إلى أصل عام",pattern:/\.postMessage\s*\([^,\n]+,\s*['"]\*['"]/,fix:"قيّد targetOrigin وتحقق من origin في مستقبل الرسالة.",ext:/\.(?:js|mjs|cjs|jsx|ts|tsx)$/i},
];
const SECRET_RULES = [
  ["OPENAI_API_KEY",/\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{22,}\b/],
  ["GITHUB_TOKEN",/\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b/],
  ["AWS_ACCESS_KEY_ID",/\b(?:AKIA|ASIA)[A-Z0-9]{16}\b/],
  ["GOOGLE_API_KEY",/\bAIza[0-9A-Za-z_-]{35}\b/],
  ["PRIVATE_KEY_HEADER",/-----BEGIN (?:(?:RSA|EC|OPENSSH|ENCRYPTED) )?PRIVATE KEY-----/]
];
const ENDPOINT = /(?:\/api\/[A-Za-z0-9_./{}:-]{2,160}|(?:local_form|support_org|BorderPort_HS|carrier_register)\/[A-Za-z0-9_./{}:-]{2,160})/g;
const IMPORT = /\b(?:from\s*|import\s*\(|require\s*\()\s*['"]([^'" ]{1,180})['"]/g;
const STORAGE = /\b(?:localStorage|sessionStorage)\s*\.\s*(?:getItem|setItem|removeItem)\s*\(\s*['"]([A-Za-z0-9_-]{1,80})['"]/g;
const SEV = {high:20, medium:8, low:3};

function extract(pattern, text, max=100) {
  const matches = [];
  const seen = new Set();
  pattern.lastIndex = 0;
  let m;
  while ((m = pattern.exec(text)) !== null && matches.length < max) {
    const v = String(m[1] || m[0]).replace(/[?#].*$/, "");
    if (!seen.has(v)) {seen.add(v);matches.push(v);}
    if (!m[0]) pattern.lastIndex++;
  }
  return matches.sort();
}
function normalizeName(name) {
  if(typeof name!=="string" || name.length>320 || !ACCEPTED.test(name)) {
    throw new TypeError("Unsupported source name or extension");
  }
  return name.replace(/\\/g,"/").replace(/[\u0000-\u001f]/g,"");
}
function formatFlag(f) {
  return f.rule_id + ": " + f.title + " (line " + f.line + ")";
}
export function analyzeSource(name, source, sha256=null) {
  const path = normalizeName(name);
  if (typeof source!=="string") throw new TypeError("Expected text source");
  const bytes = new TextEncoder().encode(source).byteLength;
  if (bytes > MAX_FILE_BYTES) throw new RangeError("Source exceeds limit");
  const findings = [];
  const secret_candidates = [];
  let clipped = 0;
  const lines = source.split(/\r?\n/);
  for (let idx=0;idx<lines.length;idx++) {
    const line = lines[idx];
    if(line.length>8192) clipped++;
    const part = line.slice(0,8192);
    for (const r of RULES) {
      if(r.ext && !r.ext.test(path))continue;
      if(r.pattern.test(part) && findings.length<300) {
        findings.push({rule_id:r.id,severity:r.level,confidence:"heuristic",path,line:idx+1,title:r.title,recommendation:r.fix});
      }
    }
    for (const [kind,pattern] of SECRET_RULES) {
      if(pattern.test(part) && secret_candidates.length<100) {
        secret_candidates.push({kind,path,line:idx+1,severity:"high",value_included:false});
      }
    }
  }
  const api_paths=extract(ENDPOINT,source);
  const imports=extract(IMPORT,source);
  const storage=extract(STORAGE,source);
  const ids=new Set(findings.map(f=>f.rule_id));
  const score=Math.min(100, Array.from(ids).reduce((n,id)=> {
    const rule=RULES.find(r=>r.id===id);
    return n+(SEV[rule.level]||0);
  },0) + (secret_candidates.length?30:0));
  return {
    name:path.split("/").pop(),relative_path:path,origin:"local_browser_source",
    classification:"JS_SOURCE",bytes,sha256,api_paths,
    api_calls:[],imports,storage,privilege_literals:[],
    flags:findings.map(formatFlag),
    findings,secret_candidates,
    severity_score:score,clipped_lines:clipped,
    engine_version:ENGINE_VERSION
  };
}
export function summarize(files) {
  const list=files.filter(Boolean),apis=new Set();
  let ruleIndicators=0,secrets=0;
  for(const f of list) {
    (f.api_paths||[]).forEach(p=>apis.add(p));
    ruleIndicators+=(f.findings||[]).length;
    secrets+=(f.secret_candidates||[]).length;
  }
  return {files:list.length,unique_api_paths:apis.size,review_indicators:ruleIndicators,secret_candidates:secrets};
}
export function buildReport(files) {
  if (!Array.isArray(files) || files.length>MAX_FILES) throw new RangeError("Too many source files");
  return {schema_version:1,engine_version:ENGINE_VERSION,static_read_only:true,
    generated_utc:new Date().toISOString(),
    source:"browser_local_only",files:files.slice()};
}
