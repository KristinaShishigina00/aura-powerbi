"""Check public project files and independent CSV controls, without Power BI."""
from pathlib import Path
from datetime import datetime
import csv
import hashlib
import json
import math
import re
import urllib.parse
import zipfile

ROOT = Path(__file__).resolve().parents[1]
checks = []

def check(name, value):
    checks.append((name, bool(value)))
    if not value:
        raise AssertionError(name)

tables = {}
for name in ['Users', 'Products', 'Recommendations', 'Interactions', 'Routine', 'Date', 'FunnelStages']:
    with (ROOT / 'data' / f'{name}.csv').open(encoding='utf-8-sig', newline='') as stream:
        tables[name] = list(csv.DictReader(stream))

expected_counts = dict(Users=8000, Products=120, Recommendations=60000, Interactions=127535, Routine=10638, Date=273, FunnelStages=6)
keys = dict(Users='user_id', Products='product_id', Recommendations='recommendation_id', Interactions='interaction_id', Routine='routine_id', Date='date', FunnelStages='stage_id')
for name, rows in tables.items():
    values = [x[keys[name]] for x in rows]
    check(f'{name}: row count', len(rows) == expected_counts[name])
    check(f'{name}: primary key', all(values) and len(set(values)) == len(values))

user_ids = {x['user_id'] for x in tables['Users']}
product_ids = {x['product_id'] for x in tables['Products']}
recommendation_ids = {x['recommendation_id'] for x in tables['Recommendations']}
for name in ['Recommendations', 'Interactions', 'Routine']:
    rows = tables[name]
    check(f'{name}: user references', all(x['user_id'] in user_ids for x in rows))
    check(f'{name}: product references', all(not x['product_id'] or x['product_id'] in product_ids for x in rows))
for name in ['Interactions', 'Routine']:
    check(f'{name}: recommendation references', all(not x['recommendation_id'] or x['recommendation_id'] in recommendation_ids for x in tables[name]))

recommendations = tables['Recommendations']
check('Accepted item requires view', all(int(x['accepted']) <= int(x['viewed']) for x in recommendations))
check('Compatibility range', all(0 <= int(x['compatibility_percent']) <= 100 for x in recommendations))
check('Score components', all(int(x['total_score']) == sum(int(x[k]) for k in ['ingredient_function_fit', 'skin_state_fit', 'evidence_quality', 'safety_fit', 'metadata_confirmation']) for x in recommendations))
check('View chronology', all(not x['first_view_at'] or x['recommendation_date'] <= x['first_view_at'] for x in recommendations))
check('Acceptance chronology', all(not x['first_added_at'] or x['first_view_at'] and x['first_view_at'] <= x['first_added_at'] for x in recommendations))
check('Synthetic data labels', all(x.get('data_origin') == 'Synthetic / Demo Data' for n in ['Users', 'Products', 'Recommendations', 'Interactions', 'Routine'] for x in tables[n]))

expected = json.loads((ROOT / 'docs/control-values.json').read_text('utf-8'))
actual = {
    'users': len(tables['Users']),
    'products': len(tables['Products']),
    'recommendations': len(recommendations),
    'completed': sum(int(x['profile_completed']) for x in tables['Users']),
    'routine_users': sum(int(x['has_routine']) for x in tables['Users']),
    'viewed_items': sum(int(x['viewed']) for x in recommendations),
    'accepted_items': sum(int(x['accepted']) for x in recommendations),
    'active_users': len({x['user_id'] for x in tables['Interactions'] if x['interaction_type'] == 'viewed'}),
    'avg_score': sum(int(x['compatibility_percent']) for x in recommendations) / len(recommendations),
    'funnel': [sum(int(x['funnel_level']) >= stage for x in tables['Users']) for stage in range(1, 7)]
}
for name, value in actual.items():
    check(f'Control: {name}', math.isclose(value, expected[name], abs_tol=1e-10) if isinstance(value, float) else value == expected[name])

for source in ROOT.rglob('*.md'):
    text = source.read_text('utf-8-sig')
    check(f'{source.relative_to(ROOT)}: fences', text.count('```') % 2 == 0)
    check(f'{source.relative_to(ROOT)}: disclosure tags', text.count('<details>') == text.count('</details>'))
    for target in re.findall(r'!?\[[^\]\n]*\]\(([^\s)]+)(?:\s+[^)]*)?\)', text):
        target = target.strip('<>')
        parsed = urllib.parse.urlsplit(target)
        if parsed.scheme or target.startswith('#'):
            continue
        dest = source.parent / urllib.parse.unquote(parsed.path)
        check(f'{source.relative_to(ROOT)}: link {target}', dest.exists())

with zipfile.ZipFile(ROOT / 'powerbi/Aura_PBIP_Source.zip') as archive:
    check('PBIP ZIP integrity', archive.testzip() is None)
    paths = set(archive.namelist())
    check('PBIP excludes local caches', not any('/.pbi/' in n for n in paths))
    project = json.loads(archive.read('Aura_Business_Analytics.pbip'))
    report_path = project['artifacts'][0]['report']['path']
    definition = json.loads(archive.read(f'{report_path}/definition.pbir'))
    check('PBIP model reference', definition['datasetReference']['byPath']['path'] == '../Aura.SemanticModel')
    model = json.loads(archive.read('Aura.SemanticModel/model.bim'))['model']
    measures = [m for table in model['tables'] for m in table.get('measures', [])]
    check('24 DAX measures', len(measures) == 24)
    check('Five report pages', len(json.loads(archive.read(f'{report_path}/definition/pages/pages.json'))['pageOrder']) == 5)
    check('Embedded query sources', all('File.Contents(' not in json.dumps(t.get('partitions', [])) for t in model['tables']))

with zipfile.ZipFile(ROOT / 'powerbi/Aura_Business_Analytics.pbix') as archive:
    check('PBIX integrity', archive.testzip() is None)
    check('PBIX data model', archive.getinfo('DataModel').file_size > 1_000_000)
    pages = [n for n in archive.namelist() if re.fullmatch(r'Report/definition/pages/[^/]+/page.json', n)]
    check('PBIX five pages', len(pages) == 5)

site = (ROOT / 'site/index.html').read_text('utf-8')
check('Five interactive tabs', len(re.findall(r'<button[^>]+data-tab=', site)) == 5)
check('Four filter controls', len(re.findall(r'<select\b', site)) == 4)
for source in (ROOT / 'site').glob('*.html'):
    text = source.read_text('utf-8')
    for target in re.findall(r'(?:href|src)=["\']([^"\']+)["\']', text):
        parsed = urllib.parse.urlsplit(target)
        if not parsed.scheme and not target.startswith('#'):
            check(f'{source.name}: asset {target}', (source.parent / parsed.path).exists())

for source in ROOT.rglob('*'):
    if source.is_file():
        check(f'{source.relative_to(ROOT)}: browser upload size', source.stat().st_size < 25_000_000)

manifest_path = ROOT / 'docs/file-manifest.json'
if manifest_path.exists():
    for entry in json.loads(manifest_path.read_text('utf-8'))['files']:
        source = ROOT / entry['path']
        check(f"Manifest: {entry['path']}", source.exists() and hashlib.sha256(source.read_bytes()).hexdigest() == entry['sha256'])

print(json.dumps({'checks_passed': len(checks), 'csv_controls': actual, 'native_dax_execution': 'not_run_by_this_script'}, ensure_ascii=False, indent=2))
