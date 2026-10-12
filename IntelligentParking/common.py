"""The wire protocol shared by the sensor, TCP gateway and central server."""
import json, socket
SLOTS=[f'A{i:02}' for i in range(1,9)]
TOPIC='parking/v2/snapshot'
STALE=8
MAX_MESSAGE=8192

def validate(d):
    if not isinstance(d,dict): raise ValueError('Snapshot must be an object')
    if d.get('source') not in ('simulation','camera'): raise ValueError('Invalid sensor source')
    if not isinstance(d.get('session'),str) or not 1<=len(d['session'])<=64: raise ValueError('Invalid session')
    if type(d.get('seq')) is not int or not 0<=d['seq']<=10**12: raise ValueError('Invalid sequence')
    states=d.get('slots')
    if not isinstance(states,dict) or set(states)!=set(SLOTS): raise ValueError('Expected exactly A01 to A08')
    if any(type(v) is not bool for v in states.values()): raise ValueError('Occupancy must be Boolean')
    return {k:d[k] for k in ('source','session','seq','slots')}

def send_tcp(host,port,data):
    with socket.create_connection((host,port),timeout=3) as sock:
        sock.sendall(json.dumps(data).encode()+b'\n')
        reply=json.loads(sock.makefile('rb').readline(MAX_MESSAGE+1))
        if not reply.get('ok'): raise OSError(reply.get('error','Gateway rejected report'))
        return reply
