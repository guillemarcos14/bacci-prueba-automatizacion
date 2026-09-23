if(new URLSearchParams(location.search).has('dataset'))history.replaceState(null,'',location.pathname);
const state = {section:'queue',view:'all',page:1,selected:null,summary:null,searchTimer:null,caseRequest:0,
  runSelection:null,impactPage:1,impactRequest:0};
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
  $('review').options[1].textContent=`Revisión humana (${number(state.summary.review_cases)})`;
}

function renderRows(items){
  const body=$('case-rows');body.replaceChildren();
  for(const item of items){
    const row=document.createElement('tr');row.dataset.id=item.case_id;row.tabIndex=0;
    row.classList.toggle('selected',item.case_id===state.selected);
    row.setAttribute('aria-current',item.case_id===state.selected?'true':'false');
    const priority=document.createElement('td'),label=document.createElement('span'),dot=document.createElement('i');
    label.className=`priority-label ${item.attention?item.priority.toLowerCase():'cerrado'}`;dot.className='priority-dot';dot.setAttribute('aria-hidden','true');label.append(dot,document.createTextNode(item.attention?item.priority:'Servido'));priority.append(label);
    row.append(priority,cell(item.order_id||'Sin referencia',true,item.line_id?`Línea ${item.line_id}`:item.kind==='unresolved_email'?'Correo sin vínculo':null),
      cell(item.client_name||'Sin identificar'),cell(number(item.pending),true,item.pending===null?'sin dato':'ud.'),cell(item.reason),cell(item.action));
    row.children[3].classList.add('numeric');
    row.children[4].title=item.reason;row.children[5].title=item.action;
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
  if($('review').value)params.set('review',$('review').value);
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
  const requestedDates=data.requested_dates||[];
  $('detail-request-label').textContent=requestedDates.length>1?'Fechas solicitadas':'Fecha solicitada';
  $('detail-request').textContent=requestedDates.length>1?`${requestedDates.map(formatDate).join(' · ')} · por aclarar`:
    data.requested_date?formatDate(data.requested_date):
    (data.request_count||data.emails?.some(mail=>mail.intent==='cambio_fecha'))?'Solicitud sin fecha identificada':'No se pidió otra fecha';
  $('detail-ordered').textContent=data.uds_pedidas===null?'Desconocidas':`${number(data.uds_pedidas)} ud.`;
  $('detail-shipped').textContent=data.uds_enviadas===null?'Desconocidas':`${number(data.uds_enviadas)} ud.`;
  $('detail-pending').textContent=data.pendientes===null?'Desconocido':`${number(data.pendientes)} ud.`;
  $('detail-reason').textContent=data.reason;
  $('detail-action').textContent=data.action;
  const issues=$('detail-issues');issues.replaceChildren();
  for(const issue of data.issues||[]){const tag=document.createElement('span');tag.className='issue';tag.textContent=issue;issues.append(tag)}
  const source=$('detail-source');source.replaceChildren();
  if(data.source_rows?.length){
    const details=document.createElement('details'),head=document.createElement('summary');
    head.textContent=`Filas originales del ERP (${data.source_rows.length})`;
    details.append(head);
    const fields=[['pedido_id','Pedido'],['linea_id','Línea'],['cliente_id','Cliente ID'],['sku','SKU'],
      ['color','Color'],['talla','Talla'],['uds_pedidas','Pedidas'],['uds_enviadas','Enviadas acumuladas'],
      ['precio_unitario_eur','Precio unitario EUR'],['fecha_compromiso','Compromiso ERP']];
    for(const row of data.source_rows){
      const item=document.createElement('div'),location=document.createElement('strong'),values=document.createElement('dl');
      item.className='source-row';
      location.textContent=`${row.__source_file||'Archivo de pedidos'} · ${row.__source_sheet||'Pedidos'} · fila ${row.__source_row??'sin dato'}`;
      for(const [key,label] of fields){
        const pair=document.createElement('div'),term=document.createElement('dt'),value=document.createElement('dd');
        term.textContent=label;
        const raw=row[key];
        value.textContent=raw===null||raw===undefined||raw===''?'Sin dato':
          key==='fecha_compromiso'?formatDate(raw):String(raw);
        pair.append(term,value);values.append(pair);
      }
      item.append(location,values);details.append(item);
    }
    source.append(details);
  }
  const evidence=$('detail-evidence');evidence.replaceChildren();
  if(!data.emails?.length){const p=document.createElement('p');p.textContent='Sin correos relacionados. Motivo calculado con los datos del ERP.';evidence.append(p)}
  for(const mail of [...(data.emails||[])].reverse()){
    const details=document.createElement('details'),head=document.createElement('summary'),bold=document.createElement('b'),meta=document.createElement('p'),body=document.createElement('p');
    bold.textContent=`${compactDateTime(mail.received_at)} · ${mail.message_id}`;
    head.append(bold,document.createTextNode(` · ${mail.subject||mail.intent}`));
    meta.className='evidence-meta';
    meta.textContent=[mail.source_file?`${mail.source_file} · ${mail.source_sheet||'Correos'} · fila ${mail.source_row??'sin dato'}`:null,
      `De ${mail.from||'sin dato'}`,`Para ${mail.to||'sin dato'}`,
      mail.match?`Vínculo: ${mail.match}`:null,
      mail.requested_date?`Fecha solicitada: ${formatDate(mail.requested_date)}`:null,
      mail.supersedes?`Rectifica ${mail.supersedes}`:null].filter(Boolean).join(' · ');
    body.textContent=mail.body||'(sin cuerpo)';details.append(head,meta,body);evidence.append(details);
  }
  if(data.suggestions?.length){const p=document.createElement('p');p.textContent=`Posibles líneas para revisar: ${data.suggestions.join(', ')}. Ninguna se ha asociado automáticamente.`;evidence.append(p)}
}

async function selectCase(id){state.selected=id;document.querySelectorAll('#case-rows tr').forEach(row=>{
  const active=row.dataset.id===id;row.classList.toggle('selected',active);row.setAttribute('aria-current',active?'true':'false')});await loadDetail(id);}
async function showSection(section){
  state.section=section;document.querySelectorAll('.rail-pill').forEach(x=>{const active=x.dataset.section===section;
    x.classList.toggle('active',active);x.setAttribute('aria-pressed',String(active))});
  $('queue-view').hidden=section==='runs';$('runs-view').hidden=section!=='runs';
  if(section==='runs'){await loadRuns();return}
  $('search').value='';$('client').value='';$('priority').value='';$('review').value='';state.page=1;
  if(section==='unresolved'){
    $('section-nav').hidden=true;$('queue-heading').textContent='Correos sin resolver';
    $('queue-description').textContent='Mensajes que requieren identificar el pedido o la línea antes de actuar.';
    state.view='unresolved';await loadCases();return;
  }
  await showView('all',true);
}
async function showView(view,fromSection=false){state.view=view;state.page=1;document.querySelectorAll('.tab').forEach(x=>{
  const active=x.dataset.view===view;x.classList.toggle('active',active);x.setAttribute('aria-pressed',String(active))});
  if(view!=='records')$('search').value='';
  if(!fromSection){state.section='queue';document.querySelectorAll('.rail-pill').forEach(x=>{const active=x.dataset.section==='queue';
    x.classList.toggle('active',active);x.setAttribute('aria-pressed',String(active))})}
  $('section-nav').hidden=false;$('queue-heading').textContent=view==='records'?'Todos los registros':'Cola de trabajo';
  $('queue-description').textContent=view==='records'?'Incluye líneas servidas. «Servido» es un estado y no aparece al filtrar por prioridad.':'Casos activos de todas las prioridades. Usa el filtro para ver solo «Alta».';
  await loadCases();}

const impactLabels={cliente:'Cliente',sku:'SKU',color:'Color',talla:'Talla',uds_pedidas:'Unidades pedidas',
  uds_enviadas:'Unidades enviadas',pendientes:'Por servir',fecha_compromiso:'Compromiso ERP',
  requested_date:'Fecha solicitada',requested_dates:'Fechas solicitadas',priority:'Prioridad',label:'Estado del caso',reason:'Motivo',
  action:'Acción propuesta',issues:'Anomalías',attention:'Trabajo activo',unresolved:'Sin correspondencia',
  email_ids:'Correos vinculados'};
function impactValue(field,value){
  if(value===null||value===undefined)return 'Sin dato';
  if(field==='email_ids')return `${value.length} (${value.join(', ')||'ninguno'})`;
  if(field==='requested_dates')return value.map(formatDate).join(' · ')||'Ninguna';
  if(field==='issues')return value.join(' · ')||'Ninguna';
  if(field==='attention'||field==='unresolved')return value?'Sí':'No';
  if(field==='fecha_compromiso'||field==='requested_date')return formatDate(value);
  return typeof value==='number'?number(value):String(value);
}
async function openChangedCase(id){
  await showSection('queue');
  $('search').value=id;
  await showView('records');
  if(state.selected===id)$('detail').scrollIntoView({behavior:'smooth',block:'start'});
  else notice('El caso ya no figura en el estado actual; conserva su historial en Control de cargas.',true);
}
function renderImpactItem(item){
  const card=document.createElement('article'),head=document.createElement('div'),title=document.createElement('h4'),tag=document.createElement('span');
  const current=item.after||item.before;
  card.className='impact-card';head.className='impact-card-head';tag.className='impact-tag';
  title.textContent=current.order_id?`${current.order_id}${current.line_id?' · línea '+current.line_id:''}`:item.case_id;
  tag.textContent=!item.before?'Caso nuevo':!item.after?'Caso retirado':'Caso actualizado';
  head.append(title,tag);card.append(head);
  if(item.changed_fields.includes('case')){
    const p=document.createElement('p');p.className='impact-note';
    p.textContent=item.after?`Nuevo caso · ${item.after.reason||'sin motivo'} · ${item.after.priority||'sin prioridad'}`:
      'El caso dejó de figurar en el estado calculado.';
    card.append(p);
  }else{
    const list=document.createElement('div');list.className='impact-diffs';
    const singleDateChange=item.changed_fields.includes('requested_date')&&
      [item.before?.requested_dates,item.after?.requested_dates].every(dates=>!dates||dates.length<=1);
    for(const field of item.changed_fields){
      if(field==='requested_dates'&&singleDateChange)continue;
      const row=document.createElement('div'),label=document.createElement('span'),before=document.createElement('span'),arrow=document.createElement('span'),after=document.createElement('strong');
      row.className='impact-diff';label.textContent=impactLabels[field]||field;
      before.textContent=impactValue(field,item.before[field]);arrow.textContent='→';after.textContent=impactValue(field,item.after[field]);
      row.append(label,before,arrow,after);list.append(row);
    }
    card.append(list);
  }
  if(item.after){const button=document.createElement('button');button.type='button';button.className='impact-open';
    button.textContent='Abrir caso actual';button.addEventListener('click',()=>openChangedCase(item.case_id).catch(e=>notice(e.message,true)));card.append(button)}
  return card;
}
async function loadRunChanges(runId,page=1){
  const request=++state.impactRequest;state.runSelection=runId;state.impactPage=page;
  const data=await api(`/api/runs/${runId}/changes?page=${page}`);
  if(request!==state.impactRequest)return;
  document.querySelectorAll('.run-change-button').forEach(button=>{const active=Number(button.dataset.runId)===runId;
    button.classList.toggle('active',active);button.setAttribute('aria-pressed',String(active))});
  const panel=$('run-impact'),items=$('impact-items');panel.hidden=false;items.replaceChildren();
  $('impact-context').textContent=data.previous_as_of
    ? `Corte ${compactDateTime(data.previous_as_of)} → ${compactDateTime(data.as_of)} · comparación de datos operativos de cada caso.`
    : `Corte ${compactDateTime(data.as_of)} · punto de partida de la prueba.`;
  $('impact-count').textContent=data.available?`${number(data.total)} ${data.total===1?'caso':'casos'}`:'Sin comparación';
  if(!data.available){const p=document.createElement('p');p.className='impact-empty';
    p.textContent=data.previous_as_of?'Esta carga se guardó antes de activar el historial de cambios.':'La carga inicial establece el punto de partida; no hay un corte anterior.';items.append(p)}
  else if(!data.total){const p=document.createElement('p');p.className='impact-empty';
    p.textContent='Ningún caso cambió en esta carga. Repetir el lote no creó trabajo nuevo ni alteró los casos.';items.append(p)}
  else for(const item of data.items)items.append(renderImpactItem(item));
  const start=(page-1)*data.page_size+1,end=Math.min(page*data.page_size,data.total||0);
  $('impact-page').textContent=data.total?`${start}–${end} de ${number(data.total)}`:'';
  $('impact-prev').disabled=page<=1;$('impact-next').disabled=page*data.page_size>=(data.total||0);
  $('impact-prev').hidden=$('impact-next').hidden=!data.available||data.total<=data.page_size;
}
async function loadRuns(){
  const runs=await api('/api/runs');const body=$('run-rows');body.replaceChildren();
  for(const run of runs){const tr=document.createElement('tr');
    const executed=cell(compactDateTime(run.created_at)),cutoff=cell(compactDateTime(run.as_of));
    executed.title=run.created_at;cutoff.title=run.as_of;
    const changed=document.createElement('td');
    if(run.changed_cases===null){changed.textContent='—'}
    else{const button=document.createElement('button');button.type='button';button.className='run-change-button';
      button.dataset.runId=String(run.run_id);button.textContent=`${number(run.changed_cases)} · Ver`;
      button.setAttribute('aria-label',`Ver cambios de la ejecución ${run.run_id}: ${number(run.changed_cases)} casos afectados`);
      button.setAttribute('aria-pressed','false');
      button.addEventListener('click',()=>loadRunChanges(run.run_id).catch(e=>notice(e.message,true)));changed.append(button)}
    tr.append(executed,cutoff,cell(number(run.added_messages)),cell(number(run.repeated_messages)),cell(number(run.conflicting_messages)),cell(number(run.total_cases)),changed,cell(`${number(run.elapsed_ms)} ms`),cell(run.output_sha256.slice(0,12)));
    body.append(tr);
  }
  const result=$('run-comparison');result.replaceChildren();
  if(runs.length>=2){const latest=runs[0],previous=runs[1];result.textContent=latest.output_sha256===previous.output_sha256
    ? `Resultado idéntico a la ejecución anterior · ${latest.added_messages} mensajes nuevos · ${latest.repeated_messages} reentregas ignoradas.`
    : latest.added_messages===0
      ? `El resultado cambió sin correos nuevos. ${latest.orders_sha256!==previous.orders_sha256?'Cambió la exportación de pedidos.':'Revisa cambios en las reglas del motor.'} Verifica antes de operar.`
      : `Resultado actualizado · ${latest.added_messages} mensajes nuevos · ${latest.repeated_messages} reentregas ignoradas. Revisa los casos afectados debajo.`}
  if(runs.length){const selected=runs.find(run=>run.run_id===state.runSelection)||runs[0];await loadRunChanges(selected.run_id,state.impactPage)}
  else $('run-impact').hidden=true;
}

async function incorporateUpdate(){
  const button=$('update-button');button.disabled=true;button.textContent='Actualizando…';clearNotice();
  try{const run=await api('/api/update',{method:'POST'});state.runSelection=run.run_id;state.impactPage=1;await loadSummary();await loadRuns();
    notice(`Lote incorporado: ${run.added_messages} mensajes nuevos, ${run.repeated_messages} reentregas ignoradas, ${run.conflicting_messages} conflictos, ${run.changed_cases} casos afectados. Resultado ${run.output_sha256.slice(0,12)}.`);
  }catch(error){notice(error.message,true)}finally{button.disabled=false;button.textContent='Incorporar lote de actualización'}
}

function wire(){
  document.querySelectorAll('.rail-pill').forEach(x=>x.addEventListener('click',()=>showSection(x.dataset.section).catch(e=>notice(e.message,true))));
  document.querySelectorAll('.tab').forEach(x=>x.addEventListener('click',()=>showView(x.dataset.view).catch(e=>notice(e.message,true))));
  for(const id of ['client','priority','review'])$(id).addEventListener('change',()=>{state.page=1;loadCases().catch(e=>notice(e.message,true))});
  $('search').addEventListener('input',()=>{clearTimeout(state.searchTimer);
    if($('search').value.trim() && state.view!=='records'){showView('records').catch(e=>notice(e.message,true));return}
    state.searchTimer=setTimeout(()=>{state.page=1;loadCases().catch(e=>notice(e.message,true))},250)});
  $('prev').addEventListener('click',()=>{state.page--;loadCases().catch(e=>notice(e.message,true))});
  $('next').addEventListener('click',()=>{state.page++;loadCases().catch(e=>notice(e.message,true))});
  $('impact-prev').addEventListener('click',()=>loadRunChanges(state.runSelection,state.impactPage-1).catch(e=>notice(e.message,true)));
  $('impact-next').addEventListener('click',()=>loadRunChanges(state.runSelection,state.impactPage+1).catch(e=>notice(e.message,true)));
  $('update-button').addEventListener('click',incorporateUpdate);
}

wire();loadSummary().then(loadCases).catch(error=>notice(`No se pudieron cargar los datos: ${error.message}`,true));
