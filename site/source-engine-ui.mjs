import {analyzeSource, summarize, buildReport, MAX_FILES, MAX_FILE_BYTES, MAX_TOTAL_BYTES, ACCEPTED} from "./source-analysis-core.mjs";
const $ = id => document.getElementById(id);
const el = (tag,cls,value) => {
  const n=document.createElement(tag);if(cls)n.className=cls;
  if(value!==undefined)n.textContent=String(value);return n;
};
const section=el("section","engine-section");
section.id="sourceEngine";
const top=el("div","engine-head");
const title=el("div");title.append(el("span","eyebrow","NATIVE SOURCE ANALYSIS"),el("h2","","محرك فحص الشيفرة المحلية"),el("p","engine-desc","الآن تستطيع اختيار ملفات JavaScript وTypeScript وPython وHTML لفحصها داخل هاتفك مباشرة. النتائج مؤشرات مراجعة، وليست ثغرات مثبتة."));
const badge=el("span","engine-badge","NO UPLOAD · NO EXECUTION");
top.append(title,badge);section.append(top);
const controls=el("div","engine-controls");
const label=el("label","btn btn-main","⌁ اختيار ملفات الشيفرة");
label.htmlFor="sourceInput";
const input=el("input");input.id="sourceInput";input.type="file";input.multiple=true;input.accept=".js,.mjs,.cjs,.jsx,.ts,.tsx,.py,.html";
const exportButton=el("button","btn btn-outline","↓ تصدير analysis.json");
exportButton.type="button";exportButton.id="sourceExport";exportButton.disabled=true;
const clearButton=el("button","btn btn-outline","↺ مسح نتائج الفحص");
clearButton.type="button";
controls.append(label,input,exportButton,clearButton);section.append(controls);
const note=el("p","engine-note","حدود التشغيل: "+MAX_FILES+" ملفًا، حتى "+Math.round(MAX_FILE_BYTES/1048576)+" MB للملف الواحد، مع حد إجمالي "+Math.round(MAX_TOTAL_BYTES/1048576)+" MB. لا تُحفظ الملفات على الخادم ولا تُرسل إلى OpenAI.");
section.append(note);
const progress=el("p","engine-progress");progress.setAttribute("aria-live","polite");section.append(progress);
const stats=el("div","engine-stats");
section.append(stats);
const results=el("div","engine-results");
section.append(results);
const hero=document.querySelector(".hero");
if(hero)hero.insertAdjacentElement("afterend",section);
let records=[];
function stat(n,k){const s=el("div","engine-stat");s.append(el("strong","",n),el("span","",k));return s;}
function draw(){
 const s=summarize(records);stats.replaceChildren(
  stat(s.files,"ملفات مفحوصة"),stat(s.unique_api_paths,"مراجع API"),stat(s.review_indicators,"مؤشرات مراجعة"),stat(s.secret_candidates,"مرشحات أسرار")
 );
 results.replaceChildren();
 if(!records.length){results.append(el("div","engine-empty","اختر ملفات من جهازك لبدء الفحص الفعلي. لا يحتاج هذا المحرك اتصالًا بالخادم."));return;}
 const list=el("div","engine-list");
 for(const f of records){
  const item=el("details","engine-file");
  const summary=el("summary","",f.relative_path);
  summary.append(el("span","engine-score","Risk index "+f.severity_score+"/100"));
  item.append(summary,el("p","engine-descriptor","SHA-256: "+String(f.sha256||"not available")+" · "+f.bytes+" bytes · clipped long lines: "+f.clipped_lines));
  const endpoints=el("div","engine-tags");
  for (const path of f.api_paths.slice(0,40)) endpoints.append(el("span","engine-tag",path));
  const meta=el("div","engine-meta");meta.append(el("h4","","API references"),endpoints.childNodes.length?endpoints:el("p","engine-empty","لا توجد مسارات في هذا الملف."));
  item.append(meta);
  item.append(el("h4","","Review findings"));
  if(!f.findings.length&&!f.secret_candidates.length)item.append(el("p","engine-empty","لا توجد مؤشرات بالقواعد الحالية، وهذا لا يعني أن الملف آمن."));
  for(const finding of f.findings.slice(0,50)){
   const box=el("div","engine-finding");
   box.append(el("b","",finding.rule_id+" · "+finding.severity+" · line "+finding.line),el("div","",finding.title),el("small","",finding.recommendation));item.append(box);
  }
  for(const s of f.secret_candidates.slice(0,25)){
   const box=el("div","engine-finding engine-secret");box.append(el("b","",s.kind+" · line "+s.line),el("small","","مرشح سر حساس؛ لم تُعرض قيمته. افحصه محليًا."));item.append(box);
  }
  list.append(item);
 }
 results.append(list);
}
function toHex(buffer){return Array.from(new Uint8Array(buffer), b=>b.toString(16).padStart(2,"0")).join("");}
async function sha(bytes){return toHex(await crypto.subtle.digest("SHA-256",bytes));}
async function handleFiles(files){
 const arr=Array.from(files||[]);
 if(arr.length>MAX_FILES){progress.textContent="العدد أكبر من الحد المسموح؛ اختر "+MAX_FILES+" ملفًا أو أقل.";return;}
 let total=0;
 for(const file of arr){
  if(!ACCEPTED.test(file.name)||file.size>MAX_FILE_BYTES){progress.textContent="ملف غير مدعوم أو كبير: "+file.name;return;}
  total+=file.size;
  if(total>MAX_TOTAL_BYTES){progress.textContent="الحجم الإجمالي يتجاوز الحد الآمن.";return;}
 }
 const next=[];progress.textContent="يجري تحليل الملفات محليًا، دون اتصال بالشبكة...";
 for(const file of arr){
  try {
   const bytes=await file.arrayBuffer();
   const digest=await sha(bytes);
   const content=new TextDecoder("utf-8",{fatal:false}).decode(bytes);
   const item=analyzeSource(file.name,content,digest);
   next.push(item);
  } catch(e) {progress.textContent="فشل تحليل ملف: "+file.name+" ("+e.name+")";return;}
 }
 records=next;exportButton.disabled=!records.length;draw();
 progress.textContent="اكتمل فحص "+records.length+" ملفًا محليًا. لا توجد طلبات رفع أو تنفيذ للشيفرات.";
}
input.addEventListener("change",()=>{handleFiles(input.files);input.value="";});
clearButton.addEventListener("click",()=>{records=[];exportButton.disabled=true;progress.textContent="مُسحت نتائج التحليل من ذاكرة الصفحة.";draw();});
exportButton.addEventListener("click",()=>{
 if(!records.length)return;
 const report=buildReport(records);
 const blob=new Blob([JSON.stringify(report,null,2)],{type:"application/json"});
 const url=URL.createObjectURL(blob);const anchor=el("a");anchor.href=url;anchor.download="analysis.json";document.body.append(anchor);anchor.click();anchor.remove();
 setTimeout(()=>URL.revokeObjectURL(url),1000);
 progress.textContent="تم تصدير analysis.json. يمكن استيراده في مستكشف الأدلة بالأعلى.";
});
draw();
