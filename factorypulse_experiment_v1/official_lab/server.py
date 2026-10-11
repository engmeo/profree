"""Local experiment HTTP API. No external access; only loopback bind."""
import json,sys,traceback,argparse,subprocess
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1];HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(ROOT),str(ROOT/'src')]
from fjsp import parse_fjsp,greedy
from experiment import run_case

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw):super().__init__(*a,directory=str(HERE/'web'),**kw)
    def do_GET(self):
        if urlsplit(self.path).path == '/api/instances':
            names=('mk01','mk02','mk03')
            return self._send(200,{'instances':{n:{'available':(ROOT/'data'/f'{n}.txt').is_file(), 'path':str(ROOT/'data'/f'{n}.txt')} for n in names}})
        return super().do_GET()
    def do_POST(self):
        if urlsplit(self.path).path=='/api/fetch-instances':
            try:
                n=int(self.headers.get('Content-Length','0'))
                if n<0 or n>1024:raise ValueError('invalid request')
                self.rfile.read(n)
                script=ROOT/'fetch_public_instances.py'
                if not script.is_file():raise FileNotFoundError('Không tìm thấy fetch_public_instances.py trong thư mục factorypulse_experiment_v1')
                cmd=[sys.executable,str(script),'--names','mk02','mk03']
                run=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=120,check=False)
                if run.returncode:raise RuntimeError((run.stderr or run.stdout)[-2500:])
                verified={}
                for name in ('mk02','mk03'):
                    path=ROOT/'data'/f'{name}.txt'
                    if not path.is_file():raise RuntimeError(f'{name} chưa được ghi vào data/')
                    inst=parse_fjsp(path)
                    verified[name]={'jobs':len(inst['jobs']),'machines':inst['machines']}
                return self._send(200,{'message':'Tải và parse mk02/mk03 thành công','verified':verified})
            except subprocess.TimeoutExpired:
                return self._send(504,{'error':'Hết thời gian tải 120 giây; kiểm tra Internet/GitHub rồi thử lại'})
            except Exception as e:
                return self._send(400,{'error':str(e)})
        if urlsplit(self.path).path!='/api/run':self.send_error(404);return
        try:
            n=int(self.headers.get('Content-Length','0'))
            if n<1 or n>20000:raise ValueError('request size invalid')
            body=json.loads(self.rfile.read(n))
            name=body.get('instance','mk01');kind=body.get('scenario','machine')
            if name not in ('mk01','mk02','mk03'):raise ValueError('unsupported instance')
            if kind not in ('machine','material','qa','machine_material','machine_qa','material_qa','all'):raise ValueError('unsupported scenario')
            seed=int(body.get('seed',42));focus=int(body.get('focus',0));timeout=float(body.get('timeout',3))
            if not 0<=seed<=1000000 or not 0<=focus<=100 or not .1<=timeout<=10:raise ValueError('invalid limits')
            path=ROOT/'data'/f'{name}.txt'
            if not path.is_file():raise ValueError(f'{name} chưa có trong data/. Chạy: .\\.venv\\Scripts\\python.exe fetch_public_instances.py --names {name} (trong factorypulse_experiment_v1), sau đó tải lại trang.')
            inst=parse_fjsp(path)
            if focus>=len(inst['jobs']):raise ValueError('focus job out of bounds')
            res=run_case(inst,greedy(inst),seed,kind,focus,timeout=timeout)
            res['instance']=name
            self._send(200,res)
        except Exception as e:
            self._send(400,{'error':str(e),'trace':traceback.format_exc(limit=1)})
    def _send(self,status,obj):
        b=json.dumps(obj,ensure_ascii=False).encode();self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(b)))
        self.end_headers();self.wfile.write(b)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8765);a=p.parse_args()
    print(f'FactoryPulse official CP-SAT lab http://127.0.0.1:{a.port}/',flush=True)
    ThreadingHTTPServer(('127.0.0.1',a.port),Handler).serve_forever()
