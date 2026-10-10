from pathlib import Path
import unittest,sys,tempfile,json
S=Path(__file__).resolve().parents[1]/'scripts';sys.path.insert(0,str(S))
from modelica_support import Source,apply
from auxiliary_metadata import clean_documentation_html,concise_class_comment
from connection_colors import Index,all_connections,canonical_with_connection_colors,apply_reviewed_palette,msl_kind
from documentation_support import enrich_generated
from verify_aux_only import compare
WIRE='''within;
package Example
 connector DerivedHeat
  extends Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_a;
  annotation(Icon(graphics={Rectangle(extent={{-10,-10},{10,10}},lineColor={128,0,128},fillColor={128,0,128})}));
 end DerivedHeat;
 connector DataBundle
  Modelica.Blocks.Interfaces.RealInput value;
  annotation(Icon(graphics={Rectangle(extent={{-10,-10},{10,10}},lineColor={0,100,100},fillColor={0,100,100})}));
 end DataBundle;
 model Plant
  DerivedHeat a;
  Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_b b;
  DataBundle x;
  DataBundle y;
  Modelica.Blocks.Interfaces.RealOutput r;
 equation
  connect(a,b) annotation(Line(points={{0,0},{20,0}},color={128,0,128},thickness=0.5));
  connect(x,y) annotation(Line(points={{0,20},{20,20}},color={0,100,100}));
  connect(r,x.value) annotation(Line(points={{0,40},{20,40}},color={0,100,100}));
  annotation(Icon(graphics={Line(points={{-10,0},{10,0}},color={0,100,100})}),Documentation(info="connect(fake,a)"));
 end Plant;
end Example;
'''
class AuxiliaryTests(unittest.TestCase):
 def test_clean_preserves_limit(self):
  x='<html><h2>设备</h2><h3>连接与责任</h3><pre>connect(a,b);</pre><h3>配置</h3><p>x=1</p><h3>仿真后如何查看</h3><p>通用话术</p><h3>使用边界</h3><p>不建反流。</p><p><small>Documentation 辅助更新 1；旧话术</small></p></html>'
  y,c=clean_documentation_html(x);self.assertEqual(c,{'connection_section':1,'result_howto_section':1,'auxiliary_boilerplate':1});self.assertIn('<h3>使用边界</h3><p>不建反流。</p>',y);self.assertIn('x=1',y);self.assertNotIn('通用话术',y);self.assertEqual(clean_documentation_html(y)[0],y)
 def test_clean_end_of_html(self):
  x='<html><h3>用途</h3><p>设备</p><h3>仿真后如何查看</h3><p>重复</p></html>';self.assertEqual(clean_documentation_html(x)[0],'<html><h3>用途</h3><p>设备</p></html>')
 def test_name_once(self):self.assertEqual(concise_class_comment('CompleteMission','CompleteMission（完整任务仿真）'),'完整任务仿真')
 def test_no_translation_guess(self):
  with self.assertRaises(ValueError):concise_class_comment('Device','Device')
 def test_explicit_chinese_catalog(self):
  x='model Device "Device（设备）" Real y; equation y=1; end Device;';c={'rename_descriptions':True,'class_comment_style':'chinese-purpose-only','classes':{'Device':{'title':'设备','summary':'输出常数','declaration_description':'Device（设备）'}}};y=enrich_generated(x,catalog=c);self.assertEqual(Source(y).classes[0].description,'设备');self.assertNotIn('仿真后如何查看',y);self.assertNotIn('Documentation 辅助更新',y)
 def test_connections_not_doc_strings(self):self.assertEqual(len(list(all_connections(Source(WIRE)))),3)
 def test_derived_and_bundle_members(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);(p/'package.mo').write_text(WIRE);ix=Index(p);rs,es=ix.inspect();self.assertEqual([tuple(r['target_color']) for r in rs],[(191,0,0),(0,100,100),(0,0,127)]);self.assertEqual(len(es[p/'package.mo']),2)
 def test_color_only_mask(self):
  b=WIRE.replace('color={128,0,128},thickness','color={191,0,0},thickness');self.assertEqual(canonical_with_connection_colors(WIRE),canonical_with_connection_colors(b));self.assertNotEqual(Source(WIRE).canonical(),Source(b).canonical())
 def test_icon_protected(self):
  b=WIRE.replace('lineColor={128,0,128}','lineColor={191,0,0}');self.assertNotEqual(canonical_with_connection_colors(WIRE),canonical_with_connection_colors(b))
 def test_diagram_art_line_protected(self):
  b=WIRE.replace('points={{-10,0},{10,0}},color={0,100,100}','points={{-10,0},{10,0}},color={0,0,0}');self.assertNotEqual(canonical_with_connection_colors(WIRE),canonical_with_connection_colors(b))
 def test_route_protected(self):self.assertNotEqual(canonical_with_connection_colors(WIRE),canonical_with_connection_colors(WIRE.replace('{{0,0},{20,0}}','{{0,0},{30,0}}')))
 def test_width_protected(self):self.assertNotEqual(canonical_with_connection_colors(WIRE),canonical_with_connection_colors(WIRE.replace('thickness=0.5','thickness=0.6')))
 def test_endpoint_protected(self):self.assertNotEqual(canonical_with_connection_colors(WIRE),canonical_with_connection_colors(WIRE.replace('connect(a,b)','connect(a,a)')))
 def test_optional_compare_flag(self):
  with tempfile.TemporaryDirectory() as td:
   a=Path(td)/'a';b=Path(td)/'b';a.mkdir();b.mkdir();(a/'package.mo').write_text(WIRE);(b/'package.mo').write_text(WIRE.replace('color={128,0,128},thickness','color={191,0,0},thickness'));self.assertEqual(compare(a,b,[])['status'],'REVIEW_REQUIRED');self.assertEqual(compare(a,b,[],connection_colors=True)['status'],'STATIC_AUXILIARY_ONLY')
 def test_reviewed_generator_palette(self):
  pal={'Example.Plant':{'a | b':[191,0,0],'x | y':[0,100,100],'r | x.value':[0,0,127]}};b=apply_reviewed_palette(WIRE,pal);self.assertEqual(b,apply_reviewed_palette(b,pal));self.assertEqual(canonical_with_connection_colors(WIRE),canonical_with_connection_colors(b))
 def test_palette_changed_topology_blocked(self):
  with self.assertRaises(ValueError):apply_reviewed_palette(WIRE,{'Example.Plant':{}})
 def test_unknown_is_not_pass(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);(p/'package.mo').write_text(WIRE.replace('DerivedHeat a;','UnknownConnector a;'));rs,_=Index(p).inspect();self.assertEqual(rs[0]['status'],'UNRESOLVED')
 def test_empty_tree_is_not_pass(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);(p/'a').mkdir();(p/'b').mkdir();self.assertEqual(compare(p/'a',p/'b',[])['status'],'REVIEW_REQUIRED')
 def test_integer_boolean_families(self):self.assertEqual(msl_kind('Modelica.Blocks.Interfaces.BooleanInput'),'BOOLEAN');self.assertEqual(msl_kind('Modelica.Blocks.Interfaces.IntegerOutput'),'INTEGER')
 def test_duplicate_root_version_metadata_only(self):
  a='package Example annotation(version="1",uses(Modelica(version="4.0.0")),version="2"); end Example;';b='package Example annotation(uses(Modelica(version="4.0.0")),version="3"); end Example;';self.assertEqual(Source(a).canonical(True),Source(b).canonical(True));self.assertNotEqual(Source(a).canonical(False),Source(b).canonical(False))
if __name__=='__main__':unittest.main()
