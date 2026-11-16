"""Build local option dictionaries and figures from visually checked aggregate tables."""
from pathlib import Path
import ast
import json
import numpy as np
import pandas as pd
import openpyxl
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/'outputs/platform_runs/jobsurvey_diagnostics/run_11161040'
V = BASE/'verified'
OUT = ROOT/'outputs/jobsurvey_mapping'
OUT.mkdir(exist_ok=True, parents=True)
FIG = ROOT/'docs/notes/figures'
FIG.mkdir(exist_ok=True)
WAVES = ['2024q2','2024q3','2024q4','2025q1']
RAW = dict(zip(WAVES,[17749,16112,18789,16099]))
UNIQUE = dict(zip(WAVES,[17749,16112,18783,16097]))
tree = ast.parse((ROOT/'scripts/diagnostics/07_jobsurvey_diagnostics.py').read_text(encoding='utf-8'))
config = {}
for node in tree.body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target,ast.Name) and target.id in ['FIELD_MAP','LABELS','VARIABLE_GROUPS']:
                config[target.id] = ast.literal_eval(node.value)
fm, labels = config['FIELD_MAP'], config['LABELS']
reverse = {(w,c):k for k,codes in fm.items() for w,c in zip(WAVES,codes) if c}
group = {k:g for g,keys in config['VARIABLE_GROUPS'].items() for k in keys}
book = openpyxl.load_workbook(ROOT/'data/就业调研变量映射表.xlsx',read_only=True,data_only=True)
wording = {(s.title,c):q for s in book for q,c in s.values if c}
rows=[]
for filename,scope,denoms in [('option_transcription.txt','RAW',RAW),('control_option_transcription.txt','UNIQUE',UNIQUE)]:
    for line in (V/filename).read_text(encoding='utf-8').splitlines():
        if not line or line.startswith('#'): continue
        w,c,page,items=line.split(' ',3)
        options=dict((o,int(n)) for o,n in (item.rsplit('=',1) for item in items.split(';')))
        N=denoms[w]
        assert sum(options.values())==N,(w,c,sum(options.values()),N)
        nm=N-options.get('<NA>',0)
        k=reverse.get((w,c),c)
        for o,n in options.items():
            kind='缺失/跳题' if o=='<NA>' else ('不确定' if o=='不确定' else ('拒答' if o in ['不愿意透露','不便透露'] else '实质选项'))
            rows.append(dict(wave=w,variable=k,label=labels.get(k,{'user_gender':'性别代码','city_level_from_yicai':'城市等级'}.get(k,k)),field=c,scope=scope,option=o,N=n,denominator=N,nonmissing=nm,pct_all=n/N,pct_nonmissing=n/nm if o!='<NA>' else None,answer_type=kind,pdf_page=page))
options=pd.DataFrame(rows)
assert len(options[options.scope.eq('RAW')].groupby(['wave','field']))==102
options.to_csv(OUT/'jobsurvey_option_distribution.csv',index=False,encoding='utf-8-sig')
options.to_csv(V/'question_options_verified.csv',index=False,encoding='utf-8-sig')
variables=[]
for k,codes in fm.items():
    for w,c in zip(WAVES,codes):
        if not c:continue
        t=options[(options.wave==w)&(options.field==c)]
        note='保留分类；尚未指定回归数值编码。'
        if k=='unresolved_q2_v53':note='原映射表缺少题名；仅有覆盖率：非空13809、缺失3940、9个不同值。选项未输出，不能认作工作收入。'
        if k=='exp_cpi':note='原始尾部标签为“下降3_以下”；保留原文，数值尾部编码待确认。'
        if k in ['consumption_income_ratio','consumption_income_ratio_alt'] and w=='2025q1':note='v80/v126题意及六个选项一致，唯一问卷中互斥且完整覆盖；可按非空值合并。'
        if k=='education':note='拒答作为独立类别，不能当作教育程度。'
        variables.append(dict(variable=k,label=labels[k],group=group[k],wave=w,field=c,question=wording.get((w,c)) or '题名未提供',option_count=int((t.option!='<NA>').sum()) if len(t) else 9,nonmissing=int(t.nonmissing.iloc[0]) if len(t) else 13809,missing=int(t.denominator.iloc[0]-t.nonmissing.iloc[0]) if len(t) else 3940,notes=note))
variables=pd.DataFrame(variables)
variables.to_csv(OUT/'jobsurvey_variable_mapping.csv',index=False,encoding='utf-8-sig')
# Q1 unique-questionnaire complementary household responses, both visually checked.
ratio_labels=['40_以下_收入结余较多','40_60_收入结余中等','60_80_收入结余一些','80_100_收入基本花掉_略有结余','100_全部花掉','超过100_收入不够花_还需要消耗储蓄或者借钱']
q4=[4207,5198,3713,3093,865,1707]
q1a=[2495,3634,2237,1639,406,717]
q1b=[1204,1256,919,839,216,535]
assert sum(q4)==UNIQUE['2024q4'] and sum(q1a)+sum(q1b)==UNIQUE['2025q1']
ratio=pd.DataFrame({'option':ratio_labels,'2024q4_N':q4,'2025q1_v80_N':q1a,'2025q1_v126_N':q1b})
ratio['2025q1_N']=ratio['2025q1_v80_N']+ratio['2025q1_v126_N']
for w in ['2024q4','2025q1']:ratio[w+'_share']=ratio[w+'_N']/UNIQUE[w]
ratio.to_csv(OUT/'household_ratio_combined.csv',index=False,encoding='utf-8-sig')
continuous=pd.read_csv(V/'continuous_unique.csv')
continuous.to_csv(OUT/'continuous_summary.csv',index=False,encoding='utf-8-sig')
duration=pd.read_csv(V/'duration_bins_unique.csv')
for w in WAVES:assert duration[w].sum()==UNIQUE[w]
positive=np.array([6938,6035,7198,6573]);zero=np.array(list(UNIQUE.values()))-positive
loss=np.array([12,9,40,56]); usable=np.array(list(UNIQUE.values()))-loss
sample=pd.DataFrame({'wave':WAVES,'raw':list(RAW.values()),'unique':list(UNIQUE.values()),'positive':positive,'zero':zero,'gain_usable':usable,'return_coverage_loss':loss})
sample.to_csv(OUT/'sample_zero_included.csv',index=False,encoding='utf-8-sig')

# The workbook is authored separately with artifact-tool; keep the input matrix simple.
payload={
 '变量映射': [['变量','简称','用途组','wave','字段','原始题名','非空选项数','非空N','缺失N','处理说明']]+variables.values.tolist(),
 '选项分布': [['wave','变量','简称','字段','样本口径','原始选项','频数','全部N','非空N','占全部比例','占非空比例','回答类型']]+options.drop(columns='pdf_page').replace({np.nan:None}).values.tolist(),
 '连续变量': [list(continuous.columns[:-1])]+continuous.iloc[:,:-1].values.tolist(),
 '家庭消费收入比': [list(ratio.columns)]+ratio.values.tolist(),
 '使用说明': [['项目','说明'],['覆盖范围','已选34个变量、103个wave字段组合；102组已核对全部选项。Q2 v53仅有覆盖信息，未猜测题意或选项。'],['比例分母','RAW为该波原始问卷；UNIQUE为去除重复提交后的问卷。选项分布同时列占全部与占非空比例，缺失的占非空比例留空。'],['问卷选项','这是实际观察到的选项；原始映射工作簿只提供题名与字段，不能确认未出现的合法选项。'],['拒答与不确定','均是已观察到的回答，不是数值零；非空分母含拒答和不确定。'],['数值编码','本表未将区间选项直接转为中点，未为开口尾部指定数值。'],['性别','保留0/1/2原代码；未凭代码推断男女。'],['持仓','未持仓过和已清仓统一为零持仓、零passive gain；正持仓且收益覆盖不足仍为缺失。'],['家庭消费收入比','Q1 v80/v126题意及选项一致，唯一问卷互斥且完整覆盖。合并表使用唯一问卷，不能与RAW分母混用。']]
}
(OUT/'workbook_payload.json').write_text(json.dumps(payload,ensure_ascii=False,allow_nan=False),encoding='utf-8')

plt.rcParams.update({'font.family':'DejaVu Serif','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
colors=['#235789','#D17A22','#39866B','#995C91']
fig,ax=plt.subplots(1,2,figsize=(9,3.1),layout='constrained')
x=np.arange(4);zshare=100*zero/np.array(list(UNIQUE.values()))
ax[0].bar(x,zshare,color='#D9DEE4',label='Zero holdings')
ax[0].bar(x,100-zshare,bottom=zshare,color=colors[0],label='Positive holdings')
for i,p in enumerate(zshare):
    ax[0].text(i,p/2,f'{p:.1f}%',ha='center',va='center');ax[0].text(i,(p+100)/2,f'{100-p:.1f}%',ha='center',va='center',color='white')
ax[0].set(xticks=x,xticklabels=[w.upper() for w in WAVES],ylim=(0,100),ylabel='Share of unique respondents (%)',title='(a) Initial holdings')
ax[0].legend(loc='upper center',bbox_to_anchor=(.5,-.14),ncol=2,frameon=False,fontsize=8)
thresholds=[30,60,100,120,180,240,300]
for w,col in zip(WAVES,colors):
    y=[100*duration.loc[duration.right.astype(float)<=t,w].sum()/UNIQUE[w] for t in thresholds]
    ax[1].plot(thresholds,y,'o-',label=w.upper(),color=col,markersize=3)
ax[1].set(xlabel='Duration threshold (seconds)',ylabel='Share below threshold (%)',ylim=(0,75),title='(b) Answer-duration screening')
ax[1].legend(frameon=False,fontsize=8)
fig.savefig(FIG/'jobsurvey_sample_duration.pdf');plt.close(fig)

fig,ax=plt.subplots(figsize=(7,2.6),layout='constrained')
for k,col in zip(['exp_gdp','exp_cpi','exp_house','exp_stock'],colors):
    t=options[(options.variable==k)&(options.option=='不确定')].set_index('wave').loc[WAVES]
    ax.plot(x,100*t.pct_all,'o-',label={'exp_gdp':'GDP','exp_cpi':'CPI','exp_house':'House prices','exp_stock':'Stock market'}[k],color=col)
ax.set(xticks=x,xticklabels=[w.upper() for w in WAVES],ylabel='Uncertain answers (%)',ylim=(20,55))
ax.legend(frameon=False,ncol=4,loc='upper center',bbox_to_anchor=(.5,-.13));fig.savefig(FIG/'jobsurvey_uncertainty.pdf');plt.close(fig)

fig,axes=plt.subplots(1,3,figsize=(9,3.2),sharex=True,sharey=True,layout='constrained')
cs=['#A9473C','#D99375','#D8D8D8','#80B8AD','#28675C']
for ax,k,title in zip(axes,['exp_income','exp_consumption','exp_employment'],['Income','Consumption','Employment environment']):
    opts=['减少很多','减少一点','基本不变','增加一点','增加很多'] if k!='exp_employment' else ['变差很多','变差一点','基本不变','变好一点','变好很多']
    left=np.zeros(4)
    for opt,col in zip(opts,cs):
        t=options[(options.variable==k)&(options.option==opt)].set_index('wave').loc[WAVES]
        val=100*t.pct_nonmissing.to_numpy();ax.barh(x,val,left=left,color=col,height=.65)
        for i,(v,l) in enumerate(zip(val,left)):
            if v>=8:ax.text(l+v/2,i,f'{v:.0f}',ha='center',va='center',fontsize=7)
        left+=val
    ax.set(title=title,yticks=x,yticklabels=[w.upper() for w in WAVES],xlim=(0,100),xlabel='Share of nonmissing answers (%)')
axes[0].invert_yaxis()
from matplotlib.patches import Patch
fig.legend([Patch(facecolor=c) for c in cs],['Much lower / worse','Slightly lower / worse','Unchanged','Slightly higher / better','Much higher / better'],loc='outside lower center',ncol=3,frameon=False,fontsize=8)
fig.savefig(FIG/'jobsurvey_expectation_options.pdf');plt.close(fig)
print(f'Checked {len(variables)} variable-wave mappings, {len(options)} option rows; all count totals reconcile.')
print(sample.to_string(index=False));print(ratio.to_string(index=False))
