(() => {
  const byId = id => document.getElementById(id);
  const el = { refresh:byId('refresh'), checked:byId('checked-at'), lab:byId('lab-state'),
    labDescription:byId('lab-description'), goclaw:byId('goclaw-state'),
    goclawDescription:byId('goclaw-description'), detail:byId('node-detail-text'),
    detailDot:byId('detail-dot'), chatStatus:byId('chat-status'), messages:byId('chat-messages'),
    form:byId('chat-form'), input:byId('chat-input'), send:byId('send-message'), error:byId('chat-error') };
  const state = { csrf:null, configured:false, lab:'unknown', goclaw:'unknown', selected:'companion', busy:false, messages:[] };
  const stateLabels = {online:'متاحة',unavailable:'غير متاحة',auth:'تحتاج مصادقة',not_configured:'غير مهيأة',unknown:'لم يُفحص'};
  const nodeText = {
    companion:'اللوحة تعمل على هذا الجهاز.',
    lab:()=>({online:'نقطة الصحة المحددة تستجيب للفحص.',unavailable:'تعذر الوصول إلى نقطة صحة المختبر المضبوطة.',auth:'نقطة الصحة تستجيب وتحتاج إلى مصادقة.',not_configured:'اضبط عنوان نقطة الصحة من ملف الإعدادات أولاً.',unknown:'لم تُفحص خدمة المختبر بعد.'}[state.lab]),
    goclaw:()=>({online:'بوابة GoClaw تستجيب لفحص الصحة.',unavailable:'تعذر الوصول إلى بوابة GoClaw المضبوطة.',auth:'البوابة تستجيب وتحتاج إلى مصادقة.',unknown:'لم تُفحص بوابة GoClaw بعد.'}[state.goclaw])
  };
  function setTag(node,value) {
    node.replaceChildren(); const dot=document.createElement('span');dot.className='dot';node.append(dot,document.createTextNode(stateLabels[value]||stateLabels.unknown));
    node.className='state-tag '+(value==='online'?'good':value==='unavailable'?'bad':value==='auth'?'warning':'');
  }
  function syncDetail(){
    const value=nodeText[state.selected];el.detail.textContent=typeof value==='function'?value():value;
    const s=state.selected==='companion'?'online':state[state.selected];
    el.detailDot.className='dot '+(s==='online'?'good-dot':s==='unavailable'?'bad-dot':'warning-dot');
  }
  function selectNode(id){
    if (!Object.hasOwn(nodeText,id)) return;state.selected=id;
    document.querySelectorAll('.node-button').forEach(button=>{const chosen=button.dataset.node===id;button.classList.toggle('selected',chosen);button.setAttribute('aria-pressed',String(chosen));});
    window.StarScene?.select(id);syncDetail();
  }
  document.querySelectorAll('.node-button').forEach(button=>button.addEventListener('click',()=>selectNode(button.dataset.node)));
  window.StarScene?.onSelect(selectNode);
  function syncChat(){
    const ready=state.configured&&state.goclaw==='online';
    el.send.disabled=!ready||state.busy;
    if (!state.configured) el.chatStatus.textContent='يلزم إعداد رمز الوصول في الخادم';
    else if (state.goclaw!=='online') el.chatStatus.textContent='بانتظار اتصال بوابة المساعد';
    else el.chatStatus.textContent='البوابة متاحة · جاهز للمراسلة';
  }
  async function session(){
    const res=await fetch('/api/session',{cache:'no-store'});if(!res.ok)throw new Error('session');
    const data=await res.json();state.csrf=data.csrf;state.configured=data.chat_configured;syncChat();
  }
  async function refresh(){
    el.refresh.disabled=true;el.checked.textContent='جارٍ فحص الخدمات...';
    try{
      const res=await fetch('/api/status',{cache:'no-store'});if(!res.ok)throw new Error('status');
      const data=await res.json();state.lab=data.lab.state;state.goclaw=data.goclaw.state;state.configured=data.chat_configured;
      setTag(el.lab,state.lab);setTag(el.goclaw,state.goclaw);
      el.labDescription.textContent=data.lab.description;el.goclawDescription.textContent=data.goclaw.description;
      const report=data.report||{state:'missing'};
      byId('report-message').textContent=report.state==='available'?'من تقرير analysis.json المحلي؛ المؤشرات ليست ثغرات مؤكدة.':(report.description||'لم يُعثر على تقرير محلي.');
      byId('report-files').textContent=report.state==='available'?report.files:'—';
      byId('report-apis').textContent=report.state==='available'?report.api_paths:'—';
      byId('report-flags').textContent=report.state==='available'?report.flags:'—';
      const date=new Date(data.checked_at);el.checked.textContent='آخر تحقق: '+date.toLocaleTimeString('ar-IQ',{hour:'2-digit',minute:'2-digit',second:'2-digit'});
      window.StarScene?.setStates({lab:state.lab,goclaw:state.goclaw});syncDetail();syncChat();
    }catch{el.checked.textContent='تعذر فحص الخدمات';state.goclaw='unknown';syncChat();}
    finally{el.refresh.disabled=false;}
  }
  el.refresh.addEventListener('click',refresh);
  function addMessage(role, content){
    const box=document.createElement('div');box.className='message '+(role==='user'?'user-message':'assistant-message');
    const label=document.createElement('span');label.className='message-label';label.textContent=role==='user'?'YOU':'STAR ASSISTANT';
    const p=document.createElement('p');p.textContent=content;box.append(label,p);el.messages.append(box);el.messages.scrollTop=el.messages.scrollHeight;
  }
  el.form.addEventListener('submit',async event=>{
    event.preventDefault();el.error.hidden=true;const text=el.input.value.trim();if(!text||state.busy||!state.csrf)return;
    const proposed=[...state.messages,{role:'user',content:text}].slice(-19);
    addMessage('user',text);el.input.value='';state.busy=true;syncChat();
    try{
      const res=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json','X-Star-CSRF':state.csrf},body:JSON.stringify({messages:proposed})});
      const data=await res.json();if(!res.ok)throw new Error(data.error||'تعذّر إرسال الرسالة');
      addMessage('assistant',data.reply);state.messages=[...proposed,{role:'assistant',content:data.reply}].slice(-18);
    }catch(error){el.error.textContent=error.message||'تعذّر إرسال الرسالة';el.error.hidden=false;el.input.value=text;}
    finally{state.busy=false;syncChat();}
  });
  el.input.addEventListener('keydown',event=>{if(event.key==='Enter'&&(event.ctrlKey||event.metaKey)){event.preventDefault();el.form.requestSubmit();}});
  document.querySelectorAll('.nav-link').forEach(link=>link.addEventListener('click',()=>{document.querySelectorAll('.nav-link').forEach(a=>a.classList.remove('active'));link.classList.add('active');}));
  session().catch(()=>{el.chatStatus.textContent='تعذر إعداد الجلسة المحلية';}).finally(refresh);
})();
