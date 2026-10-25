"""Bounded native-vs-emulated diagnostic; preserves both passing and failing cases."""
import argparse
from pathlib import Path
import json
import os
import platform
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host-kind', choices=['native-x64','rosetta'], required=True)
    parser.add_argument('--repeats', type=int, default=3)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert 1 <= args.repeats <= 8
    output = args.output.resolve();output.mkdir(parents=True, exist_ok=True)
    host = {'platform':platform.platform(),'machine':platform.machine(),'started_at':time.time(),
            'github_sha':os.getenv('GITHUB_SHA'),'github_run_id':os.getenv('GITHUB_RUN_ID')}
    if platform.system() == 'Linux':
        host['cpuinfo'] = Path('/proc/cpuinfo').read_text()
        host['kernel'] = Path('/proc/version').read_text()
        host['binfmt_entries'] = [f.name for f in Path('/proc/sys/fs/binfmt_misc').glob('*')]
    (output/'host.json').write_text(json.dumps(host,indent=2))
    cases = [(['--scenario','matrix','--rounds','60','--pace','1'],f'dual-{i}') for i in range(args.repeats)]
    cases += [(['--scenario','single','--rounds','60','--vcs'],'single-vcs')]
    results = []
    for extra, tag in cases:
        command = [sys.executable,str(ROOT/'launch.py'),'--host-kind',args.host_kind,
                   '--catalog','synthetic','--warm','--output',str(output/tag),*extra]
        print('CASE',tag,flush=True)
        process = subprocess.run(command,timeout=390)
        paths = list((output/tag).glob('*/result.json'))
        launch = list((output/tag).glob('*/launch.json'))
        result = json.loads(paths[0].read_text()) if len(paths)==1 else {'result':'HARNESS_ERROR'}
        results.append({'case':tag,'command_exit':process.returncode,'result':result,
                        'launch':json.loads(launch[0].read_text()) if len(launch)==1 else None})
        (output/'matrix.json').write_text(json.dumps(results,indent=2))
    print(json.dumps({'cases':len(results),'statuses':[r['result']['result'] for r in results]}),flush=True)
    bundle=output/'evidence';bundle.mkdir()
    for source in output.rglob('*'):
        if not source.is_file() or bundle in source.parents:continue
        if 'engine-state' in source.parts or 'workspace' in source.parts:continue
        if source.suffix not in ['.json','.jsonl','.log','.py','.mjs']:continue
        target=bundle/source.relative_to(output);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    # FAIL is retained as evidence; the process outcome also makes CI failure visible.
    return 0 if all(r['result']['result']=='PASS' for r in results) else 1

if __name__=='__main__':
    raise SystemExit(main())
