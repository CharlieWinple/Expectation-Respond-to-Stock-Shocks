"""Read-only source collection and reproducible external return audit."""
from pathlib import Path
import json
import re
import sys
import requests
import pandas as pd
import numpy as np
from pypdf import PdfReader

ROOT = Path('D:/wyp_Files/xx.Files/data/CSMAR_fund_202608')
OUT = ROOT / '20260823 exp stock/outputs/fund_return_external_audit'

def download():
    OUT.mkdir(exist_ok=True)
    urls = {
        '159925_q1': 'https://www.nffund.com/main/files/2024/04/21/018383838195.pdf',
        '159925_2023': 'https://www.nffund.com/main/files/2024/03/29/234320314479.pdf',
        '159925_split': 'https://www.nffund.com/main/files/2024/01/28/135590405082.pdf',
        '110007_q1': 'https://cdn.efunds.com.cn/owch/data/bulletin/20250422/易方达稳健收益债券型证券投资基金2025年第1季度报告.pdf',
        '110007_dividend': 'https://cdn.efunds.com.cn/owch/data/bulletin/20250111/易方达稳健收益债券型证券投资基金分红公告.pdf',
    }
    for code, name in [('110022', '消费行业股票型证券投资基金'), ('159915', '创业板交易型开放式指数证券投资基金'), ('110007', '稳健收益债券型证券投资基金')]:
        urls[code] = 'https://cdn.efunds.com.cn/owch/data/bulletin/20250331/易方达' + name + '2024年年度报告.pdf'
    for code, page in [('002001', 'https://www.chinaamc.com/c/2025-03-31/10000442694.shtml'), ('000001', 'https://fund.chinaamc.com/product/publishGgList.do?fundcode=000001')]:
        r = requests.get(page, timeout=40)
        r.raise_for_status()
        r.encoding = 'utf-8'
        if code == '000001':
            link = re.search(r'href="([^"]+)"[^>]*>\s*华夏成长证券投资基金2024年年度报告', r.text)
            if not link:
                raise ValueError('Annual report link missing')
            page = requests.compat.urljoin(page, link.group(1))
            r = requests.get(page, timeout=40)
            r.raise_for_status()
            r.encoding = 'utf-8'
        links = re.findall(r'''href=["']([^"']+)["'][^>]*title=["'][^"']+\.pdf["']''', r.text, re.I)
        if not links:
            raise ValueError(f'PDF missing: {page}')
        urls[code] = requests.compat.urljoin(page, links[0])
    (OUT / 'sources.json').write_text(json.dumps(urls, ensure_ascii=False, indent=2), encoding='utf-8')
    for code, url in urls.items():
        p = OUT / (code + '.pdf')
        if p.exists() and p.read_bytes().startswith(b'%PDF'):
            continue
        r = requests.get(url, timeout=50)
        if r.status_code != 200:
            print(code, 'download failed', r.status_code, flush=True)
            continue
        p.write_bytes(r.content)
        reader = PdfReader(p)
        (OUT / (code + '.txt')).write_text('\n'.join(f'\n--- PDF PAGE {i+1} ---\n' + page.extract_text() for i, page in enumerate(reader.pages)), encoding='utf-8')
        print(code, len(reader.pages), flush=True)

def calculate():
    codes = ['110022', '000001', '110007', '110008', '159915', '159925']
    output_root = ROOT / '20260823 exp stock/outputs'
    static = pd.read_csv(output_root / 'fund_static.csv', dtype={'fund_code': str})
    meta = static.loc[static.fund_code.isin(codes), ['fund_code', 'FundClassID', 'ShortName']].drop_duplicates()
    assert not meta.fund_code.duplicated().any()
    cols = ['FundClassID', 'TradingMonth', 'TradingDate', 'StartDate', 'NAV', 'PrvNAV', 'AccumulativeNAV', 'PrvAccumulativeNAV', 'ReturnAccumulativeNAV', 'ReturnNAV']
    chunks = []
    for p in sorted(ROOT.glob('基金月净值文件*/Fund_NAV_Month*.dta')):
        for c in pd.read_stata(p, columns=cols, convert_categoricals=False, chunksize=100000):
            chunks.append(c.loc[c.FundClassID.isin(meta.FundClassID)])
    m = pd.concat(chunks).merge(meta, on='FundClassID', validate='many_to_one')
    m = m.loc[m.TradingMonth.between('2023-12', '2025-03')].sort_values(['fund_code', 'TradingMonth'])
    assert not m.duplicated(['fund_code', 'TradingMonth']).any()
    m.to_csv(OUT / 'source_monthly.csv', index=False, encoding='utf-8-sig')
    chunks = []
    for p in sorted(ROOT.glob('基金日净值文件*_2025/Fund_NAV*.dta')):
        for c in pd.read_stata(p, columns=['FundClassID', 'TradingDate', 'NAV', 'AccumulativeNAV'], convert_categoricals=False, chunksize=100000):
            chunks.append(c.loc[c.FundClassID.isin(meta.loc[meta.fund_code.isin(['110007', '110008']), 'FundClassID']) & c.TradingDate.between('2025-01-01', '2025-03-31')])
    daily = pd.concat(chunks).sort_values('TradingDate')
    assert not daily.duplicated(['FundClassID', 'TradingDate']).any()
    daily.to_csv(OUT / 'dividend_daily_source.csv', index=False, encoding='utf-8-sig')
    rows = []
    cases = [('110022','2024-01','2024-12',.043), ('000001','2024-01','2024-12',.0525), ('110007','2025-01','2025-03',.0029), ('110008','2025-01','2025-03',.0037), ('159915','2024-01','2024-12',.1398), ('159925','2024-01','2024-03',.0297)]
    for code, start, end, official in cases:
        f = m.loc[m.fund_code.eq(code) & m.TradingMonth.between(start, end)]
        first, last = f.iloc[0], f.iloc[-1]
        n0, n1, a0, a1 = first.PrvNAV, last.NAV, first.PrvAccumulativeNAV, last.AccumulativeNAV
        dividend = {'110007': .03, '110008': .038}.get(code, 0)
        exnav = daily.loc[daily.TradingDate.eq('2025-01-14') & daily.FundClassID.eq(first.FundClassID), 'NAV'].item() if dividend else np.nan
        split = .503545799 if code == '159925' else 1
        cash = (split*n1 + dividend)/n0-1
        reinvest = n1/n0*(1+dividend/exnav)-1 if dividend else cash
        rows.append(dict(fund_code=code, name=first.ShortName, start_month=start, end_month=end, nav0=n0, nav1=n1, acc0=a0, acc1=a1,
            csmar_monthly_compounded=(1+f.ReturnAccumulativeNAV).prod()-1,
            csmar_endpoint=a1/a0-1, reconstructed_endpoint=(a1-a0)/n0,
            reconstructed_monthly_compounded=(1+(f.AccumulativeNAV-f.PrvAccumulativeNAV)/f.PrvNAV).prod()-1,
            official_return=official, event_checked_cash_return=cash, event_checked_reinvest_return=reinvest,
            dividend_per_initial_share=dividend, period_share_factor=split, ex_dividend_nav=exnav if dividend else np.nan))
    result = pd.DataFrame(rows)
    result['cash_vs_official_bp'] = (result.event_checked_cash_return-result.official_return)*10000
    result['reinvest_vs_official_bp'] = (result.event_checked_reinvest_return-result.official_return)*10000
    result.to_csv(OUT / 'comparison.csv', index=False, encoding='utf-8-sig')
    result['matches_official_display_rounding'] = result.reinvest_vs_official_bp.abs() <= .5
    result.to_csv(OUT / 'comparison.csv', index=False, encoding='utf-8-sig')
    for filename in ['ctrl_monthly_total_return_v1.csv','shock_panel_total_return_v1.csv']:
        f = pd.read_csv(output_root / 'fund_total_return' / filename, dtype={'fund_code': str}, low_memory=False)
        f.loc[f.fund_code.isin(codes)].to_csv(OUT / ('released_' + filename), index=False, encoding='utf-8-sig')
    print(result.to_string(index=False))

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    if '--download' in sys.argv:
        download()
    else:
        calculate()
