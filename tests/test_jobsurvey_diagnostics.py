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

def execute(duplicate=False, malformed=False, early_excluded=False):
    calls=[]
    def read(name,cols):
        if 'jobsurvey' in name:
            wave=next(w for w in WAVES if w in name); i=WAVES.index(wave)
            d=pd.DataFrame({c:['基本不变']*8 for c in cols})
            d['user_id']=[str(k) for k in range(8)]
            d['submit_id']=[str(k) for k in range(8)]
            d['submit_date']=[ENDS[i][:8]+'21']*8
            d['user_age']=['30']*8
            if malformed: d.loc[0,'submit_date']='bad_date'
            if early_excluded:
                d.loc[0,'submit_date']=ENDS[i][:8]+'10'
                d.loc[0,'submit_id']=None
            d['extro_info']=['answerSeconds=100','answerSeconds=bad','answerSeconds=-1','answerSeconds=0','answerSeconds=60;answerSeconds=90',None,'answerSeconds=180','answerSeconds=240']
        elif 'fund_invest' in name:
            rows=[]
            for date in MONTHS+['2024-04-30','2024-07-31','2024-10-31','2025-01-31']:
                for user,code,amount in [('0','1',10000),('1','1',0),('3','1',5000),('3','2',5000),('4','1',-1),('5','1',None),('6','1',20000),('7','3',10000)]:
                    rows.append([user,code,amount,'partition_'+date.replace('-','')])
            d=pd.DataFrame(rows,columns=[USER,'基金代码',AMOUNT,'日期'])
            if duplicate:d=pd.concat([d,d.iloc[[0]]],ignore_index=True)
        elif 'shock_panel' in name:
            raise AssertionError('Supplement must not read legacy returns')
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
    assert all(len(d)==8 for d in n['UNIQUE'].values())
    assert all(d.seconds.isna().sum()==4 for d in n['UNIQUE'].values())
    assert all('gain' not in d for d in n['UNIQUE'].values())
    assert all('family' not in g for g in n['QUESTION_GROUPS'].values())
    assert not any('RAW v' in line or 'LEGACY_SME_REFERENCE' in line for line in n['REPORT'])
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
    assert set(b['BLOCKERS'])=={'2024q2 JOB lag1 snapshot/date gate'}
    assert 'gain' not in b['UNIQUE']['2024q2']
    print('PASS: supplementary-only reads, duplicate gate and report budget')

    assert len(n['WINDOWS'])==8 and len(n['CANDIDATE_PANELS'])==8
    for window in n['WINDOWS']:
        assert window['return_end'].day==20
        assert window['holding_date'].is_month_end
        assert window['return_start']==window['holding_date']+pd.Timedelta(days=1)
    for d in n['CANDIDATE_PANELS'].values():
        assert d.loc[d.capital.gt(0),'job_gain'].isna().all()
        assert d.loc[d.capital.eq(0),'job_gain'].eq(0).all()
        assert d.holding_status.eq('zero').sum()==2
    bad=execute(malformed=True)
    assert not bad['CANDIDATE_PANELS']
    assert all(not w['date_ready'] for w in bad['WINDOWS'])
    early=execute(early_excluded=True)
    assert all(w['return_end'].day==9 for w in early['WINDOWS'])
    assert all(len(d)==7 for d in early['UNIQUE'].values())
    strict=n['submit_dates'](pd.Series(['20240621','2024-06-21 12:34:56','prefix_20240621','2024-02-30']))
    assert strict.notna().tolist()==[True,True,False,False]
    print('PASS: candidate month-end windows, raw anchor before exclusions, strict dates, pending returns and zero holdings')
