"""Host controller: two isolated containers share only a network-none/PID namespace."""
import argparse
import hashlib
import json
import os
import platform
from pathlib import Path
import shutil
import subprocess
import time
import uuid

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT

def docker(*args,timeout=30):
    return subprocess.check_output(['docker',*args],text=True,stderr=subprocess.STDOUT,timeout=timeout).strip()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--arch',choices=['amd64'],default='amd64');parser.add_argument('--snapshot',choices=['true','false'],default='true')
    parser.add_argument('--catalog',choices=['minimal','synthetic'],default='minimal');parser.add_argument('--warm',action='store_true');parser.add_argument('--pace',type=float,default=0);parser.add_argument('--runtime',choices=['opencode','bun'],default='opencode');parser.add_argument('--rounds',type=int,default=20);parser.add_argument('--scenario',choices=['matrix','single'],default='matrix');parser.add_argument('--vcs',action='store_true')
    parser.add_argument('--host-kind',choices=['native-x64','rosetta'],required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.host_kind=='native-x64':assert platform.system()=='Linux' and platform.machine()=='x86_64',(platform.system(),platform.machine())
    else:assert platform.system()=='Darwin' and platform.machine()=='arm64'
    run=args.arch+'-'+args.snapshot+'-'+args.catalog+'-'+args.runtime+'-'+uuid.uuid4().hex[:8]
    out=args.output.resolve()/run;out.mkdir(mode=0o700,parents=True)
    sources={}
    for filename in ['launch.py','driver.py','bun-only.mjs','synthetic_catalog.py']:
        content=(ROOT/filename).read_bytes();(out/filename).write_bytes(content);sources[filename]=hashlib.sha256(content).hexdigest()
    binary=ROOT/'.cache/opencode'
    assert binary.exists(),binary
    image='kortix/kortix-api@sha256:d5da5aa2b4814770629725a46abd237ae0e40479c6ae161a50443fc901b27953'
    driver_image='python@sha256:b921fe7e7522f828d45197a47656ec465a9b15689b27fa8e1fba2864fca5b967' if args.host_kind=='native-x64' else 'python@sha256:7bec7ddcddeff7975d6ba9b4be7dd6f6b2f55e7491539145e2978f7f97ce9144'
    for path in ['workspace','engine-state/home','engine-state/config/opencode','engine-state/data','engine-state/state','engine-state/cache','engine-state/tmp']:(out/path).mkdir(parents=True,exist_ok=True)
    workspace=out/'workspace'
    for i in range(100): (workspace/f'file-{i:03d}.txt').write_text(f'synthetic {i}\n')
    for cmd in [['git','init','-q','-b','main'],['git','config','user.name','Diagnostic'],['git','config','user.email','diag@example.invalid'],['git','add','.'],['git','commit','-qm','synthetic baseline']]:subprocess.run(cmd,cwd=workspace,check=True,env={**os.environ,'GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_GLOBAL':'/dev/null','GIT_AUTHOR_DATE':'2026-10-01T00:00:00+00:00','GIT_COMMITTER_DATE':'2026-10-01T00:00:00+00:00'})
    cfg={'autoupdate':False,'share':'disabled','snapshot':args.snapshot=='true','enabled_providers':['repro'],
        'model':'repro/stall-fixture','small_model':'repro/stall-fixture','default_agent':'build',
        'agent':{'build':{'steps':128},'title':{'disable':True}},'provider':{'repro':{'npm':'@ai-sdk/openai-compatible','env':[],
        'options':{'baseURL':'http://127.0.0.1:18081/v1','apiKey':'synthetic-only'},
        'models':{'stall-fixture':{'id':'stall-fixture','name':'Controlled diagnostic','tool_call':True,'limit':{'context':128000,'output':8192}}}}},
        'permission':{'*':'allow'},'plugin':[],'mcp':{},'lsp':False,'formatter':False,'compaction':{'auto':False,'prune':False},'experimental':{'openTelemetry':False}}
    if args.catalog=='synthetic':
        from synthetic_catalog import models
        cfg['provider']['repro']['models']={**models(),**cfg['provider']['repro']['models']}
    (out/'probe-options.json').write_text(json.dumps({'catalog':args.catalog,'warm':args.warm,'pace':args.pace,'runtime':args.runtime,'rounds':args.rounds,'scenario':args.scenario,'vcs':args.vcs}))
    (out/'engine-state/config/opencode/opencode.json').write_text(json.dumps(cfg))
    (out/'engine-state/models-empty.json').write_text('{}')
    (out/'engine-state/gitconfig').write_text('[safe]\n\tdirectory = /workspace\n')
    # The pinned engine runs as UID/GID 1000. Linux CI's host UID can differ;
    # prepare only these disposable synthetic mounts, without changing engine identity.
    out.chmod(0o755)
    ownership = docker('run','--rm','--pull=never','--network','none','--user','0:0',
        '--mount',f'type=bind,src={out},dst=/out','--entrypoint','python3',driver_image,'-c',
        'from pathlib import Path; import os,json; '
        'roots=[Path("/out/workspace"),Path("/out/engine-state")]; '
        '[(os.chown(p,1000,1000)) for root in roots for p in [root,*root.rglob("*")]]; '
        'print(json.dumps({str(p):{"uid":p.stat().st_uid,"gid":p.stat().st_gid,"mode":oct(p.stat().st_mode & 0o777)} for p in roots}))')
    receipt={'host_kind':args.host_kind,'host_system':platform.system(),'host_machine':platform.machine(),'host_platform':platform.platform(),'docker_arch':docker('info','--format','{{.Architecture}}'),'driver_image':driver_image,'config_sha256':hashlib.sha256((out/'engine-state/config/opencode/opencode.json').read_bytes()).hexdigest(),'initial_git_oid':subprocess.check_output(['git','rev-parse','HEAD'],cwd=workspace,text=True).strip(),'source_hashes':sources,'run_id':run,'catalog':args.catalog,'warm':args.warm,'pace':args.pace,'runtime':args.runtime,'rounds':args.rounds,'scenario':args.scenario,'vcs':args.vcs,'model_count':len(cfg['provider']['repro']['models']),'arch':args.arch,'snapshot':args.snapshot,'engine_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'image':image,'network':'none; loopback shared with a native Python observer on each host','resources':{'target_cpus':2,'target_memory':'2g','driver_cpus':1,'driver_memory':'512m'}}
    assert receipt['engine_sha256']=='de0724a36eaf3166e7f1ff38d0f4478b95ccc47725e9597b3fe66d3d3e18baa2'
    if args.host_kind=='native-x64':assert receipt['docker_arch'] in ['x86_64','amd64']
    receipt['mount_ownership']=json.loads(ownership)
    ids={}
    try:
        ids['driver']=docker('run','-d','--pull=never','--name','hh-stall-driver-'+run,'--cap-add','SYS_PTRACE','--init','--network','none','--cpus','1','--memory','512m','--pids-limit','128','--mount',f'type=bind,src={out},dst=/out','--entrypoint','python3',driver_image,'/out/driver.py')
        deadline=time.monotonic()+20
        while not (out/'driver-ready').exists() and time.monotonic()<deadline:time.sleep(.1)
        assert (out/'driver-ready').exists(),'driver startup'
        environment={'PATH':'/usr/local/bin:/usr/bin:/bin','HOME':'/engine-state/home','XDG_CONFIG_HOME':'/engine-state/config','XDG_DATA_HOME':'/engine-state/data','XDG_STATE_HOME':'/engine-state/state','XDG_CACHE_HOME':'/engine-state/cache','TMPDIR':'/engine-state/tmp','SHELL':'/bin/bash','OPENCODE_DISABLE_DEFAULT_PLUGINS':'true','OPENCODE_DISABLE_MODELS_FETCH':'true','OPENCODE_MODELS_PATH':'/engine-state/models-empty.json','OPENCODE_DISABLE_CLAUDE_CODE':'true','GIT_CONFIG_GLOBAL':'/engine-state/gitconfig'}
        engine_args=['/engine/opencode','serve','--hostname','127.0.0.1','--port','4096','--print-logs','--log-level','DEBUG']
        if args.runtime=='bun':
            environment['BUN_BE_BUN']='1';engine_args=['/engine/opencode','/out/bun-only.mjs']
        ids['engine']=docker('run','-d','--pull=never','--platform','linux/'+args.arch,'--name','hh-stall-engine-'+run,'--network','container:'+ids['driver'],'--pid','container:'+ids['driver'],'--cpus','2','--memory','2g','--pids-limit','256','--no-healthcheck','--workdir','/workspace','--mount',f'type=bind,src={out},dst=/out','--mount',f'type=bind,src={binary},dst=/engine/opencode,readonly','--mount',f'type=bind,src={workspace},dst=/workspace','--mount',f'type=bind,src={out/"engine-state"},dst=/engine-state','--entrypoint','/usr/bin/env',image,'-i',*[k+'='+v for k,v in environment.items()],*engine_args)
        receipt['containers']=ids;(out/'launch.json').write_text(json.dumps(receipt,indent=2))
        print('STARTED',out,flush=True)
        deadline=time.monotonic()+320;last=None
        while time.monotonic()<deadline:
            if (out/'checks.jsonl').exists():
                checks=(out/'checks.jsonl').read_text().splitlines()
                if len(checks)!=last:print('PROGRESS',run,'checks',len(checks),flush=True);last=len(checks)
            if (out/'result.json').exists():break
            try:
                state=json.loads(docker('inspect','--format','{{json .State}}',ids['engine'],timeout=5))
                with (out/'container-state.jsonl').open('a') as f:f.write(json.dumps({'at':time.time(),'state':state})+'\n')
            except Exception as e:receipt['state_read_error']=str(e)
            time.sleep(1)
        if not (out/'result.json').exists():receipt['controller_error']='320-second bounded probe deadline'
        receipt['workspace_files']={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in workspace.iterdir() if f.is_file()}
    finally:
        for role,cid in reversed(list(ids.items())):
            try:
                (out/(role+'.log')).write_text(docker('logs',cid,timeout=10))
            except Exception as e:receipt[role+'_log_error']=str(e)
            try:
                docker('stop','-t','5',cid,timeout=15)
                state=json.loads(docker('inspect',cid))[0]['State'];receipt[role+'_final_state']=state
                docker('rm',cid)
            except Exception as e:receipt[role+'_cleanup_error']=str(e)
        (out/'launch.json').write_text(json.dumps(receipt,indent=2)+'\n')
    if (out/'result.json').exists():print((out/'result.json').read_text(),flush=True)
    print('EVIDENCE',out,flush=True)

if __name__=='__main__':main()
