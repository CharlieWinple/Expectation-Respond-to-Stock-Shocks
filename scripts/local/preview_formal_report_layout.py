"""Build before/after previews from the actual formatters, using invented aggregates."""
import ast
import html
from pathlib import Path
import textwrap
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'outputs/report_layout_preview'


def load_formatters(path):
    names = {'report_value', 'readable_table_lines', 'unique_display_lines', 'compact_table', 'emit_selection_report'}
    tree = ast.parse(path.read_text(encoding='utf-8'))
    tree.body = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    captured = []
    env = dict(np=np, pd=pd, textwrap=textwrap, REPORT_BLOCKS=[[], [], [], []],
               OUTCOME_CODES={'exp_gdp': 'Y1', 'exp_house': 'Y2', 'exp_cpi': 'Y3'},
               TRAIT_CODES={'aer_bal_age': 'T1', 'education_category=graduate': 'T2'},
               notes_category_key=[['B1', 'aer_bal_age'], ['B2', 'education_category=graduate']],
               RUN_BLOCKERS=[], NOTES_REPORT_ERRORS=[], REPORT_CELL_BUDGET=44000,
               SCRIPT_REVISION='SYNTHETIC PREVIEW - NOT PLATFORM RESULTS',
               ant_print_all=lambda series, **kw: captured.append(list(series.unique())))
    exec(compile(tree, str(path), 'exec'), env)
    return env, captured


def array_output(calls, width):
    # Emulate Series.unique -> NumPy object-array printing, not a platform screenshot.
    with np.printoptions(linewidth=width, threshold=1000):
        return '\n\n'.join(str(np.array(call, dtype=object)) for call in calls)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cases = []
    # Invented aggregate values: useful edge cases, not estimates from real respondents.
    main_rows = [
        ['exp_gdp','W',1200,1030,.1432,.0921,.1201,-.0373,.3237,'ok'],
        ['exp_gdp','C',1200,1030,.1684,.1012,.0961,-.03,.3668,'ok'],
        ['exp_gdp','F',1200,1030,.1759,.1035,.0892,-.027,.3788,'ok'],
        ['exp_house','W',1160,997,.8214,.6612,.2141,-.4746,2.117,'ok'],
        ['exp_house','C',1160,997,1.803,.7291,.0134,.374,3.232,'ok'],
        ['exp_house','F',1160,997,1.756,.7324,.0165,.3205,3.191,'ok'],
    ]
    headers=['Y','model','N','U','beta','SE','p','CI_low','CI_high','note']
    balances = [['BASE',trait,model,1400,1200,b,se,p,b*.3,(b-1.96*se)*.3,(b+1.96*se)*.3,note]
                for trait,b,se,p,note in [('B1',.72,.31,.0202,''),('B2',0.,0.,np.nan,'degenerate_cluster_variance')]
                for model in ['Raw','Wave','Cell']]
    for label, role, tables in [
        ('04 - Main regressions','04_sme_owner_formal.py',[(
            'Main regressions: same sample per outcome',
            ['sample']+headers[:7]+['note'],
            [['Main',{'exp_gdp':'Y1','exp_house':'Y2'}[r[0]],
              {'W':'Wave','C':'Cell','F':'Owner'}[r[1]]]+r[2:7]+[r[-1]] for r in main_rows])]),
        ('05 - Selected main N1','05_sme_employee_formal.py',[(
            'Current main: Wave / Cell / Cell + employee controls',headers,main_rows)]),
        ('05 - Balance N4','05_sme_employee_formal.py',[(
            'Balance: original units and standardized estimates; all targets retained',
            ['scope','trait','model','N','U','beta','SE','p','sd_beta','sd_low','sd_high','note'],balances)])]:
        rendered=[]
        for version in ['before','after']:
            path=OUT/(role[:2]+'_before.py') if version=='before' else ROOT/'scripts/analysis'/role
            env,captured=load_formatters(path)
            if role.startswith('04'):
                title,cols,rows=tables[0]
                env['compact_table'](0,title,cols,rows)
                lines=env['REPORT_BLOCKS'][0]
                captured.append(env['unique_display_lines'](lines) if version=='after'
                                else [f'1.{i+1}|{line}' for i,line in enumerate(lines)])
            else:
                env['emit_selection_report']('N1' if 'N1' in label else 'N4',tables)
            rendered.append(array_output(captured,75 if version=='before' else 110))
        cases.append((label,*rendered))
    sections=[]
    for title,before,after in cases:
        sections.append('<section><h2>'+html.escape(title)+'</h2><div class="pair">'+
                        ''.join('<article><h3>'+label+'</h3><pre>'+html.escape(body)+'</pre></article>'
                                for label,body in [('Before',before),('After',after)])+'</div></section>')
    document='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>04 / 05 报告输出对照</title>
<style>body{font:16px system-ui;margin:32px;background:#f5f7fa;color:#172638}h1{font-size:28px}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:18px}article{background:white;border:1px solid #d7e0eb;border-radius:8px;overflow:auto}
h3{margin:0;padding:14px 18px;background:#e9eff6}pre{font:13px/1.7 Consolas,monospace;padding:18px;white-space:pre}
section{margin-top:30px}p{max-width:1000px;line-height:1.7}@media(max-width:1100px){.pair{grid-template-columns:1fr}}</style>
<h1>04 / 05：报告输出修改前后</h1><p><b>仅为本地合成展示数据，不是真实样本或平台回归结果。</b>
使用实际修改前后的格式化函数，并模拟 Series.unique 的 NumPy 文本显示。后台PDF的字体和分页仍需平台运行确认。
数值保持一致；新版用等宽空格对齐，不显示行号或竖线，表间加分隔线。
宽表重复标识列，保留系数（标准误）、星号、p值和不可用状态。</p>'''+''.join(sections)+'</html>'
    (OUT/'comparison.html').write_text(document,encoding='utf-8')
    (OUT/'before.txt').write_text('\n\n'.join(t+'\n'+b for t,b,a in cases),encoding='utf-8')
    (OUT/'after.txt').write_text('\n\n'.join(t+'\n'+a for t,b,a in cases),encoding='utf-8')
    # A static first-case preview for quick visual inspection; HTML contains all cases.
    mono=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',15)
    title_font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
    before,after=cases[0][1:]
    height=max(len(before.splitlines()),len(after.splitlines()))*23+120
    im=Image.new('RGB',(2000,height),'#f5f7fa'); draw=ImageDraw.Draw(im)
    for x,label,body in [(24,'BEFORE - SYNTHETIC',before),(1010,'AFTER - SYNTHETIC',after)]:
        draw.text((x,20),label,font=title_font,fill='#172638')
        draw.multiline_text((x,70),body,font=mono,fill='#172638',spacing=7)
    im.save(OUT/'comparison.png')
    print(OUT/'comparison.html')


if __name__=='__main__':
    main()
