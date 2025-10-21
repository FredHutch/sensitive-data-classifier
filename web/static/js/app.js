(function(){
  const classifyForm=document.getElementById('classify-form');
  const fileInput=document.getElementById('file-input');
  const dropzone=document.getElementById('dropzone');
  const results=document.getElementById('results');
  const resultsList=document.getElementById('results-list');
  if(dropzone&&fileInput){['dragenter','dragover'].forEach(evt=>dropzone.addEventListener(evt,e=>{e.preventDefault();e.stopPropagation();dropzone.classList.add('drag');}));['dragleave','drop'].forEach(evt=>dropzone.addEventListener(evt,e=>{e.preventDefault();e.stopPropagation();dropzone.classList.remove('drag');}));dropzone.addEventListener('drop',e=>{const dt=e.dataTransfer;if(dt&&dt.files) fileInput.files=dt.files;});}
  if(classifyForm){classifyForm.addEventListener('submit',async(e)=>{e.preventDefault();const fd=new FormData(classifyForm);const resp=await fetch('/api/classify',{method:'POST',body:fd});const data=await resp.json();if(data.status!=='success'){alert(data.message||'Classification failed');return;}results.style.display='block';resultsList.innerHTML='';data.results.forEach(r=>{const div=document.createElement('div');div.className='item';const riskClass=r.risk_level==='HIGH'?'red':(r.risk_level==='MEDIUM'?'yellow':'green');div.innerHTML=`<div><strong>${r.filename}</strong></div><div>Contains PHI: <span class=\"badge ${r.contains_phi?'red':'green'}\">${r.contains_phi}</span></div><div>Risk: <span class=\"badge ${riskClass}\">${r.risk_level}</span> Confidence: ${(r.confidence*100).toFixed(1)}%</div><div>Total identifiers: ${r.total_identifiers||0}</div>`;resultsList.appendChild(div);});});}
  const genForm=document.getElementById('generate-form');
  const genSummary=document.getElementById('gen-summary');
  const genResults=document.getElementById('gen-results');
  if(genForm){genForm.addEventListener('submit',async(e)=>{e.preventDefault();const count=document.getElementById('count').value;const formatsSel=document.getElementById('formats');const formats=Array.from(formatsSel.selectedOptions).map(o=>o.value);const resp=await fetch('/api/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({count:parseInt(count,10),formats})});const data=await resp.json();if(data.status!=='success'){alert(data.message||'Generation failed');return;}genResults.style.display='block';genSummary.textContent=JSON.stringify(data,null,2);});}
})();
