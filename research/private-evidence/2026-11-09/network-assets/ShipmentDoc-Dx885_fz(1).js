import{d as j,B as S,u as A,c as y,K as q,k as m,g as c,j as t,i as d,h as x,_ as I,t as o,f as L,l as h,L as U,p as N,M as D,m as O,N as R,O as B,P as k,z as C,b as $,w as E,F,C as M}from"./index-gleMzSil.js";import{_ as H,a as T}from"./iraqEagle-BF406BBV.js";import{Q}from"./browser-3Qg8aFGH.js";const V={class:"flex min-h-screen flex-col bg-gray-50 p-5 dark:bg-gray-900"},P={class:"sticky top-0 z-50 border-b border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800"},W={class:"container mx-auto px-4"},K={class:"flex h-16 items-center justify-between"},Y={class:"flex items-center gap-3"},Z={class:"bg-primary-100 dark:bg-primary-900 flex h-10 w-10 items-center justify-center rounded-lg"},G={class:"hidden md:block"},J={class:"text-lg font-bold text-gray-900 dark:text-gray-100"},X={class:"flex items-center gap-3"},tt={class:"text-sm font-semibold text-white"},et={class:"hidden text-sm font-medium text-gray-700 sm:inline dark:text-gray-300"},at={class:"flex-1"},rt={class:"border-t border-gray-200 bg-white py-6 dark:border-gray-700 dark:bg-gray-800"},ot={class:"container mx-auto px-4"},nt={class:"flex flex-col items-center justify-between gap-4 sm:flex-row"},st={class:"text-center text-sm text-gray-600 sm:text-left dark:text-gray-400"},it={class:"flex gap-3"},lt={href:"#",class:"hover:bg-primary-100 hover:text-primary-600 dark:hover:bg-primary-900 dark:hover:text-primary-400 flex h-8 w-8 items-center justify-center rounded-full bg-gray-100 text-gray-600 transition-colors dark:bg-gray-700 dark:text-gray-400","aria-label":"Facebook"},dt={href:"#",class:"hover:bg-primary-100 hover:text-primary-600 dark:hover:bg-primary-900 dark:hover:text-primary-400 flex h-8 w-8 items-center justify-center rounded-full bg-gray-100 text-gray-600 transition-colors dark:bg-gray-700 dark:text-gray-400","aria-label":"Twitter"},ct={href:"#",class:"hover:bg-primary-100 hover:text-primary-600 dark:hover:bg-primary-900 dark:hover:text-primary-400 flex h-8 w-8 items-center justify-center rounded-full bg-gray-100 text-gray-600 transition-colors dark:bg-gray-700 dark:text-gray-400","aria-label":"Instagram"},mt=j({__name:"CompanyOwnerLayout",props:{companyUserInfo:{}},setup(a){const u=S(),b=A(),g=a,s=y(()=>u.getCompanyOwnerDetails),_=y(()=>[[{label:"تسجيل الخروج",icon:"i-lucide-log-out",onSelect:()=>{b.logout()}}]]),i=y(()=>Array.isArray(s.value)&&s.value.length>0?s.value[0]?.company_name_project||"بوابة أصحاب الشركات":s.value&&typeof s.value=="object"&&"company_name_project"in s.value&&s.value.company_name_project||"بوابة أصحاب الشركات"),e=y(()=>u.isAuthenticatedOwner&&g.companyUserInfo&&g.companyUserInfo.UsFirstName||"المستخدم"),n=r=>{if(!r)return"M";const l=r.trim().split(" ");return l.length>=2?l[0][0]+l[1][0]:l[0][0]};return(r,l)=>{const p=I,v=q("router-link"),f=R,w=O,z=D;return c(),m("div",V,[t("nav",P,[t("div",W,[t("div",K,[t("div",Y,[d(v,{to:{name:"CompanyOwner"},class:"flex items-center gap-3 hover:opacity-80"},{default:x(()=>[t("div",Z,[d(p,{name:"i-lucide-building-2",class:"text-primary-600 dark:text-primary-400 h-6 w-6"})]),t("div",G,[t("h1",J,o(i.value),1)])]),_:1})]),t("div",X,[d(U),N(u).isAuthenticatedOwner?(c(),L(z,{key:0,items:_.value},{default:x(()=>[d(w,{color:"neutral",variant:"ghost",class:"gap-2"},{default:x(()=>[d(f,{alt:e.value,size:"sm",ui:{background:"bg-primary-500 dark:bg-primary-600"}},{fallback:x(()=>[t("span",tt,o(n(e.value)),1)]),_:1},8,["alt"]),t("span",et,o(e.value),1),d(p,{name:"i-lucide-chevron-down",class:"h-4 w-4 text-gray-500"})]),_:1})]),_:1},8,["items"])):h("",!0)])])])]),t("main",at,[B(r.$slots,"default",{},void 0,!0)]),t("footer",rt,[t("div",ot,[t("div",nt,[t("div",st,[t("p",null,"© "+o(new Date().getFullYear())+" الهيئة العامة للجمارك العراقية",1),l[0]||(l[0]=t("p",{class:"mt-1"},"جميع الحقوق محفوظة",-1))]),l[1]||(l[1]=k('<div class="flex flex-wrap justify-center gap-4 text-sm" data-v-147241a7><a href="#" class="hover:text-primary-600 dark:hover:text-primary-400 text-gray-600 transition-colors dark:text-gray-400" data-v-147241a7> سياسة الخصوصية </a><span class="text-gray-300 dark:text-gray-600" data-v-147241a7>|</span><a href="#" class="hover:text-primary-600 dark:hover:text-primary-400 text-gray-600 transition-colors dark:text-gray-400" data-v-147241a7> شروط الاستخدام </a><span class="text-gray-300 dark:text-gray-600" data-v-147241a7>|</span><a href="#" class="hover:text-primary-600 dark:hover:text-primary-400 text-gray-600 transition-colors dark:text-gray-400" data-v-147241a7> اتصل بنا </a></div>',1)),t("div",it,[t("a",lt,[d(p,{name:"i-lucide-facebook",class:"h-4 w-4"})]),t("a",dt,[d(p,{name:"i-lucide-twitter",class:"h-4 w-4"})]),t("a",ct,[d(p,{name:"i-lucide-instagram",class:"h-4 w-4"})])])])])])])}}}),Bt=C(mt,[["__scopeId","data-v-147241a7"]]),ut={class:"qr-document-root"},pt={class:"doc-viewport"},gt={class:"header-clean"},vt={class:"header-left"},ft={class:"doc-meta"},yt={class:"meta-line"},ht={class:"meta-value"},bt={class:"meta-line"},xt={class:"meta-value"},_t={class:"meta-line"},wt={class:"meta-value"},kt={class:"content"},$t={class:"subject-row"},jt={class:"subject-field"},Ct={class:"info-section",dir:"rtl"},zt={class:"info-table"},St={key:0},At={key:1},qt={key:2},It={style:{direction:"ltr","text-align":"right"}},Lt={key:0,class:"qr-wrap large-qr"},Ut=["src"],Nt=j({__name:"ShipmentDoc",props:{doc:{}},setup(a){const u=a,b=$(null),g=y(()=>{const i=u.doc?.items;return Array.isArray(i)?i.map(e=>({item_name:String(e?.item_name??"").trim(),production_capacity:e?.production_capacity??"",unit:String(e?.unit??"").trim()})):[]}),s=$("");E(()=>u.doc,async i=>{const e=i?.qr_code||i?.response?.qr_code;let n="";if(e){const r=String(e).trim();if(r.startsWith("data:image")){s.value=r;return}if(r.startsWith("https://customs-uboor.ur.gov.iq/robot?url="))n=r.split("url=")[1]||"";else if(/^[A-Za-z0-9+/=]+$/.test(r)&&r.length>80){s.value=`data:image/png;base64,${r}`;return}else n=r}else{const r=i?.license_approval_number||i?.vehicle_number||i?.driver_name||"";r&&(n=r)}if(n)try{s.value=await Q.toDataURL(n,{width:200,margin:1})}catch{s.value=""}else s.value=""},{immediate:!0,deep:!0});const _=()=>{const i=b.value;if(!i){window.print();return}const e=i.outerHTML,n=window.open("","_blank","width=900,height=1000");if(!n)return;const r=[];r.push('<meta charset="utf-8" />'),r.push("<title>طباعة الوثيقة</title>"),Array.from(document.querySelectorAll("style")).forEach(v=>r.push(v.outerHTML)),Array.from(document.querySelectorAll('link[rel="stylesheet"]')).forEach(v=>{const f=v.getAttribute("href");if(!f)return;const w=f.includes("?")?"&":"?";r.push(`<link rel="stylesheet" href="${f}${w}print_copy=${Date.now()}" />`)}),r.push(`
    <style>
      @page { size: A4; margin: 0; }
      html, body {
        margin: 0;
        padding: 0;
        background: #fff;
      }
      .a4-page {
        width: 210mm !important;
        height: 296mm !important; /* Force single page height */
        margin: 0 auto;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        padding: 10mm !important; /* Reduced padding */
        overflow: hidden;
        /* Reset positioning from screen view */
        position: static !important;
        transform: none !important;
        box-shadow: none !important;
        border: none !important;
      }
      .a4-page .content {
        flex: 1 1 auto;
        display: flex;
        flex-direction: column;
        gap: 4px !important;
      }

      /* Compact Header */
      .header-clean { padding: 0 !important; gap: 4px !important; }
      .center-logo { width: 80px !important; height: 80px !important; }
      .office-lines { font-size: 0.75rem !important; line-height: 1.2 !important; }
      .doc-meta { gap: 2px !important; }
      .doc-meta .meta-value { font-size: 0.8rem !important; min-width: auto !important; }
      .meta-label { font-size: 0.8rem !important; }

      .divider { margin: 4px 0 !important; }
      .doc-title { margin: 4px 0 !important; font-size: 1.2rem !important; }

      /* Compact Body */
      .subject-row { margin-bottom: 4px !important; font-size: 0.9rem !important; }
      .subject-field { padding: 2px 6px !important; }

      .info-table th { font-size: 0.8rem !important; padding: 2px 4px !important; }
      .info-table td { font-size: 0.8rem !important; padding: 1px 4px !important; }

      /* Compact QR & Notes */
      .qr-wrap { margin-top: 4px !important; }
      .large-qr .barcode-img { width: 40mm !important; padding: 2px !important; }
      .notes p { margin: 1px 0 !important; font-size: 0.75rem !important; }

      /* Compact Footer */
      .doc-footer {
        margin-top: auto;
        page-break-inside: avoid;
        padding-top: 4px !important;
        gap: 4px !important;
      }
      .footer-logo { width: 50px !important; height: 40px !important; }
      .doc-footer .small { font-size: 0.65rem !important; line-height: 1.2; }

      /* Hide UI elements */
      button,
      .print-toolbar,
      .download-toolbar,
      .preview-overlay,
      .preview-card,
      .action-buttons,
      .doc-actions {
        display: none !important;
      }
      * {
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
      }
    </style>
  `),n.document.open(),n.document.write(`
    <!doctype html>
    <html dir="rtl" lang="ar">
      <head>
        ${r.join(`
`)}
      </head>
      <body>
        ${e}
      </body>
    </html>
  `),n.document.close(),n.onload=()=>{n.focus(),n.print(),n.close()}};return(i,e)=>(c(),m("div",ut,[t("div",pt,[t("div",{class:"a4-page",dir:"rtl",ref_key:"docRef",ref:b},[t("header",gt,[e[3]||(e[3]=k('<div class="header-right" data-v-435b7756><div class="office-lines small" data-v-435b7756><div style="text-align:right;" data-v-435b7756>جمهورية العراق</div><div style="text-align:right;" data-v-435b7756> وزارة المالية</div><div style="text-align:right;" data-v-435b7756> الهيئــة العامــة للكمـــارك </div></div></div><div class="header-center logo-wrap" data-v-435b7756><img src="'+H+'" alt="Logo" class="center-logo" data-v-435b7756></div>',2)),t("div",vt,[t("div",ft,[t("div",yt,[e[0]||(e[0]=t("span",{class:"meta-label"},"رقم الوثيقة",-1)),t("span",ht,o(a.doc?.doc_id||"—"),1)]),t("div",bt,[e[1]||(e[1]=t("span",{class:"meta-label"},"تاريخ إنشاء الوثيقة",-1)),t("span",xt,o(a.doc?.date_str||a.doc?.current_date||""),1)]),t("div",_t,[e[2]||(e[2]=t("span",{class:"meta-label"},"التوقيت",-1)),t("span",wt,o(a.doc?.time_str||""),1)])]),t("div",{class:"doc-actions"},[t("button",{type:"button",class:"print-btn",title:"طباعة الوثيقة",onClick:_}," طباعة الوثيقة ")])])]),e[25]||(e[25]=t("hr",{class:"divider"},null,-1)),t("div",kt,[e[23]||(e[23]=t("h2",{class:"doc-title"},"منصة المنتج المحلي",-1)),t("div",$t,[e[4]||(e[4]=t("strong",null,"الموضوع /",-1)),t("div",jt,o(a.doc?.subject||""),1)]),t("div",Ct,[t("table",zt,[e[21]||(e[21]=t("colgroup",null,[t("col",{style:{width:"35%"}}),t("col",{style:{width:"65%"}})],-1)),e[22]||(e[22]=t("thead",null,[t("tr",null,[t("th",{colspan:"2",class:"text-white"},"المعلومات الشخصية")])],-1)),t("tbody",null,[a.doc?.checkpoint_name_control?(c(),m("tr",St,[e[5]||(e[5]=t("td",null,"اسم سيطرة الدخول",-1)),t("td",null,o(a.doc.checkpoint_name_control),1)])):h("",!0),t("tr",null,[e[6]||(e[6]=t("td",null,"اسم السائق",-1)),t("td",null,o(a.doc?.driver_name||""),1)]),t("tr",null,[e[7]||(e[7]=t("td",null,"رقم العجلة",-1)),t("td",null,o(a.doc?.vehicle_number||""),1)]),t("tr",null,[e[8]||(e[8]=t("td",null,"محافظة تسجيل العجلة",-1)),t("td",null,o(a.doc?.registration_governorate||""),1)]),t("tr",null,[e[9]||(e[9]=t("td",null,"نوع / تفاصيل الحمولة",-1)),t("td",null,o(a.doc?.cargo_typedetails||""),1)]),t("tr",null,[e[10]||(e[10]=t("td",null,"الوزن / الكمية",-1)),t("td",null,o(a.doc?.weight_quantity||""),1)]),t("tr",null,[e[11]||(e[11]=t("td",null,"الوجهة النهائية / المحافظة",-1)),t("td",null,o(a.doc?.destination_governorate||""),1)]),t("tr",null,[e[12]||(e[12]=t("td",null,"اسم المحافظة",-1)),t("td",null,o(a.doc?.governorate_name||""),1)]),t("tr",null,[e[13]||(e[13]=t("td",null,"اسم الشركة / المشروع",-1)),t("td",null,o(a.doc?.company_name_project||a.doc?.company_name||""),1)]),a.doc?.company_type?(c(),m("tr",At,[e[14]||(e[14]=t("td",null,"نوع الشركة",-1)),t("td",null,o(a.doc.company_type),1)])):h("",!0),t("tr",null,[e[15]||(e[15]=t("td",null,"الجهة المانحة للإجازة / الموافقة",-1)),t("td",null,o(a.doc?.granting_license_approval||""),1)]),t("tr",null,[e[16]||(e[16]=t("td",null,"رقم الإجازة / الموافقة",-1)),t("td",null,o(a.doc?.license_approval_number||""),1)]),t("tr",null,[e[17]||(e[17]=t("td",null,"تاريخ الإجازة / الموافقة",-1)),t("td",null,o(a.doc?.license_approval_date||""),1)]),t("tr",null,[e[18]||(e[18]=t("td",null,"منطوق الإجازة / الاختصاص",-1)),t("td",null,o(a.doc?.license_text_specialization||""),1)]),t("tr",null,[e[19]||(e[19]=t("td",null,"العلامة التجارية",-1)),t("td",null,o(a.doc?.brand||""),1)]),a.doc?.items&&a.doc.items.length||g.value.length?(c(),m("tr",qt,[...e[20]||(e[20]=[t("th",{colspan:"2",class:"text-white info-header"},"المواد / المنتجات المرخَّصة",-1)])])):h("",!0),(c(!0),m(F,null,M(g.value,(n,r)=>(c(),m("tr",{key:"it-"+r},[t("td",null,o(n.item_name),1),t("td",It,o(n.production_capacity)+" "+o(n.unit),1)]))),128))])])]),s.value?(c(),m("div",Lt,[t("img",{src:s.value,alt:"QR",class:"barcode-img",crossorigin:"anonymous"},null,8,Ut)])):h("",!0),e[24]||(e[24]=t("div",{class:"notes centered"},[t("div",{style:{"text-align":"center"}},[t("p",null,"إن احتفاظك بهذه الوثيقة يمكّنك من استخدامها لدى الجهات المرتبطة بالنظام."),t("p",null,"يمكنك حفظ صورة الوثيقة في الهاتف لاستخدامها عند الحاجة."),t("p",{class:"muted"}," لمزيد من المعلومات عن الخدمات الحكومية الإلكترونية يمكن زيارة: "),t("a",{href:"https://ur.gov.iq",target:"_blank",rel:"noopener noreferrer",class:"external-link"}," https://ur.gov.iq ")])],-1))]),e[26]||(e[26]=k('<footer class="doc-footer" data-v-435b7756><div class="footer-left" data-v-435b7756><img src="'+T+'" alt="Logo" class="footer-logo" data-v-435b7756></div><div class="footer-center" data-v-435b7756><div class="small" data-v-435b7756><strong data-v-435b7756>مكتب رئيس الوزراء / المركز الوطني للتحول الرقمي</strong></div><div class="small" data-v-435b7756>بغداد – كرادة مريم</div><div class="small" data-v-435b7756>المركز الوطني للتحول الرقمي @2025</div></div><div class="footer-right en-footer" dir="ltr" data-v-435b7756><div class="small" data-v-435b7756>Prime Minister’s Office</div><div class="small" data-v-435b7756>National Center for Digital Transformation</div><div class="small" data-v-435b7756>Tel: 5599</div></div></footer>',1))],512)])]))}}),Et=C(Nt,[["__scopeId","data-v-435b7756"]]);export{Bt as C,Et as S};