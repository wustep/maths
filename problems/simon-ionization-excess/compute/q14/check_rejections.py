#!/usr/bin/env python3
"""Exercise certificate rejection, including a driver-level missing witness."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent


def run(command, expected_success):
    p=subprocess.run(command,capture_output=True,text=True)
    if (p.returncode==0)!=expected_success:
        raise RuntimeError(f'{command}: unexpected exit {p.returncode}\n{p.stdout}\n{p.stderr}')


def main():
    original=json.loads((HERE/'certificate.json').read_text())
    with tempfile.TemporaryDirectory(prefix='ion-q14-negative-') as tmp:
        root=Path(tmp)
        binary=root/'rust-check'
        run(['rustc','--edition=2021','-O','-C','overflow-checks=on',
             str(HERE/'verify.rs'),'-o',str(binary)],True)
        commands=[[sys.executable,str(HERE/'verify.py')],[str(binary)]]
        # Positive controls ensure failures below are not missing dependencies.
        for command in commands:
            run(command+[str(HERE/'certificate.json')],True)
        cases=[]
        bad=copy.deepcopy(original); bad['edges'][-1]='9'
        cases.append(('uncovered endpoint',bad,commands))
        bad=copy.deepcopy(original); bad['edges'][12]=bad['edges'][11]
        cases.append(('empty bin',bad,commands))
        bad=copy.deepcopy(original); bad['phi']='913/1000'
        cases.append(('wrong target',bad,commands))
        bad=copy.deepcopy(original); bad['P_numerators'][0][0]=-10**10
        cases.append(('indefinite P',bad,[commands[0]]))
        bad=copy.deepcopy(original); bad['B_numerators'][0][0]=10**10
        cases.append(('oversized Gram witness',bad,[commands[1]]))
        for name,bad,which in cases:
            path=root/'bad.json'; path.write_text(json.dumps(bad))
            for command in which:
                run(command+[str(path)],False)
            print('rejected:',name)
        for command in commands:
            run(command+[str(root/'missing.json')],False)
        print('rejected: absent certificate in both verifiers')
        driver=root/'driver'; driver.mkdir()
        for name in ('run_all.sh','verify.py','verify.rs'):
            shutil.copy2(HERE/name,driver/name)
        run(['bash',str(driver/'run_all.sh')],False)
        print('rejected: absent certificate through run_all.sh')
    print('All rejection controls passed.')


if __name__=='__main__':
    main()
