if(new URLSearchParams(location.search).has('dataset'))history.replaceState(null,'',location.pathname);
const state = {section:'queue',view:'all',page:1,selected:null,summary:null,searchTimer:null,caseRequest:0};
const $ = id => document.getElementById(id);
const formatDate = value => value ? new Intl.DateTimeFormat('es-ES',{day:'numeric',month:'short',year:'numeric'}).format(new Date(`${value.slice(0,10)}T12:00:00`)) : 'Sin dato';
const compactDateTime = value => `${value.slice(8,10)}/${value.slice(5,7)} ${value.slice(11,16)}`;
const number = value => value === null || value === undefined ? '—' : new Intl.NumberFormat('es-ES').format(value);

async function api(path, options={}) {
  const response = await fetch(path,{cache:'no-store',...options});
  const data = await response.json();
  if(!response.ok) throw new Error(data.error || `Error ${response.status}`);
  return data;
}
function notice(message,error=false){const el=$('notice');el.textContent=message;el.classList.toggle('error',error);el.hidden=false;}
function clearNotice(){ $('notice').hidden=true; }
function cell(text, strong=false, small=null){const td=document.createElement('td');const main=document.createElement(strong?'strong':'span');main.textContent=text;td.append(main);if(small){const sub=document.createElement('small');sub.textContent=small;td.append(sub)}return td;}
async function loadSummary(){
  state.summary=await api('/api/summary');
  const run=state.summary.latest_run;
  $('cutoff').textContent=run ? `Corte ${formatDate(run.as_of)} · ${run.as_of.slice(11,16)}` : 'Sin datos';
  const select=$('client'), current=select.value;select.replaceChildren(new Option('Todos',''));
  for(const client of state.summary.clients) select.add(new Option(client.name,client.id));
  select.value=current;
}

function renderRows(items){
  const body=$('case-rows');body.replaceChildren();
  for(const item of items){
    const row=document.createElement('tr');row.dataset.id=item.case_id;row.tabIndex=0;
    row.classList.toggle('selected',item.case_id===state.selected);
    const priority=document.createElement('td'),label=document.createElement('span'),dot=document.createElement('i');
    label.className=`priority-label ${item.attention?item.priority.toLowerCase():'cerrado'}`;dot.className='priority-dot';dot.setAttribute('aria-hidden','true');label.append(dot,document.createTextNode(item.attention?item.priority:'Servido'));priority.append(label);
    row.append(priority,cell(item.order_id||'Sin referencia',true,item.line_id?`Línea ${item.line_id}`:item.kind==='unresolved_email'?'Correo sin vínculo':null),
      cell(item.client_name||'Sin identificar'),cell(number(item.pending),true,item.pending===null?'sin dato':'ud.'),cell(item.reason),cell(item.action));
    row.children[3].classList.add('numeric');
    row.addEventListener('click',()=>selectCase(item.case_id));
    row.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();selectCase(item.case_id)}});
    body.append(row);
  }
}

async function loadCases(){
  const request=++state.caseRequest;
  const params=new URLSearchParams({view:state.view,page:String(state.page)});
  if($('client').value)params.set('client',$('client').value);
  if($('priority').value)params.set('priority',$('priority').value);
  if($('search').value.trim())params.set('search',$('search').value.trim());
  const data=await api(`/api/cases?${params}`);
  if(request!==state.caseRequest)return;
  $('empty').hidden=data.total>0;
  const noun=state.view==='records'?'registros':'casos';
  $('range').textContent=data.total?`${(data.page-1)*data.page_size+1}–${Math.min(data.page*data.page_size,data.total)} de ${number(data.total)} ${noun}`:`0 ${noun}`;
  $('page-label').textContent=`Página ${data.page} de ${Math.max(1,Math.ceil(data.total/data.page_size))}`;
  $('prev').disabled=data.page<=1;$('next').disabled=data.page*data.page_size>=data.total;
  if(!data.items.some(item=>item.case_id===state.selected))state.selected=data.items[0]?.case_id||null;
  renderRows(data.items);
  $('detail').hidden=!state.selected;
  if(state.selected)await loadDetail(state.selected);
}

async function loadDetail(id){
  const data=await api(`/api/cases/${encodeURIComponent(id)}`);
  if(id!==state.selected)return;
  $('detail-title').textContent=data.order_id ? `${data.order_id}${data.line_id?' · línea '+data.line_id:''}` : `Correo ${data.emails?.[0]?.message_id||''}`;
  $('detail-item').textContent=[data.cliente,data.sku,data.color,data.talla].filter(Boolean).join(' · ');
  $('detail-state').textContent=data.label;
  $('detail-erp').textContent=formatDate(data.fecha_compromiso);
  $('detail-request').textContent=data.requested_date?formatDate(data.requested_date):'Sin cambio solicitado';
  $('detail-pending').textContent=data.pendientes===null?'Desconocido':`${number(data.pendientes)} de ${number(data.uds_pedidas)} ud.`;
  $('detail-reason').textContent=data.reason+'. '+(data.kind==='line'?'El dato de pedido procede del ERP; los correos son peticiones o consultas, no cambios confirmados.':'El correo queda pendiente de asociación por una persona.');
  $('detail-action').textContent=data.action;
  const issues=$('detail-issues');issues.replaceChildren();
  for(const issue of data.issues||[]){const tag=document.createElement('span');tag.className='issue';tag.textContent=issue;issues.append(tag)}
  if(data.request_conflict){const tag=document.createElement('span');tag.className='issue';tag.textContent='Peticiones activas múltiples';issues.append(tag)}
  const evidence=$('detail-evidence');evidence.replaceChildren();
  if(!data.emails?.length){const p=document.createElement('p');p.textContent='Sin correos relacionados. Motivo calculado con los datos del ERP.';evidence.append(p)}
  for(const mail of [...(data.emails||[])].reverse()){
    const details=document.createElement('details'),head=document.createElement('summary'),bold=document.createElement('b'),body=document.createElement('p');
    bold.textContent=`${mail.received_at.slice(11,16)} · ${mail.message_id}`;
    head.append(bold,document.createTextNode(` · ${mail.subject||mail.intent}`));
    body.textContent=mail.body||'(sin cuerpo)';details.append(head,body);evidence.append(details);
  }
  if(data.suggestions?.length){const p=document.createElement('p');p.textContent=`Posibles líneas para revisar: ${data.suggestions.join(', ')}. Ninguna se ha asociado automáticamente.`;evidence.append(p)}
}

async function selectCase(id){state.selected=id;document.querySelectorAll('#case-rows tr').forEach(row=>row.classList.toggle('selected',row.dataset.id===id));await loadDetail(id);}
async function showSection(section){
  state.section=section;document.querySelectorAll('.rail-pill').forEach(x=>x.classList.toggle('active',x.dataset.section===section));
  $('queue-view').hidden=section==='runs';$('runs-view').hidden=section!=='runs';
  if(section==='runs'){await loadRuns();return}
  $('search').value='';$('client').value='';$('priority').value='';state.page=1;
  if(section==='unresolved'){
    $('section-nav').hidden=true;$('queue-heading').textContent='Correos sin resolver';
    $('queue-description').textContent='Mensajes que requieren identificar el pedido o la línea antes de actuar.';
    state.view='unresolved';await loadCases();return;
  }
  await showView('all',true);
}
async function showView(view,fromSection=false){state.view=view;state.page=1;document.querySelectorAll('.tab').forEach(x=>x.classList.toggle('active',x.dataset.view===view));
  if(view!=='records')$('search').value='';
  if(!fromSection){state.section='queue';document.querySelectorAll('.rail-pill').forEach(x=>x.classList.toggle('active',x.dataset.section==='queue'))}
  $('section-nav').hidden=false;$('queue-heading').textContent=view==='records'?'Todos los registros':'Cola de trabajo';
  $('queue-description').textContent=view==='records'?'Incluye líneas servidas. «Servido» es un estado y no aparece al filtrar por prioridad.':'Casos activos de todas las prioridades. Usa el filtro para ver solo «Alta».';
  await loadCases();}

async function loadRuns(){
  const runs=await api('/api/runs');const body=$('run-rows');body.replaceChildren();
  for(const run of runs){const tr=document.createElement('tr');
    const executed=cell(compactDateTime(run.created_at)),cutoff=cell(compactDateTime(run.as_of));
    executed.title=run.created_at;cutoff.title=run.as_of;
    tr.append(executed,cutoff,cell(number(run.added_messages)),cell(number(run.repeated_messages)),cell(number(run.conflicting_messages)),cell(number(run.total_cases)),cell(`${number(run.elapsed_ms)} ms`),cell(run.output_sha256.slice(0,12)));
    body.append(tr);
  }
  const result=$('run-comparison');result.replaceChildren();
  if(runs.length>=2){const latest=runs[0],previous=runs[1];result.textContent=latest.output_sha256===previous.output_sha256
    ? `Resultado idéntico a la ejecución anterior · ${latest.added_messages} mensajes nuevos · ${latest.repeated_messages} reentregas ignoradas.`
    : latest.added_messages===0
      ? `El resultado cambió sin correos nuevos. ${latest.orders_sha256!==previous.orders_sha256?'Cambió la exportación de pedidos.':'Revisa cambios en las reglas del motor.'} Verifica antes de operar.`
      : `Resultado actualizado · ${latest.added_messages} mensajes nuevos · ${latest.repeated_messages} reentregas ignoradas. Abre la cola para revisar los casos.`}
}

async function incorporateUpdate(){
  const button=$('update-button');button.disabled=true;button.textContent='Actualizando…';clearNotice();
  try{const run=await api('/api/update',{method:'POST'});await loadSummary();await loadRuns();
    notice(`Lote incorporado: ${run.added_messages} mensajes nuevos, ${run.repeated_messages} reentregas ignoradas, ${run.conflicting_messages} conflictos. Resultado ${run.output_sha256.slice(0,12)}.`);
  }catch(error){notice(error.message,true)}finally{button.disabled=false;button.textContent='Incorporar lote de actualización'}
}

function wire(){
  document.querySelectorAll('.rail-pill').forEach(x=>x.addEventListener('click',()=>showSection(x.dataset.section).catch(e=>notice(e.message,true))));
  document.querySelectorAll('.tab').forEach(x=>x.addEventListener('click',()=>showView(x.dataset.view).catch(e=>notice(e.message,true))));
  for(const id of ['client','priority'])$(id).addEventListener('change',()=>{state.page=1;loadCases().catch(e=>notice(e.message,true))});
  $('search').addEventListener('input',()=>{clearTimeout(state.searchTimer);
    if($('search').value.trim() && state.view!=='records'){showView('records').catch(e=>notice(e.message,true));return}
    state.searchTimer=setTimeout(()=>{state.page=1;loadCases().catch(e=>notice(e.message,true))},250)});
  $('prev').addEventListener('click',()=>{state.page--;loadCases().catch(e=>notice(e.message,true))});
  $('next').addEventListener('click',()=>{state.page++;loadCases().catch(e=>notice(e.message,true))});
  $('update-button').addEventListener('click',incorporateUpdate);
}

wire();loadSummary().then(loadCases).catch(error=>notice(`No se pudieron cargar los datos: ${error.message}`,true));
