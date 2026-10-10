from pathlib import Path
import unittest,sys,tempfile,json,subprocess
S=Path(__file__).resolve().parents[1]/'scripts';sys.path.insert(0,str(S))
from modelica_support import Source
from documentation_support import enrich_generated
from verify_aux_only import compare
from audit_project import audit
from check_contract import validate
from inspect_result_metadata import read_xml

BASE='''within Demo;
model Device "device"
  parameter Real capacity(unit="C")=100 "capacity";
  Real x(start=0,fixed=true) "state";
  Modelica.Blocks.Interfaces.RealOutput y "output";
  constant String label="business-string";
equation
  der(x)=-x;
  y=x;
  annotation(Icon(graphics={Text(extent={{-10,-10},{10,10}},textString="device")}),experiment(StopTime=10),Documentation(info="<html>old</html>"));
end Device;
'''
CAT={'version':'0.7','classes':{'Demo.Device':{'title':'设备','summary':'演示源码中的一阶状态和输出','fields':{'capacity':'额定电荷量','x':'内部状态','y':'公开输出','label':'业务字符串'},'parents':[],'resolved_types':{}}},'model_classes':['Demo.Device']}
class SourceTests(unittest.TestCase):
 def test_parse(self):
  s=Source(BASE);self.assertFalse(s.unparsed);self.assertEqual(len(s.classes[0].decls),4)
 def test_enrich_and_invariant(self):
  n=enrich_generated(BASE,catalog=CAT);self.assertEqual(Source(BASE).canonical(False),Source(n).canonical(False));self.assertIn('用途与定位',Source(n).doc_info(Source(n).classes[0]))
 def test_idempotent(self):
  n=enrich_generated(BASE,catalog=CAT);self.assertEqual(n,enrich_generated(n,catalog=CAT))
 def test_binding_protected(self):self.assertNotEqual(Source(BASE).canonical(),Source(BASE.replace('=100','=101')).canonical())
 def test_string_constant_protected(self):self.assertNotEqual(Source(BASE).canonical(),Source(BASE.replace('business-string','other-business')).canonical())
 def test_graphics_protected(self):self.assertNotEqual(Source(BASE).canonical(),Source(BASE.replace('textString="device"','textString="other"')).canonical())
 def test_experiment_protected(self):self.assertNotEqual(Source(BASE).canonical(),Source(BASE.replace('StopTime=10','StopTime=20')).canonical())
 def test_units_protected(self):self.assertNotEqual(Source(BASE).canonical(),Source(BASE.replace('unit="C"','unit="J"')).canonical())
 def test_initialization_protected(self):self.assertNotEqual(Source(BASE).canonical(),Source(BASE.replace('fixed=true','fixed=false')).canonical())
 def test_root_version(self):
  a='package Demo annotation(version="1",uses(Modelica(version="4.0.0"))); end Demo;';b=a.replace('version="1"','version="2"')
  self.assertEqual(Source(a).canonical(),Source(b).canonical());self.assertNotEqual(Source(a).canonical(False),Source(b).canonical(False));self.assertNotEqual(Source(a).canonical(),Source(a.replace('4.0.0','4.1.0')).canonical())
 def test_multi_declaration(self):
  s=Source('model A Real x "X",y "Y"; equation x=1; y=x; end A;');self.assertEqual([d.name for d in s.classes[0].decls],['x','y'])
 def test_short_class(self):
  text='within Demo; connector In = input Real;';cat={'version':'0.7','rename_descriptions':True,'classes':{'Demo.In':{'title':'输入','summary':'实数输入别名','declaration_description':'In（输入）','fields':{}}}}
  n=enrich_generated(text,catalog=cat);s=Source(n);self.assertFalse(s.unparsed);self.assertEqual(s.classes[0].description,'In（输入）');self.assertEqual(Source(text).canonical(),s.canonical())
 def test_redeclare_extends(self):
  s=Source('package A redeclare record extends ThermodynamicState Real p; end ThermodynamicState; end A;');self.assertFalse(s.unparsed);self.assertEqual(len(list(s.all_classes())),2)
 def test_bad_brackets(self):
  with self.assertRaises(ValueError):Source('model A Real x(start=1; end A;')
 def test_unknown_stops_enrichment(self):
  with self.assertRaises(ValueError):enrich_generated('unknown_source;',catalog=CAT)
 def test_file_guard(self):
  with tempfile.TemporaryDirectory() as td:
   a=Path(td)/'a';b=Path(td)/'b';a.mkdir();b.mkdir();(a/'Device.mo').write_text(BASE);(b/'Device.mo').write_text(enrich_generated(BASE,catalog=CAT));self.assertEqual(compare(a,b,[])['status'],'STATIC_AUXILIARY_ONLY');(b/'Device.mo').write_text(BASE.replace('der(x)=-x','der(x)=x'));self.assertEqual(compare(a,b,[])['status'],'REVIEW_REQUIRED')
 def test_inventory(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);(p/'Device.mo').write_text(BASE);r=audit(p);self.assertEqual(r['status'],'PARSED');self.assertEqual(r['modelBlockCount'],1)
 def test_contract(self):
  c={'entryModel':'Demo.Main','signals':[dict(id='x',path='x',description='state',unit='1',identity='state',timeSemantics='continuous',required=True)]};self.assertEqual(validate(c)['status'],'SCHEMA_OK');c['signals']*=2;self.assertEqual(validate(c)['status'],'INVALID')
 def test_xml_metadata(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'init.xml';p.write_text('<root><ScalarVariable name="T" description="温度"><Real unit="K"/></ScalarVariable></root>');r=read_xml(p);self.assertEqual(r[0]['description'],'温度');self.assertEqual(r[0]['unit'],'K')
 def test_guarded_command_success(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);r=subprocess.run([sys.executable,str(S/'run_guarded.py'),'--cwd',td,'--timeout','5','--log',str(p/'log'),'--metadata',str(p/'meta'),'--',sys.executable,'-c','print("ok")'],capture_output=True,text=True);self.assertEqual(r.returncode,0);self.assertEqual(json.loads((p/'meta').read_text())['engineeringAcceptance'],'NOT_EVALUATED')
 def test_guarded_timeout(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);r=subprocess.run([sys.executable,str(S/'run_guarded.py'),'--cwd',td,'--timeout','0.1','--log',str(p/'log'),'--metadata',str(p/'meta'),'--',sys.executable,'-c','import time; time.sleep(3)'],capture_output=True,text=True);self.assertEqual(r.returncode,124);self.assertEqual(json.loads((p/'meta').read_text())['status'],'TIMEOUT')
if __name__=='__main__':unittest.main()
