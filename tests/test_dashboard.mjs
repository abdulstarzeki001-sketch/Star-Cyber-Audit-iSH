import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import vm from 'node:vm';

const source = await readFile(new URL('../site/worker.js', import.meta.url), 'utf8');
const worker = (await import('data:text/javascript;base64,' + Buffer.from(source).toString('base64'))).default;
const response = await worker.fetch(new Request('https://audit.example/'));
const html = await response.text();
const sample = await (await worker.fetch(new Request('https://audit.example/api/sample'))).json();

class Element {
  constructor(id = '') { this.id=id; this.children=[]; this.listeners={}; this.value=''; this.className=''; this._text=''; this.parentElement={}; this.files=[]; }
  set textContent(value) { this._text=String(value);this.children=[]; }
  get textContent() { return this._text+this.children.map(child=>typeof child==='string'?child:child.textContent).join(''); }
  get firstChild() { return this.children[0]||null; }
  removeChild(child) { this.children.splice(this.children.indexOf(child),1); }
  append(...children) { this.children.push(...children); }
  addEventListener(name,callback) { this.listeners[name]=callback; }
  getBoundingClientRect() { return {width:600,height:230}; }
  getContext() { return new Proxy({}, { get(target,key) { return target[key] || (()=>{}); }, set(target,key,value) { target[key]=value; return true; } }); }
  setPointerCapture() {}
  click() { if(this.listeners.click)this.listeners.click({}); }
}

function browserHarness() {
  const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]);
  const elements=Object.fromEntries(ids.map(id=>[id,new Element(id)]));
  elements.filter.value='all';
  const calls=[];
  const document={getElementById:id=>elements[id],createElement:()=>new Element()};
  const window={devicePixelRatio:1,addEventListener(){}};
  class ResizeObserver { observe(){} }
  const fetch=async url=>{calls.push(url);return {ok:true,json:async()=>structuredClone(sample)}};
  const script=html.match(/<script>\s*([\s\S]*?)<\/script>/)?.[1];
  assert.ok(script,'the dashboard has a client script');
  vm.runInNewContext(script,{document,window,ResizeObserver,fetch,console,Blob,URL,setTimeout});
  return {elements,calls};
}

test('worker retains read-only routes and CSP', async()=>{
  assert.equal(response.status,200);
  assert.match(response.headers.get('content-security-policy'),/connect-src 'self'/);
  assert.equal((await worker.fetch(new Request('https://audit.example/',{method:'POST'}))).status,405);
  assert.equal((await worker.fetch(new Request('https://audit.example/health'))).status,200);
  assert.match(html,/خريطة نتائج التقرير/);
});

test('report selection uses relative paths and import stays local', async()=>{
  const {elements,calls}=browserHarness();
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal(elements.sceneFiles.textContent,'6');
  const before=calls.length;
  const report={files:[
    {name:'same.js',relative_path:'one/same.js',classification:'JS_SOURCE',api_paths:['/a'],flags:['first']},
    {name:'same.js',relative_path:'two/same.js',classification:'JS_SOURCE',api_paths:['/b'],flags:['second']},
  ]};
  await elements.upload.listeners.change({target:{files:[{size:100,text:async()=>JSON.stringify(report)}],value:'test'}});
  assert.equal(calls.length,before,'import must not send the report to any server');
  assert.equal(elements.sceneFiles.textContent,'2');
  assert.equal(elements.sceneApis.textContent,'2');
  assert.equal(elements.sceneFlags.textContent,'2');
  elements.files.children[1].click();
  assert.match(elements.detail.textContent,/two\/same\.js/);
  assert.match(elements.detail.textContent,/second/);
  assert.doesNotMatch(elements.detail.textContent,/first/);
  elements.audit3dLeft.click();elements.audit3dRight.click();elements.audit3dReset.click();
  const tooMany={files:Array.from({length:501},()=>({name:'item.js'}))};
  await elements.upload.listeners.change({target:{files:[{size:100,text:async()=>JSON.stringify(tooMany)}],value:'large'}});
  assert.match(elements.message.textContent,/500/);
  assert.equal(elements.sceneFiles.textContent,'2','oversized report must not silently replace the previous results');
});
