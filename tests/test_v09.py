from pathlib import Path
import tempfile,sys,unittest,json,subprocess
S=Path(__file__).resolve().parents[1]/'scripts';sys.path.insert(0,str(S))
from verify_change_scope import scoped_signature,compare_trees,lexical_tokens
from format_modelica import format_text,format_tree
from audit_roles import review as roles_review
from audit_connections import review as connections_review
from connection_colors import Index

BASE='''within;
package Demo "演示"
  connector Port = Modelica.Blocks.Interfaces.RealInput "输入";
  model Device "设备"
    parameter Real k=1 "系数";
    Modelica.Blocks.Interfaces.RealInput u "输入"
      annotation(Placement(transformation(extent={{-110,-10},{-90,10}})),HideResult=false);
    Modelica.Blocks.Interfaces.RealOutput y "输出";
    constant String label="data-file.csv";
    // Keep this engineering comment.  
  equation
    connect(u,y) annotation(Line(points={{-100,0},{100,0}},color={0,0,127},thickness=0.5));
    annotation(Icon(graphics={Rectangle(extent={{-90,-90},{90,90}},lineColor={0,0,0})}),
      Diagram(coordinateSystem(extent={{-150,-150},{150,150}})),
      experiment(StopTime=10,Tolerance=1e-6),Evaluate=false,
      Documentation(info="<html>设备说明</html>"));
  end Device;
  annotation(version="0.8.0",uses(Modelica(version="4.0.0")));
end Demo;
'''

def signature(t,mode='visual-only',rv=False):return scoped_signature(t,mode,rv)

class ScopeTests(unittest.TestCase):
 def test_format_spacing(self):self.assertEqual(signature(BASE,'format-only'),signature(BASE.replace('parameter Real','parameter   Real'),'format-only'))
 def test_format_comment_protected(self):self.assertNotEqual(signature(BASE,'format-only'),signature(BASE.replace('engineering comment','different comment'),'format-only'))
 def test_format_string_comment_protected(self):self.assertNotEqual(signature(BASE,'format-only'),signature(BASE.replace('"设备"','"设备2"'),'format-only'))
 def test_format_order_protected(self):self.assertNotEqual(signature(BASE,'format-only'),signature(BASE.replace('connect(u,y)','connect(y,u)'),'format-only'))
 def test_doc_allows_description(self):self.assertEqual(signature(BASE,'documentation-only'),signature(BASE.replace('"设备"','"部件"').replace('设备说明','真实新说明'),'documentation-only'))
 def test_doc_protects_visual(self):self.assertNotEqual(signature(BASE,'documentation-only'),signature(BASE.replace('lineColor={0,0,0}','lineColor={1,2,3}'),'documentation-only'))
 def test_color_protects_doc(self):self.assertNotEqual(signature(BASE,'connection-color-only'),signature(BASE.replace('设备说明','新说明'),'connection-color-only'))
 def test_color_allows_color(self):self.assertEqual(signature(BASE,'connection-color-only'),signature(BASE.replace('color={0,0,127}','color={0,0,0}'),'connection-color-only'))
 def test_color_absent_added(self):self.assertEqual(signature(BASE,'connection-color-only'),signature(BASE.replace(',color={0,0,127}',''),'connection-color-only'))
 def test_color_route_protected(self):self.assertNotEqual(signature(BASE,'connection-color-only'),signature(BASE.replace('{100,0}','{120,0}'),'connection-color-only'))
 def test_color_width_protected(self):self.assertNotEqual(signature(BASE,'connection-color-only'),signature(BASE.replace('thickness=0.5','thickness=0.6'),'connection-color-only'))
 def test_visual_allows_icon(self):self.assertEqual(signature(BASE),signature(BASE.replace('lineColor={0,0,0}','lineColor={2,3,4}')))
 def test_visual_allows_line(self):self.assertEqual(signature(BASE),signature(BASE.replace('thickness=0.5','thickness=1').replace('{100,0}','{120,0}')))
 def test_visual_allows_placement(self):self.assertEqual(signature(BASE),signature(BASE.replace('{-110,-10}','{-120,-10}')))
 def test_visual_doc_protected(self):self.assertNotEqual(signature(BASE),signature(BASE.replace('设备说明','新说明')))
 def test_visual_hide_result_protected(self):self.assertNotEqual(signature(BASE),signature(BASE.replace('HideResult=false','HideResult=true')))
 def test_visual_experiment_protected(self):self.assertNotEqual(signature(BASE),signature(BASE.replace('StopTime=10','StopTime=20')))
 def test_visual_evaluate_protected(self):self.assertNotEqual(signature(BASE),signature(BASE.replace('Evaluate=false','Evaluate=true')))
 def test_visual_causality_protected(self):self.assertNotEqual(signature(BASE),signature(BASE.replace('RealInput u','RealOutput u')))
 def test_visual_visibility_scope_protected(self):self.assertNotEqual(signature(BASE),signature(BASE.replace('    constant String','  protected\n    constant String')))
 def test_visual_business_string_protected(self):self.assertNotEqual(signature(BASE),signature(BASE.replace('data-file.csv','other.csv')))
 def test_visual_equation_protected(self):self.assertNotEqual(signature(BASE),signature(BASE.replace('connect(u,y)','connect(u,u)')))
 def test_visual_parameter_protected(self):self.assertNotEqual(signature(BASE),signature(BASE.replace('k=1','k=2')))
 def test_visual_solver_private_protected(self):
  a=BASE.replace('Evaluate=false','__OpenModelica_simulationFlags(s="dassl")');b=a.replace('dassl','euler');self.assertNotEqual(signature(a),signature(b))
 def test_aux_allows_docs_and_colors_only(self):self.assertEqual(signature(BASE,'auxiliary-only'),signature(BASE.replace('设备说明','新说明').replace('color={0,0,127}','color={1,2,3}'),'auxiliary-only'))
 def test_root_version_explicit(self):
  b=BASE.replace('version="0.8.0"','version="0.9.0"');self.assertNotEqual(signature(BASE),signature(b));self.assertEqual(signature(BASE,rv=True),signature(b,rv=True))
 def test_library_version_protected(self):self.assertNotEqual(signature(BASE,rv=True),signature(BASE.replace('4.0.0','4.1.0'),rv=True))
 def test_format_no_version_exemption(self):
  with self.assertRaises(ValueError):signature(BASE,'format-only',True)
 def test_lex_unclosed_string(self):
  with self.assertRaises(ValueError):lexical_tokens('model A "oops')
 def test_lex_unclosed_comment(self):
  with self.assertRaises(ValueError):lexical_tokens('model A /*oops')
 def test_tree_empty_not_pass(self):
  with tempfile.TemporaryDirectory() as t:
   a=Path(t)/'a';b=Path(t)/'b';a.mkdir();b.mkdir();self.assertEqual(compare_trees(a,b,'format-only')['status'],'REVIEW_REQUIRED')
 def test_tree_exact_white_list(self):
  with tempfile.TemporaryDirectory() as t:
   a=Path(t)/'a';b=Path(t)/'b';a.mkdir();b.mkdir();(a/'package.mo').write_text(BASE);(b/'package.mo').write_text(BASE)
   with self.assertRaises(ValueError):compare_trees(a,b,'documentation-only',['*.json'])

class FormattingTests(unittest.TestCase):
 def test_cleanup_idempotent(self):
  a='model A   \n\n\n  Real x;   \n\n\nequation\n  x=1;\nend A;\n';b=format_text(a);self.assertNotIn('\n\n\n',b);self.assertEqual(b,format_text(b));self.assertEqual(signature(a,'format-only'),signature(b,'format-only'))
 def test_multiline_literal_preserved(self):
  a='model A\n String s="one\n\n\n three  ";\nend A;';self.assertIn('one\n\n\n three  ',format_text(a))
 def test_multiline_comment_preserved(self):
  a='model A\n /* info\n\n\n end  */\nend A;';self.assertEqual(a,format_text(a))
 def test_new_candidate_only(self):
  with tempfile.TemporaryDirectory() as t:
   a=Path(t)/'a';a.mkdir();(a/'A.mo').write_text('model A\n\n\nend A;\n');b=Path(t)/'b';r=format_tree(a,b);self.assertEqual(r['changedFileCount'],1);self.assertIn('\n\n\n',(a/'A.mo').read_text());self.assertTrue(r['idempotent'])
 def test_nested_candidate_forbidden(self):
  with tempfile.TemporaryDirectory() as t:
   with self.assertRaises(ValueError):format_tree(Path(t),Path(t)/'child')
 def test_utf8_bom_preserved(self):
  with tempfile.TemporaryDirectory() as t:
   a=Path(t)/'a';a.mkdir();(a/'A.mo').write_bytes(b'\xef\xbb\xbfmodel A\n\n\nend A;\n');b=Path(t)/'b';format_tree(a,b);self.assertTrue((b/'A.mo').read_bytes().startswith(b'\xef\xbb\xbf'))

class NewRoleTests(unittest.TestCase):
 def r(self,text,roles):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);(p/'package.mo').write_text(text);return roles_review(p,{'roles':roles})
 def test_bu_connect_forbidden(self):self.assertIn('BU_CONNECT_FORBIDDEN',str(self.r(BASE,{'Demo.Device':'BU'})))
 def test_bu_inherited_connect(self):
  a=BASE.replace('  annotation(version=', '  model Child extends Device; end Child;\n  annotation(version=');self.assertIn('BU_CONNECT_FORBIDDEN',str(self.r(a,{'Demo.Child':'BU'})))
 def test_whitebox_equal_alias_forbidden(self):self.assertIn('WHITEBOX_BEHAVIOR_EQUATION',str(self.r(BASE.replace('connect(u,y)','y=u'),{'Demo.Device':'SB'})))
 def test_bu_without_connect(self):self.assertEqual(self.r('model B Real x; equation x=1; end B;',{'B':'BU'})['status'],'NO_LOCAL_FINDING')
 def test_unknown_type_not_silent(self):self.assertIn('DECLARATION_TYPE_UNRESOLVED',str(self.r('model B Unknown x; end B;',{'B':'BU'})))

class ConnectionTests(unittest.TestCase):
 def r(self,text):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);(p/'package.mo').write_text(text);return connections_review(p)
 def test_all_real_connections_enumerated(self):self.assertEqual(self.r(BASE)['sourceConnectCount'],1)
 def test_no_line_found(self):self.assertIn('MISSING_LINE',str(self.r(BASE.replace(' annotation(Line(points={{-100,0},{100,0}},color={0,0,127},thickness=0.5))',''))))
 def test_hidden_found(self):self.assertIn('HIDDEN_CONNECTION',str(self.r(BASE.replace('thickness=0.5','thickness=0.5,visible=false'))))
 def test_zero_width(self):self.assertIn('NONPOSITIVE_LINE_WIDTH',str(self.r(BASE.replace('thickness=0.5','thickness=0'))))
 def test_zero_length(self):self.assertIn('ZERO_LENGTH_CONNECTION',str(self.r(BASE.replace('{-100,0},{100,0}','{-100,0},{-100,0}'))))
 def test_outside_canvas(self):self.assertIn('WHOLE_LINE_OUTSIDE_DECLARED_CANVAS',str(self.r(BASE.replace('{-100,0},{100,0}','{200,0},{250,0}'))))
 def test_zero_port_size(self):self.assertIn('ZERO_SIZE_',str(self.r(BASE.replace('{-110,-10},{-90,10}','{-100,-10},{-100,10}'))))
 def test_duplicate_is_candidate(self):
  a=BASE.replace('  end Device;','  end Device;')
  line='connect(u,y) annotation(Line(points={{-100,0},{100,0}},color={0,0,127},thickness=0.5));';a=a.replace(line,line+'\n'+line);self.assertEqual(len(self.r(a)['duplicateCandidates']),1)
 def test_gui_not_claimed(self):self.assertEqual(self.r(BASE)['nativeGUI'],'NOT_CHECKED')

class PaletteTests(unittest.TestCase):
 def ix(self,pal=None,strict=True):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);p=Path(self.tmp.name)
  p.joinpath('P.mo').write_text('package P connector Bus Real value; annotation(Icon(graphics={Rectangle(extent={{-10,-10},{10,10}},fillColor={0,100,100},lineColor={0,100,100})})); end Bus; connector Heat = Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_a; end P;')
  return Index(p,reviewed_palette=pal,require_reviewed_palette=strict)
 def test_inference_not_approval(self):ix=self.ix();self.assertIn('P.Bus',ix.inferred_custom_colors);self.assertNotIn('P.Bus',ix.custom_colors)
 def test_reviewed_custom_palette(self):self.assertEqual(self.ix({'reviewed':True,'mslVersion':'4.0.0','customColors':{'P.Bus':[0,100,100]}}).custom_colors['P.Bus'],(0,100,100))
 def test_unreviewed_palette_rejected(self):
  with self.assertRaises(ValueError):self.ix({'reviewed':False,'mslVersion':'4.0.0','customColors':{}})
 def test_msl_override_rejected(self):
  with self.assertRaises(ValueError):self.ix({'reviewed':True,'mslVersion':'4.0.0','customColors':{'P.Heat':[0,100,100]}})
 def test_unsupported_version_rejected(self):
  with self.assertRaises(ValueError):self.ix({'reviewed':True,'mslVersion':'4.1.0','customColors':{}})
 def test_invalid_boolean_rgb_rejected(self):
  with self.assertRaises(ValueError):self.ix({'reviewed':True,'mslVersion':'4.0.0','customColors':{'P.Bus':[True,1,2]}})

if __name__=='__main__':unittest.main()
