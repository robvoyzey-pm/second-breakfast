#!/usr/bin/env python3
"""
Second Breakfast — canonical build script.
Always run this. Never patch the output file directly.
Usage: python3 build-v2.py
"""
import re, sys, subprocess

src_path = '/home/claude/second-breakfast-source.html'
out_path = '/home/claude/second-breakfast.html'
js_check = '/tmp/sb-syntax.js'

s = open(src_path).read()
errors = []

def apply(label, old, new):
    global s
    if old not in s:
        errors.append(f'FAIL: {label}')
        return
    s = s.replace(old, new)
    print(f'  OK  {label}')

print('Applying fixes...')

# FIX 1: Restore budget-card display on renderBudget entry
apply('budget-card display reset on entry',
    "function renderBudget(){var t=cfg.budgetType||'weekly';var html='';",
    "function renderBudget(){document.getElementById('budget-card').style.display='';var t=cfg.budgetType||'weekly';var html='';")

# FIX 2: Hide widget for no-budget users
apply('no-budget widget hidden',
    "else{var tot=0;for(var i=0;i<exps.length;i++)tot+=exps[i].aud;"
    "var days=Math.max(1,Math.round((new Date(today())-new Date(cfg.tripStart))/864e5)+1);"
    "var attributed=attributedToDate(today());var dailyAvg=attributed/days;"
    "var sub='Day '+days+(cfg.tripDays>0?' of '+cfg.tripDays:'');"
    "if(dailyAvg>0)sub+=(' \xb7 '+fH(dailyAvg)+'/day');"
    "html='<div class=\"bwk\">Accounted for</div>'"
    "+'<div class=\"brow\"><div><div class=\"bamt\">'+sub+'</div></div></div>';"
    "}document.getElementById('budget-card').innerHTML=html;}",
    "else{document.getElementById('budget-card').style.display='none';return;}"
    "document.getElementById('budget-card').innerHTML=html;}")

# FIX 3: Daily chart - widen columns for large values
apply('daily chart column width 30->36px',
    '.dbc{display:flex;flex-direction:column;align-items:center;flex-shrink:0;width:30px;cursor:pointer}',
    '.dbc{display:flex;flex-direction:column;align-items:center;flex-shrink:0;width:36px;cursor:pointer}')

apply('daily chart bar width 20->24px',
    '.dbb{width:20px;border-radius:4px 4px 0 0;min-height:2px;transition:height .4s ease}',
    '.dbb{width:24px;border-radius:4px 4px 0 0;min-height:2px;transition:height .4s ease}')

apply('daily chart label font size',
    '.dbl{font-size:.5rem;color:var(--ink3);margin-top:4px;text-align:center;line-height:1.3}',
    '.dbl{font-size:.48rem;color:var(--ink3);margin-top:4px;text-align:center;line-height:1.3;overflow:hidden}')

# FIX 4: Daily chart container - clip vertical overflow only, keep horizontal scroll
apply('daily chart vertical clip only',
    '.dcwrap{overflow-x:auto;scrollbar-width:none;padding-bottom:4px}',
    '.dcwrap{overflow-x:auto;overflow-y:hidden;scrollbar-width:none;padding-bottom:4px}')

# FIX 5: Fix scroll offset to match wider bar columns (36px bar + 3px gap = 39px)
apply('daily chart scroll offset matches bar width',
    'c.parentElement.scrollLeft=Math.max(0,(idx-8)*33)',
    'c.parentElement.scrollLeft=Math.max(0,(idx-8)*39)')


# FIX 6: avg/day — simple total spend divided by days on trip
apply('avg/day uses total spend not attributedToDate',
    "var attributed=attributedToDate(t);var dailyAvg=attributed/days;",
    "var dailyAvg=tot/days;")

# VERSION
apply('version 3.0->3.3', "APP_VERSION='3.0'", "APP_VERSION='3.3'")

if errors:
    print('\n'.join(errors))
    sys.exit(1)

open(out_path, 'w').write(s)
print(f'\nWritten: {out_path}')

# SYNTAX CHECK
scripts = re.findall(r'<script(?![^>]*src)[^>]*>(.*?)</script>', s, re.DOTALL)
open(js_check, 'w').write(scripts[-1])
r = subprocess.run(['node', '--check', js_check], capture_output=True, text=True)
if r.returncode != 0:
    print('SYNTAX ERROR:\n' + r.stderr)
    sys.exit(1)
print('Syntax: OK\n')

# AUDIT
checks = [
    ('Spread: dailyAud',              'function dailyAud(e,d){'),
    ('Spread: dailyAudForWeek',       'function dailyAudForWeek(e,wn){'),
    ('Spread: attributedToDate',      'function attributedToDate(d){'),
    ('No-budget: widget hidden',      "style.display='none';return;"),
    ('No-budget: display reset',      "getElementById('budget-card').style.display='';"),
    ('Stat3: trip total label',       'trip total</div>'),
    ('Stat3: set a limit hint',       'set a limit'),
    ('Stat3: Day X of Y',             "cfg.tripDays>0?' of '+cfg.tripDays"),
    ('Widget: wPaceLine',             'wPaceLine'),
    ('Widget: mPaceLine',             'mPaceLine'),
    ('Widget: at this pace',          'at this pace, lasts to'),
    ('Widget: pot willRunOut',        'willRunOut'),
    ('Chart: wider columns',          'width:36px'),
    ('Chart: vertical clip',          'overflow-y:hidden'),
    ('Chart: scroll offset fixed',    '(idx-8)*39'),
    ('Avg/day: simple calculation',   'var dailyAvg=tot/days;'),
    ('Service worker',                'serviceWorker'),
    ('GoatCounter',                   'goatcounter'),
    ('Rob uid filtered',              'usr_6j2atr'),
    ('rateUpdated',                   'rateUpdated'),
    ('catOverrides',                  'catOverrides'),
    ('cfg restore',                   'if(d.cfg)'),
    ('Version 3.3',                   "APP_VERSION='3.3'"),
]

print('Audit:')
all_pass = True
for label, needle in checks:
    ok = needle in s
    print(f"  {'OK  ' if ok else 'FAIL'} {label}")
    if not ok: all_pass = False

print()
if all_pass:
    print('All checks passed. Ready to ship.')
else:
    print('BUILD FAILED — do not ship.')
    sys.exit(1)

# FIX: This section appended — run build-v2.py to apply
