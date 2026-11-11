"""Synthetic end-to-end checks; no platform data required."""
import runpy
import sys
import types
from pathlib import Path
import pandas as pd
import numpy as np

SCRIPT=Path(__file__).resolve().parents[1]/'scripts/diagnostics/07_jobsurvey_diagnostics.py'
WAVES=['2024q2','2024q3','2024q4','2025q1']
MONTHS=['2024-05-31','2024-08-31','2024-11-30','2025-02-28']
STARTS=['2024-06-01','2024-09-01','2024-12-01','2025-03-01']
ENDS=['2024-06-20','2024-09-20','2024-12-20','2025-03-20']
USER='匿名化用户id'
AMOUNT='当月月底日持有金额元'

def execute(duplicate=False):
    calls=[]
    def read(name,cols):
        if 'jobsurvey' in name:
            wave=next(w for w in WAVES if w in name); i=WAVES.index(wave)
            d=pd.DataFrame({c:['基本不变']*8 for c in cols})
            d['user_id']=[str(k) for k in range(8)]
            d['submit_id']=[str(k) for k in range(8)]
            d['submit_date']=[ENDS[i][:8]+'21']*8
            d['user_age']=['30']*8
            d['extro_info']=['answerSeconds=100','answerSeconds=bad','answerSeconds=-1','answerSeconds=0','answerSeconds=60;answerSeconds=90',None,'answerSeconds=180','answerSeconds=240']
        elif 'fund_invest' in name:
            rows=[]
            for date in MONTHS:
                for user,code,amount in [('0','1',10000),('1','1',0),('3','1',5000),('3','2',5000),('4','1',-1),('5','1',None),('6','1',20000),('7','3',10000)]:
                    rows.append([user,code,amount,'partition_'+date.replace('-','')])
            d=pd.DataFrame(rows,columns=[USER,'基金代码',AMOUNT,'日期'])
            if duplicate:d=pd.concat([d,d.iloc[[0]]],ignore_index=True)
        elif 'shock_panel' in name:
            rows=[]
            for w,start,end in zip(WAVES,STARTS,ENDS):
                for code,r in [('000001',10),('000003',-5)]:rows.append([code,w,r,1,start,end,'nav_price_annotated_v1'])
            d=pd.DataFrame(rows,columns=['fund_code','wave','shock_ret_rate_pp','shock_usable','window_start','window_end','return_version'])
        else:
            d=pd.DataFrame({USER:[str(k) for k in range(8)],'性别':['男']*8,'风险等级':['低']*8})
        return d[cols].copy()
    def output(data,**kw):
        assert len(data)<=41
        assert len(data)==len(set(data))
        calls.append(data)
    m=types.ModuleType('marvel.AntPrint');m.ant_read_data=read;m.ant_print_all=output
    sys.modules['marvel']=types.ModuleType('marvel');sys.modules['marvel.AntPrint']=m
    result=runpy.run_path(str(SCRIPT))
    assert len(result['PAGES'])<=result['REPORT_CELLS']
    assert len(result['EMITTED_PAGES'])==len(result['PAGES'])
    assert all(b<=result['REPORT_CELL_BUDGET'] for b in result['REPORT_BYTES'])
    assert [line for page in result['PAGES'] for line in page]==result['REPORT']
    return result

if __name__=='__main__':
    n=execute()
    assert not n['BLOCKERS']
    assert {w:len(m) for w,m in n['MAP'].items()}==dict(zip(WAVES,[28,23,26,26]))
    for w,m in n['MAP'].items():
        assert all(c in m for c in n['TARGETS'][w])
        assert not any(c in m for c in ['v43','v44','v45','v46','v47','v48'])
        assert {'v1','v2','v3','v4','v7','v8','v9','v10','v29','v62','v27'}<=set(m)
    assert 'v53' not in n['TARGETS']['2024q2']
    assert 'v53' in n['TARGETS']['2024q3']
    assert {'v100','v101','v102','v103','v104'}<=set(n['MAP']['2024q2'])
    assert 'v91' in n['MAP']['2024q4']
    assert {'v80','v81','v87','v126'}<=set(n['MAP']['2025q1'])
    assert 'v136' not in n['MAP']['2024q3']
    assert 'v84' not in n['MAP']['2024q3']
    assert 'v101' not in n['MAP']['2024q4']
    assert any('consumption income ratio source audit' in line for line in n['REPORT'])
    for d in n['UNIQUE'].values():
        g=d.set_index('user_id')
        assert np.isclose(g.loc['0','gain'],.1) # 10000 yuan * 10% = 1000 yuan = .1 wan
        assert g.loc['1','gain']==0
        assert pd.isna(g.loc['2','gain']) and g.loc['2','holding_status']=='unmatched'
        assert g.loc['3','coverage']==.5 and pd.isna(g.loc['3','gain'])
        assert pd.isna(g.loc['4','capital']) and pd.isna(g.loc['5','gain'])
        assert np.isclose(g.loc['7','gain'],-.05)
        assert g.seconds.isna().sum()==4
    # Stress byte boundaries, duplicate rows, multilingual options, and continuation.
    stress=['重复中文选项 '+str(i%3)+' '+'长文本'*80 for i in range(1200)]
    blocks,budgets,errors=n['prepare_report'](stress)
    assert not errors and len(blocks)>8
    assert [line for block in blocks for call in block for line in call[1:]]==stress
    assert all(b<=44000 for b in budgets)
    assert all(len(call)<=41 and len(call)==len(set(call)) for block in blocks for call in block)
    _,_,errors=n['prepare_report'](['超'*20000])
    assert errors
    print('Normal report blocks:',len(n['PAGES']),'; max budget:',max(n['REPORT_BYTES']))
    b=execute(True)
    assert b['BLOCKERS']==['2024q2 exposure input gate']
    assert 'gain' not in b['UNIQUE']['2024q2']
    print('PASS: selected question scope and four-wave full workflow; gain units/sign, zero/unmatched/invalid, coverage, duration, duplicate gate and report budget')
