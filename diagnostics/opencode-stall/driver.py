"""Isolated, zero-network/zero-paid-model probe of pinned native OpenCode tools."""
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import json
import os
from pathlib import Path
import re
import threading
import time
import urllib.request
import urllib.error
import uuid

OUT=Path('/out')
BASE='http://127.0.0.1:4096'
MODEL='stall-fixture'
TRACE_LOCK=threading.Lock()
REQUESTS=0
STOP=threading.Event()
OPTIONS=json.loads((OUT/'probe-options.json').read_text())
WARM_PATHS=['/experimental/tool/ids','/agent','/skill','/config/providers','/mcp']

def record(name,value):
    with TRACE_LOCK:
        with (OUT/name).open('a') as f:f.write(json.dumps({'at':time.time(),**value})+'\n')

def content(value):
    if isinstance(value,str):return value
    return '\n'.join(x.get('text','') for x in value or [] if isinstance(x,dict))

def api(path,body=None,timeout=5):
    req=urllib.request.Request(BASE+path, data=None if body is None else json.dumps(body).encode(),
        headers={'Content-Type':'application/json','x-opencode-directory':'/workspace'})
    with urllib.request.urlopen(req,timeout=timeout) as r:
        raw=r.read()
        return json.loads(raw) if raw else None

COMMANDS={
 'plain':['ls -la >/dev/null; printf "REPRO_OK\\n"','git status --short >/dev/null; printf "REPRO_OK\\n"'],
 'pipeline':['git status --short | head -50; printf "REPRO_OK\\n"',
             'git ls-files | head -5; printf "REPRO_OK\\n"'],
 'write':['printf "%s\\n" "round-$RANDOM" > changed.txt; git status --short | head -50; printf "REPRO_OK\\n"',
          'git diff --stat | head -5; printf "REPRO_OK\\n"'],
}

class Handler(BaseHTTPRequestHandler):
    protocol_version='HTTP/1.1'
    def log_message(self,*args):pass
    def do_POST(self):
        global REQUESTS
        try:
            if self.path!='/v1/chat/completions':raise ValueError('unexpected endpoint')
            body=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            with TRACE_LOCK:
                REQUESTS+=1
                seq=REQUESTS
            if seq>250:raise ValueError('fixture request bound')
            messages=body['messages']
            latest=max(i for i,m in enumerate(messages) if m['role']=='user')
            marker=re.search(r'REPRO:([a-z0-9]+):(plain|pipeline|write):(\d+)',content(messages[latest]['content']))
            if not marker:raise ValueError('missing fixture marker')
            tag,kind,rounds=marker[1],marker[2],int(marker[3])
            results=[m for m in messages[latest+1:] if m['role']=='tool']
            if any('REPRO_OK' not in content(m['content']) for m in results):raise ValueError('native tool failed')
            index=len(results)//2
            tools={t['function']['name'] for t in body.get('tools',[])}
            if 'bash' not in tools:raise ValueError('native bash missing')
            calls=[]
            if index<rounds:
                for j,command in enumerate(COMMANDS[kind]):
                    calls.append({'index':j,'id':f'call_{tag}_{index}_{j}','type':'function',
                        'function':{'name':'bash','arguments':json.dumps({'command':command,'description':'Synthetic native subprocess diagnostic','timeout':5000})}})
            record('fixture.jsonl',{'sequence':seq,'tag':tag,'kind':kind,'results':len(results),'calls':len(calls)})
            if tag.startswith('dual') and OPTIONS.get('pace'):time.sleep(OPTIONS['pace'])
            self.send_response(200);self.send_header('Content-Type','text/event-stream');self.send_header('Connection','close');self.end_headers();self.close_connection=True
            base={'id':'chatcmpl_'+uuid.uuid4().hex,'object':'chat.completion.chunk','created':int(time.time()),'model':MODEL}
            for delta,finish in [({'role':'assistant','content':''},None),
                ({'tool_calls':calls} if calls else {'content':f'REPRO_DONE {tag}'},None),
                ({},'tool_calls' if calls else 'stop')]:
                frame={**base,'choices':[{'index':0,'delta':delta,'finish_reason':finish}]}
                self.wfile.write(('data: '+json.dumps(frame)+'\n\n').encode())
            self.wfile.write(('data: '+json.dumps({**base,'choices':[],'usage':{'prompt_tokens':0,'completion_tokens':0,'total_tokens':0}})+'\n\ndata: [DONE]\n\n').encode());self.wfile.flush()
        except Exception as e:
            record('fixture-errors.jsonl',{'type':type(e).__name__,'error':str(e)})
            try:self.send_error(422,str(e))
            except OSError:pass

def proc_field(path):
    try:return path.read_text().strip()
    except OSError as e:return {'unavailable':type(e).__name__}

def proc_snapshot(detailed=False):
    rows=[]
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():continue
        try:
            stat=(p/'stat').read_text();end=stat.rindex(')');fields=stat[end+2:].split()
            comm=(p/'comm').read_text().strip()
            if comm in ['python3','docker-init','sleep']:continue
            row={'pid':int(p.name),'ppid':int(fields[1]),'comm':comm,'state':fields[0],
                'cmdline':(p/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace'),
                'wchan':(p/'wchan').read_text().strip()}
            if detailed and 'opencode' in comm:
                row['threads']=[{'tid':t.name,**{field:proc_field(t/field) for field in ['comm','stat','wchan','syscall','stack']}} for t in (p/'task').iterdir()]
                try:row['exe']=os.readlink(p/'exe')
                except OSError as e:row['exe_error']=type(e).__name__
                row['status']=(p/'status').read_text()
            rows.append(row)
        except (OSError,ValueError):pass
    return rows

def monitor():
    previous=None
    while not STOP.wait(.1):
        try:rows=proc_snapshot()
        except Exception as e:
            record('monitor-errors.jsonl',{'error':repr(e)});continue
        key=[(x['pid'],x['state']) for x in rows]
        if key!=previous:record('processes.jsonl',{'processes':rows});previous=key

def timed_read(path,timeout=2):
    start=time.monotonic()
    try:
        req=urllib.request.Request(BASE+path,headers={'x-opencode-directory':'/workspace'})
        with urllib.request.urlopen(req,timeout=timeout) as r:
            raw=r.read();value={'path':path,'status':r.status,'bytes':len(raw)}
    except Exception as e:value={'path':path,'error':type(e).__name__+': '+str(e)}
    value['elapsed']=time.monotonic()-start
    record('http-timings.jsonl',value)
    return value

def health_monitor():
    while not STOP.is_set():
        timed_read('/global/health')
        timed_read('/session?directory=%2Fworkspace&limit=1')
        STOP.wait(1)

def vcs_monitor():
    while not STOP.is_set():
        timed_read('/vcs/diff?mode=git',timeout=10)
        STOP.wait(2)

def warm_loop():
    while not STOP.is_set():
        with ThreadPoolExecutor(max_workers=5) as pool:
            results=list(pool.map(lambda p:timed_read(p,timeout=120),WARM_PATHS))
        record('warm.jsonl',{'results':results})
        if STOP.wait(30):break

def wait_ready():
    deadline=time.monotonic()+60
    while time.monotonic()<deadline:
        try:
            h=api('/global/health',timeout=1)
            if h.get('healthy'):return h
        except Exception:pass
        time.sleep(.25)
    raise TimeoutError('engine health startup')

def inspect(sid):
    messages=api(f'/session/{sid}/message',timeout=3)
    parts=[p for m in messages for p in m.get('parts',[])]
    status=api('/session/status',timeout=3)
    return {'messages':messages,'parts':parts,'status':status.get(sid,{'type':'idle'})}

def run_turn(kind,rounds,tag):
    sid=api('/session',{'title':f'{kind}-{tag}'},timeout=20)['id']
    start=time.monotonic();before=REQUESTS
    api(f'/session/{sid}/prompt_async',{'agent':'build','model':{'providerID':'repro','modelID':MODEL},
        'parts':[{'type':'text','text':f'REPRO:{tag}:{kind}:{rounds}'}]},timeout=20)
    deadline=time.monotonic()+280;last_progress=start;last_count=-1
    while time.monotonic()<deadline:
        try:
            value=inspect(sid)
        except (OSError,TimeoutError) as e:
            record('inspect-errors.jsonl',{'sid':sid,'error':str(e)})
            if time.monotonic()-last_progress>25:raise
            time.sleep(.25);continue
        tools=[p for p in value['parts'] if p['type']=='tool']
        completed=[p for p in tools if p['state']['status']=='completed']
        failed=[p for p in tools if p['state']['status']=='error']
        terminal=any(p['type']=='text' and f'REPRO_DONE {tag}' in p.get('text','') for p in value['parts'])
        if len(completed)!=last_count:last_progress=time.monotonic();last_count=len(completed)
        if failed or time.monotonic()-last_progress>20:
            (OUT/f'failed-{tag}.json').write_text(json.dumps(value,indent=2))
            raise RuntimeError(f'{tag}: native failure/no progress completed={len(completed)} failed={len(failed)} state={value["status"]}')
        if terminal and value['status']['type']=='idle':
            assert len(completed)==rounds*2,(tag,len(completed))
            result={'tag':tag,'sid':sid,'kind':kind,'rounds':rounds,'completed_tools':len(completed),'elapsed':time.monotonic()-start,'fixture_requests':REQUESTS-before}
            (OUT/f'turn-{tag}.json').write_text(json.dumps(value,indent=2));record('checks.jsonl',result)
            print(json.dumps(result),flush=True);return result
        time.sleep(.25)
    raise TimeoutError(tag)

def bun_turn():
    api('/start',{})
    start=time.monotonic();deadline=start+150;last_count=0;last_change=start
    while time.monotonic()<deadline:
        value=api('/progress',timeout=3)
        if value['failed']:raise RuntimeError(value['failed'])
        if value['completed']!=last_count:last_change=time.monotonic();last_count=value['completed']
        if value['finished']:
            assert value['completed']==600,value
            return {'runtime':value['runtime'],'completed':600,'elapsed':time.monotonic()-start}
        if time.monotonic()-last_change>20:raise RuntimeError('Bun child completion stalled: '+json.dumps(value))
        time.sleep(.5)
    raise TimeoutError('Bun-only 150-second bound')

def main():
    result={'options':OPTIONS,'started_at':time.time(),'model':'controlled local SSE; not a real model','paid_calls':0,'checks':[]}
    server=ThreadingHTTPServer(('127.0.0.1',18081),Handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    threading.Thread(target=monitor,daemon=True).start()
    (OUT/'driver-ready').write_text('ready\n')
    try:
        result['health']=wait_ready();print('ENGINE_READY',result['health'],flush=True)
        threading.Thread(target=health_monitor,daemon=True).start()
        if OPTIONS.get('vcs'):threading.Thread(target=vcs_monitor,daemon=True).start()
        if OPTIONS.get('warm'):threading.Thread(target=warm_loop,daemon=True).start()
        if OPTIONS.get('runtime')=='bun':result['checks'].append(bun_turn())
        elif OPTIONS.get('scenario')=='single':result['checks'].append(run_turn('write',OPTIONS.get('rounds',20),'singledeep'))
        else:
            for kind in ['plain','pipeline','write']:
                result['checks'].append(run_turn(kind,5,'single'+kind))
            with ThreadPoolExecutor(max_workers=2) as pool:
                result['checks'].extend(list(pool.map(lambda x:run_turn('write',OPTIONS.get('rounds',20),x),['duala','dualb'])))
        result['result']='PASS'
    except Exception as e:
        result.update(result='FAIL',error_type=type(e).__name__,error=str(e))
        (OUT/'failure-detected.json').write_text(json.dumps({'at':time.time(),'error':str(e)}))
        result['processes']=proc_snapshot(True)
        record('failed-processes.jsonl',{'processes':result['processes']})
        time.sleep(10)
        record('failed-processes.jsonl',{'processes':proc_snapshot(True)})
        for path in ['/global/health','/session/status']:
            try:result[path]=api(path,timeout=3)
            except Exception as q:result[path]={'error':type(q).__name__+': '+str(q)}
        print(json.dumps({'result':'FAIL','error':str(e)}),flush=True)
    finally:
        result['fixture_requests']=REQUESTS;result['finished_at']=time.time()
        (OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n')
        STOP.set();server.shutdown()

if __name__=='__main__':main()
