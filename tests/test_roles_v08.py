from pathlib import Path
import tempfile,sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_roles import review
class RoleTests(unittest.TestCase):
 def run_review(self,text,roles):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);(p/'package.mo').write_text(text);return review(p,{'roles':roles})
 def test_whitebox_connect_only(self):
  t='model System Modelica.Blocks.Interfaces.RealInput u; Modelica.Blocks.Interfaces.RealOutput y; equation connect(u,y); end System;';r=self.run_review(t,{'System':'SB'});self.assertEqual(r['status'],'NO_LOCAL_FINDING')
 def test_whitebox_equation(self):
  t='model System Modelica.Blocks.Interfaces.RealInput u; Modelica.Blocks.Interfaces.RealOutput y; equation y=2*u; end System;';self.assertEqual(self.run_review(t,{'System':'SB'})['status'],'FINDINGS')
 def test_constant_runtime_input_is_not_parameter(self):
  t='model System Modelica.Blocks.Math.Gain gain(u=1); end System;';r=self.run_review(t,{'System':'SB'});self.assertIn('WHITEBOX_CHILD_INPUT_BINDING',str(r))
 def test_parameter_modifier_allowed(self):
  t='model System parameter Real k=2; Modelica.Blocks.Math.Gain gain(k=k); end System;';self.assertEqual(self.run_review(t,{'System':'SB'})['status'],'NO_LOCAL_FINDING')
 def test_bu_cannot_hide_msl_blocks(self):
  t='model Behavior Modelica.Blocks.Continuous.Integrator memory; end Behavior;';self.assertIn('BU_RUNTIME_CHILD',str(self.run_review(t,{'Behavior':'BU'})))
 def test_whitebox_initial_section(self):
  t='model System Real x; initial equation x=1; equation der(x)=0; end System;';self.assertIn('WHITEBOX_ALGORITHM_OR_INITIAL_SECTION',str(self.run_review(t,{'System':'SB'})))
 def test_effective_inherited_behavior(self):
  t='package Example model Base Real x; equation x=1; end Base; model System extends Base; end System; end Example;';self.assertEqual(self.run_review(t,{'Example.System':'SB'})['status'],'FINDINGS')
 def test_unknown_library_base(self):
  t='model Device extends Modelica.Blocks.Continuous.FirstOrder; end Device;';self.assertEqual(self.run_review(t,{'Device':'LU'})['status'],'REVIEW_REQUIRED')
 def test_empty_role_map_rejected(self):
  with self.assertRaises(ValueError):self.run_review('model A end A;',{})
 def test_ab_count(self):
  t='model Assembly Modelica.Blocks.Math.Gain gain; end Assembly;';self.assertIn('AB_FEWER_THAN_TWO',str(self.run_review(t,{'Assembly':'AB'})))
if __name__=='__main__':unittest.main()
