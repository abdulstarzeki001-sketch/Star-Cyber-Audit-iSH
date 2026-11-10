import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import vm from 'node:vm';

const app = await readFile(new URL('../tools/companion/static/app.js',import.meta.url),'utf8');
const html = await readFile(new URL('../tools/companion/static/index.html',import.meta.url),'utf8');

class Element {
  constructor(){this.children=[];this.listeners={};this.value='';this.textContent='';this.disabled=false;this.hidden=false;this.classList={toggle(){},remove(){},add(){}};}
  append(...children){this.children.push(...children)}
  replaceChildren(...children){this.children=[...children]}
  addEventListener(name,fn){this.listeners[name]=fn}
  setAttribute(){}
}

test('authenticated health allows chat and long Arabic exchanges respect server limits',async()=>{
  const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]);
  const nodes=Object.fromEntries(ids.map(id=>[id,new Element()]));
  const document={getElementById:id=>nodes[id],createElement:()=>new Element(),createTextNode:text=>text,querySelectorAll:()=>[]};
  const posts=[];
  const fetch=async (url,options={})=>{
    if(url==='/api/session')return{ok:true,json:async()=>({csrf:'test',chat_configured:true})};
    if(url==='/api/status')return{ok:true,json:async()=>({checked_at:new Date().toISOString(),
      lab:{state:'not_configured',description:'not configured'},goclaw:{state:'auth',description:'authentication required'},
      report:{state:'missing'},chat_configured:true})};
    assert.equal(url,'/api/chat');
    const bytes=new TextEncoder().encode(options.body).length;
    const body=JSON.parse(options.body);
    assert.ok(bytes<=64*1024,`payload was ${bytes} bytes`);
    for(const m of body.messages)assert.ok(Array.from(m.content).length<=6000);
    posts.push(body);
    return{ok:true,json:async()=>({reply:'رد '.repeat(5000)})};
  };
  vm.runInNewContext(app,{document,window:{},fetch,TextEncoder,Date,JSON,Object,String,Array});
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal(nodes['send-message'].disabled,false,'401 health must not prevent an authenticated chat attempt');
  for(let i=0;i<9;i++){
    nodes['chat-input'].value='ع'.repeat(6000);
    await nodes['chat-form'].listeners.submit({preventDefault(){}});
  }
  assert.equal(posts.length,9,'long exchanges must not leave the chat unusable');
  assert.ok(posts.at(-1).messages.length<19,'history should be bounded by byte size');
});
