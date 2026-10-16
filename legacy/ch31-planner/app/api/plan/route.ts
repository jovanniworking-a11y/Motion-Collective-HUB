import { env } from 'cloudflare:workers';
import { items,tasks } from '../../../lib/plan';
function validValue(id:string,v:Record<string,unknown>){
 const num=(key:string,min:number,max:number)=>typeof v[key]==='number'&&Number.isFinite(v[key])&&Number(v[key])>=min&&Number(v[key])<=max;
 const str=(key:string,max=5000)=>v[key]===undefined||typeof v[key]==='string'&&String(v[key]).length<=max;
 if(id.startsWith('item:'))return items.some(i=>id==='item:'+i.id)&&num('qty',0,10000)&&Number.isInteger(v.qty)&&num('price',0,100000)&&['Buy','Check first','Owned','Borrow pending','Borrow confirmed','Skip'].includes(String(v.status))&&str('owner',100)&&str('note')&&(v.actual===undefined||num('actual',0,100000));
 if(id.startsWith('task:'))return tasks.some(t=>id==='task:'+t.id)&&['Not started','In progress','Done'].includes(String(v.state))&&str('owner',100)&&str('note');
 if(id==='setting:budget')return num('guests',1,74)&&Number.isInteger(v.guests)&&num('friends',1,6)&&Number.isInteger(v.friends)&&num('crew',0,74)&&Number.isInteger(v.crew)&&Number(v.guests)+Number(v.crew)<=75&&num('tax',0,20)&&num('reserve',0,10000)&&num('fees',0,1000)&&num('artist',0,100000)&&num('other',0,100000);
 if(id==='setting:run-notes')return typeof v.text==='string'&&str('text',10000);
 if(/^crew:person-[0-5]$/.test(id))return str('name',100)&&str('note')&&num('paid',0,100000);
 return false;
}
function database() { if (!env.DB) throw new Error('Storage unavailable'); return env.DB; }
export async function GET(request: Request) {
  if (!request.headers.get('oai-authenticated-user-id')) return Response.json({error:'Sign in to load the working plan.'},{status:401});
  try { const rows = await database().prepare('SELECT id,value,revision FROM planning_records').all(); return Response.json({records:rows.results},{headers:{'Cache-Control':'no-store'}}); }
  catch { return Response.json({error:'The saved plan is unavailable. Please retry.'},{status:503}); }
}
export async function PUT(request: Request) {
  if (!request.headers.get('oai-authenticated-user-id')) return Response.json({error:'Sign in to save changes.'},{status:401});
  if (request.headers.get('origin') && request.headers.get('origin') !== new URL(request.url).origin) return Response.json({error:'Invalid origin'},{status:403});
  try {
    const {id,value,revision} = await request.json() as {id:string;value:Record<string,unknown>;revision:number};
    if (typeof id !== 'string' || !/^(item|task|setting|crew):[a-z0-9-]+$/.test(id) || typeof value !== 'object' || value === null || JSON.stringify(value).length > 12000 || !Number.isInteger(revision) || revision < 0) return Response.json({error:'Invalid change.'},{status:400});
    if(!validValue(id,value))return Response.json({error:'Check the values. Guests plus crew cannot exceed 75; costs and quantities must be non-negative.'},{status:400});
    const row = await database().prepare('INSERT INTO planning_records (id,value,revision) VALUES (?,?,1) ON CONFLICT(id) DO UPDATE SET value=excluded.value,revision=planning_records.revision+1 WHERE planning_records.revision=? RETURNING revision').bind(id,JSON.stringify(value),revision).first();
    if (!row) return Response.json({error:'Someone changed this entry. Refresh the plan before saving it again.'},{status:409});
    return Response.json(row);
  } catch { return Response.json({error:'Change not saved. Your draft is still here; try again.'},{status:503}); }
}
