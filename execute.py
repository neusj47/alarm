from _load import *
from pykrx import stock
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

df_mkt = get_code_info()
df_target = df_mkt[(df_mkt.시장구분.isin(['KOSDAQ','KOSPI'])) & (df_mkt.소속부 != ('SPAC(소속부없음)')) & (df_mkt.주식종류 == ('보통주'))]
start_date =  stock.get_nearest_business_day_in_a_week(datetime.today().strftime('%Y%m%d'))

def get_corporate_action(start_date, df_target) :
    all = pd.DataFrame()
    for i in range(0,len(df_target)) :
        try:
            freecapinc_temp = free_capital_inc(start_date, df_target.Code[i])
        except:
            freecapinc_temp = pd.DataFrame()

    all = pd.concat([all, freecapinc_temp])
    return all


def send_mail(df,froms,tos):
    if len(df) != 0:
        df_html = df.to_html(index=False, justify='center', border=1)
        df_html = df_html.replace('<table border="1" class="dataframe">',
                                  '<table border="0" class="dataframe" bgcolor=black cellpadding=1 cellspacing=1><tr><td><table border="0" class="dataframe" bgcolor=black>')
        df_html = df_html.replace('</table>', '</table> </td></tr></table>')
        df_html = df_html.replace('<td>', '<td bgcolor=white>')
        df_html = df_html.replace('<th>', '<th bgcolor=#e5e5e5>')
        i = 0
        while i == len(df) - 1:
            df_html = df_html.replace(df.iloc[i].site, '<A href=' + df.iloc[i].site + '> DART이동 </A>')
            i = i + 1

        msg_header = "" + start_date + "_기업공시내역입니다." \
                                       "<br><br>"

        contents = msg_header + df_html

        part1 = MIMEText(contents, 'html', _charset="utf8")

        loginId = ""
        loginPw = ""

        msg = MIMEMultipart('alternative')
        msg['Subject'] = start_date + '_Corporate_Action_List'
        msg['From'] = froms
        # msg['To'] = toMail

        msg.attach(part1)

        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.ehlo()  # say Hello
        smtp.starttls()  # TLS 사용시 필요
        smtp.login(loginId, loginPw)

        for toss in tos:
            smtp.sendmail(froms, toss, msg.as_string())

        smtp.quit()
    else:
        pass
    return

froms = ""
tos = [""]

send_mail(get_corporate_action(start_date, df_target), froms, tos)





