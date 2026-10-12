import time,unittest
from common import SLOTS,validate
from server import State
from sensor import Sensor
class CoreTests(unittest.TestCase):
    def payload(self,seq=1,occupied=False):return {'source':'simulation','session':'test','seq':seq,'slots':{s:occupied for s in SLOTS},'gateway_at':time.time()}
    def test_validation(self):
        d=self.payload();d['slots']['A01']='false'
        with self.assertRaises(ValueError):validate(d)
        with self.assertRaises(ValueError):validate(None)
    def test_full_and_departure(self):
        s=State();s.update(self.payload(1,True));self.assertIsNone(s.snapshot(True)['recommendation'])
        d=self.payload(2,True);d['slots']['A03']=False;s.update(d);self.assertEqual(s.snapshot(True)['recommendation'],'A03')
    def test_old_duplicate_and_stale(self):
        s=State();s.update(self.payload());s.update(self.payload());self.assertEqual(s.messages,1)
        self.assertEqual(s.duplicates,1);s.seen-=9;self.assertEqual(s.snapshot(True)['counts']['UNKNOWN'],8)
        d=self.payload(2);d['gateway_at']-=20
        with self.assertRaises(ValueError):s.update(d)
    def test_broker_loss(self):
        s=State();s.update(self.payload());self.assertEqual(s.snapshot(False)['counts']['UNKNOWN'],8)
    def test_camera_session(self):
        s=Sensor('127.0.0.1',5050);token=s.set_mode('camera');s.camera({'token':token,'slots':{x:False for x in SLOTS}})
        self.assertTrue(s.snapshot()['camera_ready']);s.set_mode('simulation')
        with self.assertRaises(ValueError):s.camera({'token':token,'slots':{x:False for x in SLOTS}})
if __name__=='__main__':unittest.main(verbosity=2)
