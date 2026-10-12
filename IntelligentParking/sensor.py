"""IoT sensor agent: automatic traffic model or browser camera readings -> TCP."""
import argparse,json,threading,time,uuid
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from common import SLOTS,send_tcp
BASE=Path(__file__).parent
class Sensor:
    def __init__(self,host,port):
        self.lock=threading.Lock();self.host=host;self.port=port;self.mode='simulation';self.paused=False
        self.session=uuid.uuid4().hex;self.seq=0;self.states={s:False for s in SLOTS}
        self.camera_seen=None;self.camera_token=None;self.status='Connecting to TCP gateway';self.started=time.monotonic()
        self.last_ack=None;self.stop=threading.Event()
    def snapshot(self):
        with self.lock:return {'mode':self.mode,'paused':self.paused,'slots':self.states.copy(),'status':self.status,
            'last_ack':self.last_ack,'seq':self.seq,'cycle':int(time.monotonic()-self.started)%80,
            'camera_ready':self.camera_seen is not None and time.monotonic()-self.camera_seen<3.5}
    def set_mode(self,mode):
        if mode not in ('simulation','camera'):raise ValueError('Invalid mode')
        with self.lock:
            self.mode=mode;self.paused=False;self.camera_seen=None;self.camera_token=uuid.uuid4().hex if mode=='camera' else None
            self.session=uuid.uuid4().hex;self.seq=0;self.started=time.monotonic();self.last_ack=None
            self.status='Waiting for fresh camera readings' if mode=='camera' else 'Automatic traffic starting'
            return self.camera_token
    def camera(self,d):
        slots=d.get('slots')
        if not isinstance(slots,dict) or set(slots)!=set(SLOTS) or any(type(v)is not bool for v in slots.values()):raise ValueError('Invalid camera states')
        with self.lock:
            if self.mode!='camera' or d.get('token')!=self.camera_token:raise ValueError('Camera session expired')
            self.states=slots;self.camera_seen=time.monotonic()
    def loop(self):
        while not self.stop.is_set():
            now=time.monotonic()
            with self.lock:
                if self.mode=='simulation':
                    # 80-second deterministic arrival/departure cycle, no manual slot buttons.
                    t=int(now-self.started)%80
                    self.states={s:(5+i*5<=t<50+i*3) for i,s in enumerate(SLOTS)}
                ready=self.mode=='simulation' or self.camera_seen is not None and now-self.camera_seen<3.5
                active=ready and not self.paused
                if not ready:self.status='Camera not reporting. Calibrate, start detection and keep this tab visible.'
                if self.paused:self.status='Sensor transmission paused for failure demonstration'
                if active:
                    self.seq+=1;d={'source':self.mode,'session':self.session,'seq':self.seq,'slots':self.states.copy()}
            if active:
                try:
                    ack=send_tcp(self.host,self.port,d)
                    with self.lock:self.last_ack=ack;self.status='TCP gateway accepted report; MQTT broker acknowledged'
                except (OSError,ValueError) as exc:
                    with self.lock:self.last_ack=None;self.status='Connection problem: '+str(exc)
            self.stop.wait(1)
SENSOR=None
class Handler(BaseHTTPRequestHandler):
    def reply(self,d):
        b=json.dumps(d).encode();self.send_response(200);self.send_header('Content-Type','application/json')
        self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
    def do_GET(self):
        if self.path=='/api/state':self.reply(SENSOR.snapshot());return
        files={'/':('sensor.html','text/html; charset=utf-8'),'/style.css':('style.css','text/css'),'/vision.js':('vision.js','application/javascript')}
        if self.path not in files:self.send_error(404);return
        filename,mime=files[self.path];b=(BASE/'web'/filename).read_bytes()
        self.send_response(200);self.send_header('Content-Type',mime);self.end_headers();self.wfile.write(b)
    def do_POST(self):
        try:
            n=int(self.headers.get('Content-Length',0))
            if not 0<n<=8192:raise ValueError('Invalid body size')
            d=json.loads(self.rfile.read(n))
            if not isinstance(d,dict):raise ValueError('Object expected')
            if self.path=='/api/mode':self.reply({'ok':True,'token':SENSOR.set_mode(d.get('mode'))})
            elif self.path=='/api/camera':SENSOR.camera(d);self.reply({'ok':True})
            elif self.path=='/api/pause':
                with SENSOR.lock:SENSOR.paused=not SENSOR.paused
                self.reply({'ok':True})
            else:self.send_error(404)
        except (ValueError,TypeError):self.send_error(400)
    def log_message(self,*a):pass
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--gateway-host',default='127.0.0.1');p.add_argument('--gateway-port',type=int,default=5050)
    p.add_argument('--port',type=int,default=8091);a=p.parse_args()
    SENSOR=Sensor(a.gateway_host,a.gateway_port);threading.Thread(target=SENSOR.loop,daemon=True).start()
    http=ThreadingHTTPServer(('127.0.0.1',a.port),Handler);print(f'Sensor station http://127.0.0.1:{a.port}',flush=True)
    try:http.serve_forever()
    except KeyboardInterrupt:pass
    finally:SENSOR.stop.set();http.server_close()
