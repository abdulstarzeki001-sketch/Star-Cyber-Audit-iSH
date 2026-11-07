import{_ as $,a as L}from"./iraqEagle-BF406BBV.js";import{d as Q,x as S,J as T,b as d,c as w,w as k,k as v,g as f,j as t,l as _,P as q,t as n,i as B,n as H,z as F}from"./index-gleMzSil.js";import{s as C,u as M}from"./useExitGate-BvHNutwH.js";import U from"./QRCheckpoints-Brs0uL0-.js";import{Q as V}from"./browser-3Qg8aFGH.js";import"./qrStore-B8bgApfd.js";import"./useHealthCertificate-DVL2cDcP.js";const I={class:"qr-document-root"},P={class:"doc-viewport"},J={class:"header-clean"},O={class:"header-left"},G={class:"doc-meta"},K={class:"meta-line"},W={class:"meta-value"},X={class:"meta-line"},Y={class:"meta-value"},Z={class:"meta-line"},tt={class:"meta-value"},et={class:"content"},ot={class:"download-toolbar"},at={class:"info-section",dir:"rtl"},nt={class:"info-table"},lt={class:"qr-wrap large-qr"},it=["src"],rt={key:0,class:"fixed inset-0 z-50 flex items-center justify-center"},st={class:"relative max-h-[85vh] w-[95%] max-w-4xl overflow-auto rounded-lg bg-white p-4 shadow-lg dark:bg-gray-800"},dt={class:"mb-3 flex items-center justify-between"},mt=Q({__name:"AchievementDocument",props:{docNumber:{}},setup(z){const m=z,R=S(),g=T(),a=d({}),r=d(""),b=d(null),s=d(!1),D=w(()=>a.value?.read_doc||[]);async function p(l){const e=typeof l=="string"?JSON.parse(l):l,o=e?.data||e||{};if(a.value=o,o.qr_code||o.doc_id||o.doc_number){const i=o.qr_code||o.doc_id||o.doc_number;try{r.value=await V.toDataURL(i,{width:500,margin:1})}catch(x){console.error("Failed to generate QR code locally",x),r.value=`https://quickchart.io/qr?text=${encodeURIComponent(i)}&size=500`}}else r.value=""}async function h(l){if(l)try{const o=M(),{resp:i}=await o.fetchAchievementDocDetail(l);if(i){await p(i);return}}catch(o){console.error("[AchievementDocument] Failed to fetch doc detail from query",o)}const e=C.value||history.state?.record||g.query.data;e&&await p(e)}const y=w(()=>m.docNumber||g.query.doc_number||"");k(y,async l=>{l?await h(l):await h()},{immediate:!0}),k(()=>C.value,async l=>{l&&!y.value&&await p(l)},{immediate:!0});function A(){R.back()}function N(){s.value=!0}function j(){const l=b.value;if(!l){window.print();return}const e=l.outerHTML,o=window.open("","_blank","width=900,height=1000");if(!o)return;const i=[];i.push('<meta charset="utf-8" />'),i.push("<title>طباعة الوثيقة</title>"),Array.from(document.querySelectorAll("style")).forEach(u=>i.push(u.outerHTML)),Array.from(document.querySelectorAll('link[rel="stylesheet"]')).forEach(u=>{const c=u.getAttribute("href");if(!c)return;const E=c.includes("?")?"&":"?";i.push(`<link rel="stylesheet" href="${c}${E}print_copy=${Date.now()}" />`)}),i.push(`
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
        padding-bottom: 2mm !important;
      }

      /* Compact Header */
      .header-clean { padding: 0 !important; gap: 4px !important; }
      .center-logo { width: 80px !important; height: 80px !important; }
      .office-lines { font-size: 0.75rem !important; line-height: 1.2 !important; }
      .doc-meta { gap: 2px !important; }
      .meta-line { gap: 4px !important; }
      .meta-label, .meta-value { font-size: 0.8rem !important; min-width: auto !important; }

      .divider { margin: 4px 0 !important; }
      .doc-title { margin: 4px 0 !important; font-size: 1.2rem !important; }

      /* Compact Body */
      .subject-row { margin: 4px 0 !important; font-size: 0.9rem !important; }
      .subject-field { padding: 2px 6px !important; min-height: auto !important; }

      .info-table th { font-size: 0.8rem !important; padding: 2px 4px !important; }
      .info-table td { font-size: 0.8rem !important; padding: 1px 4px !important; min-height: auto !important; }

      /* Compact QR & Notes */
      .qr-wrap { margin-top: 3px !important; margin-bottom: 4px !important; }
      .large-qr .barcode-img { width: 30mm !important; padding: 2px !important; }
      .notes { margin-top: 3px !important; gap: 2px !important; }
      .notes p { margin: 1px 0 !important; font-size: 0.75rem !important; }

      /* Compact Footer */
      .doc-footer {
        padding: 4px !important;
        margin-top: auto !important;
        page-break-inside: avoid;
        gap: 4px !important;
      }
      .footer-logo { width: 50px !important; height: 40px !important; }
      .doc-footer .small { font-size: 0.65rem !important; line-height: 1.2 !important; }

      /* Hide UI elements */
      button,
      .download-toolbar,
      .preview-overlay,
      .preview-card,
      .action-buttons,
      .doc-actions,
      .print-toolbar {
        display: none !important;
      }
      * {
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
      }
    </style>
  `),o.document.open(),o.document.write(`
    <!doctype html>
    <html dir="rtl" lang="ar">
      <head>
        ${i.join(`
`)}
      </head>
      <body>
        ${e}
      </body>
    </html>
  `),o.document.close(),o.onload=()=>{o.focus(),o.print(),setTimeout(()=>o.close(),500)}}return(l,e)=>(f(),v("div",{class:H(["achievement-wrapper",{"in-modal":!!m.docNumber}])},[t("div",I,[t("div",P,[t("div",{class:"a4-page container",dir:"rtl",ref_key:"docRef",ref:b},[t("header",J,[e[5]||(e[5]=q('<div class="header-right" data-v-40b2f318><div class="office-lines small" data-v-40b2f318><div style="text-align:right;" data-v-40b2f318>جمهورية العراق</div><div style="text-align:right;" data-v-40b2f318>وزارة المالية</div><div style="text-align:right;" data-v-40b2f318>الهيئــة العامــة للكمـــارك</div></div></div><div class="header-center logo-wrap" data-v-40b2f318><img src="'+$+'" alt="Logo" class="center-logo" data-v-40b2f318></div>',2)),t("div",O,[t("div",G,[t("div",K,[e[2]||(e[2]=t("span",{class:"meta-label"},"رقم الوثيقة",-1)),t("span",W,n(a.value.doc_id||""),1)]),t("div",X,[e[3]||(e[3]=t("span",{class:"meta-label"},"تاريخ الادخال",-1)),t("span",Y,n(a.value.date_str||""),1)]),t("div",Z,[e[4]||(e[4]=t("span",{class:"meta-label"},"التوقيت",-1)),t("span",tt,n(a.value.time_str||""),1)])])])]),e[24]||(e[24]=t("hr",{class:"divider"},null,-1)),t("div",et,[e[22]||(e[22]=t("h2",{class:"doc-title"},"استمارة الناقل",-1)),t("div",ot,[t("button",{onClick:j,class:"btn btn-soft btn-primary dark:bg-gray-600 dark:text-gray-100"}," طباعة "),m.docNumber?_("",!0):(f(),v("button",{key:0,onClick:A,class:"btn btn-soft btn-error dark:bg-gray-600 dark:text-gray-100"}," رجـوع ")),t("button",{onClick:N,class:"btn btn-soft btn-primary dark:bg-gray-600 dark:text-gray-100"}," عرض السيطرات ")]),t("div",at,[t("table",nt,[e[20]||(e[20]=t("colgroup",null,[t("col",{style:{width:"35%"}}),t("col",{style:{width:"65%"}})],-1)),e[21]||(e[21]=t("thead",null,[t("tr",null,[t("th",{colspan:"2",class:"text-white"},"معلومات الوثيقة")])],-1)),t("tbody",null,[t("tr",null,[e[6]||(e[6]=t("td",null,"اسم المكتب الكمركي",-1)),t("td",null,n(a.value.customs_office_name||"لا يوجد"),1)]),t("tr",null,[e[7]||(e[7]=t("td",null,"اسم السائق",-1)),t("td",null,n(a.value.driver_name||"لا يوجد"),1)]),t("tr",null,[e[8]||(e[8]=t("td",null,"رقم العجلة",-1)),t("td",null,n(a.value.vehicle_number||"لا يوجد"),1)]),t("tr",null,[e[9]||(e[9]=t("td",null,"رقم العربة",-1)),t("td",null,n(a.value.vehicle_number2||"لا يوجد"),1)]),t("tr",null,[e[10]||(e[10]=t("td",null,"محافظة تسجيل العجلة",-1)),t("td",null,n(a.value.vehicle_registration_governorate||"لا يوجد"),1)]),t("tr",null,[e[11]||(e[11]=t("td",null,"الوزن/ الكمية",-1)),t("td",null,n(a.value.weight_quantity||"لا يوجد"),1)]),t("tr",null,[e[12]||(e[12]=t("td",null,"الوجهة النهائية/ المحافظة",-1)),t("td",null,n(a.value.final_destination_governorate||"لا يوجد"),1)]),t("tr",null,[e[13]||(e[13]=t("td",null,"اسم المخلص او صاحب العلاقة",-1)),t("td",null,n(a.value.clearance_agent_name||"لا يوجد"),1)]),t("tr",null,[e[14]||(e[14]=t("td",null,"اسم شركة التخليص",-1)),t("td",null,n(a.value.clearance_company_name||"لا يوجد"),1)]),t("tr",null,[e[15]||(e[15]=t("td",null,"رقم الوصل",-1)),t("td",null,n(a.value.receipt_number37||"لا يوجد"),1)]),t("tr",null,[e[16]||(e[16]=t("td",null,"تاريخ الوصل",-1)),t("td",null,n(a.value.receipt_date37||"لا يوجد"),1)]),t("tr",null,[e[17]||(e[17]=t("td",null,"مبلغ الوصل",-1)),t("td",null,n(a.value.total_amount||"لا يوجد"),1)]),t("tr",null,[e[18]||(e[18]=t("td",null,"نوع وتفاصيل الحمولة",-1)),t("td",null,n(a.value.load_type_and_details||"لا يوجد"),1)]),t("tr",null,[e[19]||(e[19]=t("td",null,"ملاحظات الكشف",-1)),t("td",null,n(a.value.decision_reason||"لا يوجد"),1)])])])]),t("div",lt,[t("img",{src:r.value,alt:"QR",class:"barcode-img",crossorigin:"anonymous"},null,8,it)]),e[23]||(e[23]=t("div",{class:"notes centered"},[t("div",{style:{"text-align":"center"}},[t("p",null," ان حفاظك على هذه الوثيقة دون ضرر يمكنك من استخدامها في كافة نقاط التفتيش والسيطرات "),t("p",null,"يمكنك حفظ صورة الوثيقة في هاتفك لاستخدامها عند الضرورة"),t("p",{class:"muted"}," لمزيد من المعلومات عن الخدمات الحكومية الالكترونية، بالأمكان زيارة الرابط التالي "),t("a",{href:"https://ur.gov.iq",target:"_blank",rel:"noopener noreferrer",class:"external-link"},"https://ur.gov.iq")])],-1))]),e[25]||(e[25]=q('<footer class="doc-footer" data-v-40b2f318><div class="footer-left" data-v-40b2f318><img src="'+L+'" alt="Logo" class="footer-logo" data-v-40b2f318></div><div class="footer-center" data-v-40b2f318><div class="small" data-v-40b2f318><strong data-v-40b2f318>مكتب رئيس الوزراء/المركز الوطني للتحول الرقمي</strong></div><div class="small" data-v-40b2f318>بغداد-كرادة مريم</div><div class="small" data-v-40b2f318>المركز الوطني للتحول الرقمي @2025</div></div><div class="footer-right en-footer" dir="ltr" data-v-40b2f318><div class="small" data-v-40b2f318>Prime Minister’s Office</div><div class="small" data-v-40b2f318>National Center for Digital Transformation</div><div class="small" data-v-40b2f318>Tel: 5599</div></div></footer>',1))],512)])]),s.value?(f(),v("div",rt,[t("div",{class:"absolute inset-0 bg-black/40",onClick:e[0]||(e[0]=o=>s.value=!1)}),t("div",st,[t("div",dt,[e[26]||(e[26]=t("h3",{class:"text-lg font-semibold"},"سيطرات القراءة",-1)),t("button",{onClick:e[1]||(e[1]=o=>s.value=!1),class:"rounded bg-gray-100 px-2 py-1 text-sm hover:bg-gray-200"}," إغلاق ")]),B(U,{items:D.value},null,8,["items"])])])):_("",!0)],2))}}),yt=F(mt,[["__scopeId","data-v-40b2f318"]]);export{yt as default};
