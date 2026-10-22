"""Resource equality/+1 through the real file CLI; internal work/output gates separately."""
import json
import unittest

import test_cli as protocol


class Resources(unittest.TestCase):
    @classmethod
    def setUpClass(cls): protocol.NativeCli.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls): protocol.NativeCli.tearDownClass.__func__(cls)

    call = protocol.NativeCli.call
    failure = protocol.NativeCli.failure

    def document(self, value, name):
        path = self.folder / name
        path.write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')
        return path

    def check_limit(self, doc, name, limit, add):
        path = self.document(doc, name)
        self.assertEqual(json.loads(self.call('evaluate', path, '--format', 'json').stdout)['status'], 'completed')
        add(doc); path = self.document(doc, name + '-over')
        error = self.failure(path, 'RESOURCE_LIMIT', 3)['error']
        self.assertEqual((error['limit'], error['observed']), (limit, limit+1))

    def test_recording_and_label_counts(self):
        doc = dict(schema_version=1, labels=['a'], recordings=[dict(id=f'r{i}', reference=[], prediction=[]) for i in range(1000)])
        self.check_limit(doc, 'recordings', 1000, lambda d:d['recordings'].append(dict(id='over',reference=[],prediction=[])))
        doc = dict(schema_version=1, labels=[f'l{i}' for i in range(256)], recordings=[])
        self.check_limit(doc, 'labels', 256, lambda d:d['labels'].append('over'))

    def test_combined_event_count(self):
        event = lambda id,i:dict(id=id,label='a',onset_s=str(2*i),offset_s=str(2*i+1))
        doc = dict(schema_version=1,labels=['a'],recordings=[dict(id='x',reference=[event(f'r{i}',i) for i in range(1000)],prediction=[event(f'p{i}',i) for i in range(1000)])])
        self.check_limit(doc,'events',2000,lambda d:d['recordings'][0]['prediction'].append(event('over',1001)))

    def test_codepoints_in_recording_event_and_label(self):
        for field in ['recording','event','label']:
            long = '😀'*256
            event = dict(id=long if field=='event' else 'r',label=long if field=='label' else 'a',onset_s='0',offset_s='1')
            doc = dict(schema_version=1,labels=[event['label']],recordings=[dict(id=long if field=='recording' else 'x',reference=[event],prediction=[])])
            def add(d):
                if field=='recording':d['recordings'][0]['id']+='😀'
                elif field=='event':d['recordings'][0]['reference'][0]['id']+='😀'
                else:d['labels'][0]+='😀';d['recordings'][0]['reference'][0]['label']+='😀'
            self.check_limit(doc,field,256,add)

    def test_time_and_collar_business_range(self):
        for field in ['time','collar']:
            doc = dict(schema_version=1,labels=['a'],recordings=[dict(id='x',reference=[dict(id='r',label='a',onset_s='2591999',offset_s='2592000')],prediction=[])])
            if field=='collar':doc['config']=dict(collar_s='2592000')
            path=self.document(doc,field);self.call('evaluate',path,'--format','json')
            if field=='time':doc['recordings'][0]['reference'][0]['offset_s']='2592000.000001'
            else:doc['config']['collar_s']='2592000.000001'
            self.failure(self.document(doc,field+'-over'),'OUT_OF_RANGE',2)

    def test_depth_equal_parses_but_schema_is_invalid(self):
        for depth,code,exit_code in [(16,'INVALID_TYPE',2),(17,'RESOURCE_LIMIT',3)]:
            path=self.folder/f'depth-{depth}'
            path.write_bytes(b'['*depth+b'0'+b']'*depth)
            self.failure(path,code,exit_code)


if __name__ == '__main__':unittest.main()
