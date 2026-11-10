/* Projected 3D illustration: logical components, not an observed trace. */
(() => {
  const canvas = document.getElementById('scene-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  const models = [
    { id: 'companion', x: -2.55, label: 'LOCAL UI', color: '#94e6c3' },
    { id: 'lab', x: 0, label: 'LAB API', color: '#a6b5b0' },
    { id: 'goclaw', x: 2.55, label: 'GOCLAW', color: '#b5afe8' },
  ];
  let selected = 'companion', yaw = -0.23, pitch = 0.67;
  let width = 0, height = 0, pointer = null, onSelect = () => {};
  const states = { companion: 'online', lab: 'unknown', goclaw: 'unknown' };

  function resize() {
    const box = canvas.getBoundingClientRect();
    width = box.width; height = box.height;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.max(1, Math.round(width * dpr));
    canvas.height = Math.max(1, Math.round(height * dpr));
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    render();
  }
  function project(point) {
    const [x, y, z] = point;
    const rotatedX = x * Math.cos(yaw) - z * Math.sin(yaw);
    const rotatedZ = x * Math.sin(yaw) + z * Math.cos(yaw);
    const rotatedY = y * Math.cos(pitch) - rotatedZ * Math.sin(pitch);
    const depth = y * Math.sin(pitch) + rotatedZ * Math.cos(pitch);
    const unit = Math.min(width / 9.3, height / 5.5);
    const scale = unit * 9 / (9 + depth);
    return { x: width * .5 + rotatedX * scale, y: height * .63 - rotatedY * scale, depth };
  }
  function poly(points, fill, stroke, lineWidth=1) {
    ctx.beginPath(); points.forEach((p, i) => { const q = project(p); i ? ctx.lineTo(q.x,q.y) : ctx.moveTo(q.x,q.y); });
    ctx.closePath(); if (fill) { ctx.fillStyle = fill; ctx.fill(); }
    if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = lineWidth; ctx.stroke(); }
  }
  function line(points, color, widthPx=1, dash=[]) {
    ctx.beginPath(); points.forEach((p,i) => { const q=project(p); i?ctx.lineTo(q.x,q.y):ctx.moveTo(q.x,q.y); });
    ctx.strokeStyle=color;ctx.lineWidth=widthPx;ctx.setLineDash(dash);ctx.stroke();ctx.setLineDash([]);
  }
  function floor() {
    const y = -1.05;
    for (let x=-5; x<=5; x++) line([[x,y,-3],[x,y,3]],'rgba(144,193,170,0.10)');
    for (let z=-3; z<=3; z++) line([[-5,y,z],[5,y,z]],'rgba(144,193,170,0.10)');
    poly([[-4.15,y,-1.35],[4.15,y,-1.35],[4.15,y,1.35],[-4.15,y,1.35]],'rgba(70,131,103,0.08)','rgba(128,184,156,0.20)');
    // Lines convey a proposed arrangement only; there are no measured traces.
    line([[-2.1,y+.03,0],[-.55,y+.03,0]],'rgba(163,213,186,.45)',1.2,[4,5]);
    line([[.55,y+.03,0],[2.1,y+.03,0]],'rgba(163,213,186,.45)',1.2,[4,5]);
  }
  function colorFor(id) {
    if (id === 'companion') return '#8ee5c5';
    if (states[id] === 'online') return '#8ee5c5';
    if (states[id] === 'auth') return '#e5c28d';
    if (states[id] === 'unavailable') return '#d9938a';
    return '#98aaa3';
  }
  function tower(model) {
    const x=model.x, z=0, bottom=-.96, top=.63, hw=.57, hd=.48;
    const base=[x-hw,bottom,z-hd], a=[x+hw,bottom,z-hd], b=[x+hw,bottom,z+hd], c=[x-hw,bottom,z+hd];
    const upper=[[x-hw,top,z-hd],[x+hw,top,z-hd],[x+hw,top,z+hd],[x-hw,top,z+hd]];
    const lower=[base,a,b,c];
    const faces=[];
    for(let i=0;i<4;i++) { const j=(i+1)%4; const pts=[lower[i],lower[j],upper[j],upper[i]];
      faces.push({pts,depth:pts.reduce((n,p)=>n+project(p).depth,0)/4,fill:i%2?'#253b36':'#1c302e'}); }
    faces.sort((u,v)=>v.depth-u.depth).forEach(f=>poly(f.pts,f.fill,'rgba(143,184,164,.38)'));
    poly(upper,'#39594c',selected===model.id?'#a6f0ce':'rgba(164,206,181,.6)',selected===model.id?2:1);
    const frontZ=.486;
    for(let j=0;j<3;j++) {
      const y=-.6+j*.34;
      line([[x-.37,y,frontZ],[x+.25,y,frontZ]],'rgba(171,218,190,.42)',2);
      const led=project([x+.37,y,frontZ]);ctx.beginPath();ctx.arc(led.x,led.y,2,0,Math.PI*2);ctx.fillStyle=colorFor(model.id);ctx.fill();
    }
    const center=project([x,top+.18,0]);
    ctx.beginPath();ctx.arc(center.x,center.y,selected===model.id?4.5:3,0,Math.PI*2);ctx.fillStyle=colorFor(model.id);ctx.fill();
    const text=project([x,-1.22,.52]);
    ctx.fillStyle='#bccfc4';ctx.font='700 9px Arial, sans-serif';ctx.textAlign='center';ctx.fillText(model.label,text.x,text.y+11);
    model.hit=project([x,0,0]);
  }
  function render(){
    if (!width || !height) return;
    ctx.clearRect(0,0,width,height);floor();
    [...models].sort((a,b)=>project([b.x,0,0]).depth-project([a.x,0,0]).depth).forEach(tower);
  }
  canvas.addEventListener('pointerdown',event=>{pointer={id:event.pointerId,x:event.clientX,y:event.clientY,startX:event.clientX,startY:event.clientY,moved:false};canvas.setPointerCapture(event.pointerId);});
  canvas.addEventListener('pointermove',event=>{if(!pointer||pointer.id!==event.pointerId)return;const dx=event.clientX-pointer.x,dy=event.clientY-pointer.y;pointer.moved ||= Math.hypot(event.clientX-pointer.startX,event.clientY-pointer.startY)>5;yaw+=dx*.009;pitch=Math.max(.35,Math.min(1.02,pitch+dy*.004));pointer.x=event.clientX;pointer.y=event.clientY;render();});
  canvas.addEventListener('pointerup',event=>{if(!pointer||pointer.id!==event.pointerId)return;if(!pointer.moved){const r=canvas.getBoundingClientRect(),x=event.clientX-r.left,y=event.clientY-r.top;let best=null,dist=Infinity;for(const m of models){if(!m.hit)continue;const d=Math.hypot(m.hit.x-x,m.hit.y-y);if(d<dist){best=m;dist=d;}}if(best&&dist<60)onSelect(best.id);}pointer=null;});
  canvas.addEventListener('pointercancel',()=>{pointer=null;});
  document.getElementById('rotate-left').addEventListener('click',()=>{yaw-=.25;render();});
  document.getElementById('rotate-right').addEventListener('click',()=>{yaw+=.25;render();});
  document.getElementById('reset-view').addEventListener('click',()=>{yaw=-.23;pitch=.67;render();});
  if ('ResizeObserver' in window) new ResizeObserver(resize).observe(canvas.parentElement); else window.addEventListener('resize',resize);
  window.StarScene={select(id){selected=id;render();},setStates(value){Object.assign(states,value);render();},onSelect(callback){onSelect=callback;}};
  resize();
})();
