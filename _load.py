from datetime import datetime
import dart_fss as dart
import pandas as pd
import numpy as np
import requests
from io import BytesIO


api_key = ''
dart.set_api_key(api_key=api_key)
corp_list = dart.get_corp_list()


def get_code_info():
    query_str_parms = {
        'locale': 'ko_KR',
        'mktId': 'ALL',
        'share': '1',
        'csvxls_isNo': 'false',
        'name': 'fileDown',
        'url': 'dbms/MDC/STAT/standard/MDCSTAT01901'
        }
    headers = {
        'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0'
        }
    r = requests.get('http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd', query_str_parms, headers=headers)
    form_data = {
        'code': r.content
        }
    r = requests.post('http://data.krx.co.kr/comm/fileDn/download_excel/download.cmd', form_data, headers=headers)
    df = pd.read_excel(BytesIO(r.content)).rename(columns = {'단축코드':'Code','한글 종목약명':'Name'})
    return df

def free_capital_inc(start_date, code) :
    reports_key = corp_list.find_by_stock_code(code).search_filings(bgn_de=start_date, pblntf_detail_ty='B001')
    cnt = reports_key.total_page
    df = pd.DataFrame(columns=['stddate', 'code', 'name', 'mkt', 'gubun','site'])
    for n in range(1, cnt+1):
        reports_key = corp_list.find_by_stock_code(code).search_filings(bgn_de=start_date, pblntf_detail_ty='B001', page_no=n)
        for i in range(0, len(reports_key)):
            dict_temp = reports_key[i].to_dict()
            if ('무상증자' in dict_temp['report_nm']) and ('[첨부정정]' not in dict_temp['report_nm']) and ('[기재정정]' not in dict_temp['report_nm'])\
                    and ('자회사의 주요경영사항' not in dict_temp['report_nm']):
                stddate = datetime.strftime(datetime.strptime(dict_temp['rcept_dt'], "%Y%m%d"), "%Y-%m-%d")
                name = dict_temp['corp_name']
                stock_code = dict_temp['stock_code']
                mkt = np.where(dict_temp['corp_cls'] == 'Y', 'KOSPI',
                               np.where(dict_temp['corp_cls'] == 'K', 'KOSDAQ', 'ETC'))
                gubun = dict_temp['report_nm']
                site = 'https://dart.fss.or.kr/dsaf001/main.do?rcpNo=' + dict_temp['rcp_no']
                df = df.append({'stddate': stddate, 'code': stock_code, 'name': name, 'mkt': mkt, 'gubun': gubun, 'site': site},
                               ignore_index=True)
            else : pass
        df = df.sort_values('stddate').reset_index(drop=True)
    return df

