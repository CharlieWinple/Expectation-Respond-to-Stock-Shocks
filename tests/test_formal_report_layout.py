"""Report-only checks: significance boundaries, panels and aggregate preservation."""
import ast
import re
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/local'))
from preview_formal_report_layout import load_formatters


def test_layout():
    helpers=[]
    for name in ['04_sme_owner_formal.py','05_sme_employee_formal.py']:
        path=ROOT/'scripts/analysis'/name
        env,_=load_formatters(path)
        tree=ast.parse(path.read_text(encoding='utf-8'))
        helpers.append(ast.dump(next(n for n in tree.body if isinstance(n,ast.FunctionDef)
                                     and n.name=='readable_table_lines')))
        rows=[['exp_gdp','F',200,180,b,.123,p,'ok']
              for b,p in [(0.,.10),(-.01,.05),(.02,.01),(.03,.009),(1e-9,np.nan)]]
        lines=env['readable_table_lines']('Synthetic regression',
            ['Y','model','N','U','beta','SE','p','note'],rows)
        text='\n'.join(lines)
        for exact in ['0 (0.123)','-0.01* (0.123)','0.02** (0.123)',
                      '0.03*** (0.123)','1e-09 (0.123)','NA','Controls','exp_gdp']:
            assert exact in text,exact
        assert all(len(line)<=96 for line in lines)
        # Every unique value must survive the wide-table pagination. Repeated
        # identical input rows also remain distinct, with stable row numbers.
        columns=['key']+['field'+str(i) for i in range(15)]
        values=[['ROW'+str(i)]+[str(i)+'x'+str(j) for j in range(15)] for i in range(23)]
        rendered=env['readable_table_lines']('Wide accounting',columns,values)
        assert sum('Wide accounting' in line for line in rendered)>3
        assert all('|' not in line and '\t' not in line for line in rendered)
        tokens=[part.strip() for line in rendered for part in re.split(r'\s{3,}',line)]
        assert all(v in tokens for row in values for v in row)
        assert values[0][0]=='ROW0', 'Formatter must not mutate its inputs'
        repeated=['same data']*85
        displayed=env['unique_display_lines'](repeated,40)
        assert [s.rstrip() for s in displayed]==repeated
        assert all(len(set(displayed[i:i+40]))==len(displayed[i:i+40]) for i in range(0,85,40))
        decoded='\n'.join(env['readable_table_lines']('Balance',['trait','N'],[['B1',100]],{'B1':'aer_bal_age'}))
        assert 'Age' in decoded and 'B1' not in decoded
    assert helpers[0]==helpers[1], 'Standalone platform copies must stay identical'


if __name__=='__main__':
    test_layout()
    print('PASS: report precision, star boundaries, unavailable p, all wide-table fields and shared layout')
