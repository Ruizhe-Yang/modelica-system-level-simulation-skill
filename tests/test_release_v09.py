"""Release metadata and command-line integration tests; no Modelica engine."""
from pathlib import Path
import collections, json, re, subprocess, sys, tempfile, unittest

ROOT=Path(__file__).resolve().parents[1]

def run(name,*args):
    return subprocess.run([sys.executable,str(ROOT/'scripts'/name),*map(str,args)],text=True,capture_output=True,timeout=20)

class ReleaseDataTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((ROOT/'assets/rules.json').read_text(encoding='utf-8'))
        self.mapping=json.loads((ROOT/'assets/latest_requirements.json').read_text(encoding='utf-8'))
    def test_main_rule_ids(self):
        self.assertEqual([r['id'] for r in self.data['rules']],[f'M{i:02d}' for i in range(1,37)])
    def test_main_levels(self):
        self.assertEqual(collections.Counter(r['grade'] for r in self.data['rules']),{'R':26,'S':9,'F':1})
    def test_source_mapping_complete(self):
        wanted=[f'U-{s}{i:02d}' for s,n in [('A',4),('B',6),('C',4),('D',5),('E',4),('F',4),('G',4),('H',5)] for i in range(1,n+1)]
        self.assertEqual([r['id'] for r in self.mapping['requirements']],wanted)
    def test_source_mapping_targets(self):
        ids={r['id'] for r in self.data['rules']}
        for r in self.mapping['requirements']:
            self.assertIn(r['grade'],('R','S','F'));self.assertTrue(set([r['primaryRule']]+r['relatedRules'])<=ids)
            self.assertTrue(r['sourceText']);self.assertTrue(r['integration'])
    def test_readable_standard_complete(self):
        text=(ROOT/'references/standard.md').read_text(encoding='utf-8')
        for r in self.data['rules']:
            self.assertIn(r['text'],text);self.assertIn(r['check'],text)
    def test_versions(self):
        self.assertEqual(self.data['version'],'0.9.0')
        text=(ROOT/'SKILL.md').read_text(encoding='utf-8')
        self.assertIn('version: "0.9.0"',text);self.assertIn('standard: "MOSAIC v0.9"',text)
        self.assertIn('# MOSAIC-skill v0.9',(ROOT/'README.md').read_text(encoding='utf-8'))
    def test_templates_not_execution_proof(self):
        project=json.loads((ROOT/'assets/project_contract.json').read_text(encoding='utf-8'))
        profile=json.loads((ROOT/'assets/authoring_profile.json').read_text(encoding='utf-8'))
        colors=json.loads((ROOT/'assets/connector_palette.json').read_text(encoding='utf-8'))
        self.assertEqual(project['mode'],'AUDIT');self.assertEqual(project['allowedChanges'],[])
        self.assertEqual(project['currentExecution'],'NOT_RUN');self.assertFalse(project['finalRegression']['required'])
        self.assertFalse(profile['enabled']);self.assertFalse(colors['reviewed'])
    def test_skill_relative_links(self):
        text=(ROOT/'SKILL.md').read_text(encoding='utf-8')
        for target in re.findall(r'\]\(([^)]+)\)',text):
            if '://' in target or target.startswith('#'):continue
            self.assertTrue((ROOT/target.split('#')[0]).is_file(),target)

class CommandLineTests(unittest.TestCase):
    def test_formatter_then_scope(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);src=p/'src';src.mkdir();(src/'Cell.mo').write_text('within;\nmodel Cell\n\n\n  parameter Real capacity=1;  \nend Cell;\n',encoding='utf-8')
            result=run('format_modelica.py',src,p/'candidate','--report',p/'format.json')
            self.assertEqual(result.returncode,0,result.stderr)
            result=run('verify_change_scope.py',src,p/'candidate','--mode','format-only','--output',p/'diff.json')
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads((p/'diff.json').read_text())['status'],'STATIC_SCOPE_MATCH')
    def test_connections_missing_line_reported(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);src=p/'src';src.mkdir();(src/'P.mo').write_text('model P\n Modelica.Blocks.Interfaces.RealInput u;\n Modelica.Blocks.Interfaces.RealOutput y;\nequation\nconnect(u,y);\nend P;',encoding='utf-8')
            result=run('audit_connections.py',src,'--output',p/'audit.json')
            self.assertTrue((p/'audit.json').is_file(),result.stderr)
            self.assertIn('MISSING_LINE',(p/'audit.json').read_text());self.assertNotEqual(result.returncode,0)
    def test_color_write_requires_explicit_version(self):
        with tempfile.TemporaryDirectory() as d:
            result=run('connection_colors.py',d,'--apply','--report',Path(d)/'colors.json')
            self.assertNotEqual(result.returncode,0);self.assertIn('--msl-version',result.stderr)
    def test_formatter_rejects_existing_candidate(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);src=p/'src';src.mkdir();(src/'P.mo').write_text('model P end P;',encoding='utf-8');candidate=p/'dst';candidate.mkdir()
            result=run('format_modelica.py',src,candidate,'--report',p/'report.json')
            self.assertNotEqual(result.returncode,0);self.assertTrue((src/'P.mo').exists())

if __name__=='__main__':unittest.main()
