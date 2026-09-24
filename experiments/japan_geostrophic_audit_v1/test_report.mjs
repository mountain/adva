import { chromium } from '/home/ubuntu/climatetensor-xue/node_modules/playwright/index.mjs';
const url=process.argv[2];
const browser=await chromium.launch({executablePath:'/home/ubuntu/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome',headless:true,args:['--no-sandbox']});
const rows=[];
try {
 for(const viewport of [{width:1440,height:1000},{width:390,height:844}]) {
  const page=await browser.newPage({viewport});const errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto(url,{waitUntil:'networkidle'});
  const result=await page.evaluate(async()=>{
   const imgs=[...document.images].map(x=>({loaded:x.complete&&x.naturalWidth>0,width:x.naturalWidth}));
   const links=[...new Set([...document.querySelectorAll('a[href]')].map(x=>x.getAttribute('href')).filter(x=>!x.startsWith('http')))];
   const responses=[];for(const l of links){const r=await fetch(l,{method:'HEAD'});responses.push({path:l,status:r.status});}
   return {title:document.title,images:imgs,links:responses,overflow:document.documentElement.scrollWidth>innerWidth+1,hasMismatch:document.body.innerText.includes('冻结版本没有 2026 年 12 月预报'),hasFloquet:document.body.innerText.includes('周期系数的齐次线性近似')};
  });
  if(errors.length||result.overflow||!result.hasMismatch||!result.hasFloquet||result.images.some(x=>!x.loaded)||result.links.some(x=>x.status!==200))throw Error(JSON.stringify({viewport,errors,result}));
  rows.push({viewport,errors,...result});await page.close();
 }
 console.log(JSON.stringify({status:'Pass',url,rows},null,2));
} finally {await browser.close();}
