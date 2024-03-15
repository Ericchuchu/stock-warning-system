import requests
import time
import re
import os
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import telebot
import datetime

#telegram bot
API_key="6487255122:AAGe9Vx4dfGns00BP47ZUzpRyQES-QoLALs"
bot=telebot.TeleBot(API_key)
next_month='0'
past_stock_number=[]
#字典寫入list的function
def append_revenue(stock,current_revenue,average_revenue_last_season):
    revenue_dict={}
    revenue_dict['股票']=stock
    revenue_dict['最近一月營收(千元)']=current_revenue
    revenue_dict['最近一季平均月營收(千元)']=average_revenue_last_season
    final_revenue_list.append(revenue_dict)
def append_eps(stock,current_eps,average_eps_last_season):
    eps_dict={}
    eps_dict['股票']=stock
    eps_dict['最近一月盈餘(元)']=current_eps
    eps_dict['最近一季平均月盈餘(元)']=average_eps_last_season
    final_eps_list.append(eps_dict)
'''
@bot.message_handler(commands=['start','help'])
def handle_start_help(message):
    print(message.chat.id)

bot.polling()
'''
while True:
    time.sleep(1)
    # 獲取當前日期
    today = datetime.date.today()
    # 獲取年月日
    year = str(today.year-1911)
    month = str(today.month)
    day = str(today.day)
    # day='17'
    #到下一個月就重置list
    if month == next_month:
        past_stock_number=[]
    next_month = str(today.month+1)
    #設置driver
    #driver = webdriver.Edge(executable_path='C:\\Program Files(x86)\\Microsoft\\Edge\\Application\\msedge')

    service = Service(EdgeChromiumDriverManager().install())
    options = Options()
    options.add_argument("--headless") # or use pyvirtualdiplay
    options.add_argument("--no-sandbox") # needed, because colab runs as root
    options.headless = True
    inconnect = True
    while inconnect:
      try:
        driver = webdriver.Chrome(service=service, options=options)
        url = "https://mops.twse.com.tw/mops/web/t05st02"
        time.sleep(2)
        driver.get(url)
        inconnect = False
      except:
        inconnect = True # 直到連接上為止

    #特定的年月日
    time.sleep(1)
    year_box = driver.find_element(By.ID,'year')
    year_box.send_keys(year)
    month_dropdown = driver.find_element(By.ID,'month')
    dropdown_month = Select(month_dropdown)
    dropdown_month.select_by_visible_text(month)
    day_dropdown = driver.find_element(By.ID,'day')
    dropdown_day = Select(day_dropdown)
    dropdown_day.select_by_visible_text(day)
    day_dropdown.send_keys(Keys.ENTER)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source,"lxml")
    target_class1="odd"
    target_class2="even"
    tr_elements1 = soup.find_all('tr', class_=target_class1)
    tr_elements2 = soup.find_all('tr', class_=target_class2)
    tr_withkeyword=[]
    # 關鍵字
    keyword = "達公布注意交易資訊"
    keyword2 = "達公佈注意交易資訊"
    keyword3 = "達公布注意資訊標準"
    keyword4 = "達公佈注意資訊標準"
    keyword5 = "達公布注意交易資訊標準"
    ketword6 = "達公佈注意交易資訊標準"
    keyword7 = "近期股價異常，故公告相關訊息"
    keyword8 = "集中交易市場有異常交易情形"

    # 找出包含關鍵字的tr
    for tr in tr_elements1:
        td_elements = tr.find_all('td')
        # 輸出找到的 <td> 元素內容
        for td in td_elements:
            if keyword in td.text or keyword2 in td.text or keyword3 in td.text or keyword4 in td.text or keyword5 in td.text:
                tr_withkeyword.append(tr)

    for tr in tr_elements2:
        td_elements = tr.find_all('td')
        # 輸出找到的 <td> 元素內容
        for td in td_elements:
            if keyword in td.text or keyword2 in td.text or keyword3 in td.text or keyword4 in td.text or keyword5 in td.text:
                tr_withkeyword.append(tr)

    if not tr_withkeyword:
        print('今天無警示股')

    #將有括號的eps轉為負數
    def convert_eps(uncleaned_eps):
        cleaned_eps=''
        minus_flag=False
        for char in uncleaned_eps:
            if char=="(" or char==')':
                minus_flag=True
                continue
            else:
                cleaned_eps+=char
        if minus_flag:
            return str(-float(cleaned_eps))
        else:
            return cleaned_eps
    # 警示股股票代號和股票名稱
    stock_number=[]
    stock_name=[]
    stock_list=[]
    eps_list=[]
    # 點擊選定tr中的詳細資訊
    for tr in tr_withkeyword:
        soup = BeautifulSoup(str(tr),"lxml")
        #從新聞裡的詳細資訊取出(格式不同)
        input_element = soup.find_all("input", {"type": "hidden"}) #找到特定的 input type
        max_len=0
        # 找到要取用的內容，也就是target_value
        if input_element:
            for type_hidden in input_element:
                value = type_hidden.get("value")
                if len(value) > max_len:
                    max_len=len(value)
                    target_value=value
        #抓取公布的最近一月營收盈餘
        #revenue = re.search(r"營業收入(?:\(百萬元\))?\s+([\d.]+)", target_value)
        try:
            eps_target = re.search(r"每股盈餘(?:\s+)?(?:\(虧損\))?(?:\s+)?(?:\(元\))?(?:\s+)?(\(?-?[\d.]+\)?)", target_value) #可能還會有格式的例外
            eps_target = convert_eps(eps_target.group(1))
            # print(eps_target)
            eps_list.append(eps_target)
        except:
            eps_target = 'none'
        if eps_target != 'none':
            td_elements=soup.find_all('td')
            stock_number.append(td_elements[2].text.replace('\xa0','')) #時重大資訊為td_elements[0]
            stock_name.append(td_elements[3].text.replace('\xa0',''))#及時重大資訊為td_elements[1]
            stock_list.append(td_elements[2].text.replace('\xa0','')+td_elements[3].text.replace('\xa0',''))
            print(td_elements[2].text.replace('\xa0','')+td_elements[3].text.replace('\xa0',''))
    #把重複過的股票排除
    for i in range(len(stock_number)):
        if stock_number[i] in past_stock_number:
            stock_number[i]=''
            stock_name[i]=''
            stock_list[i]=''
            eps_list[i]=''
    #創建營收和盈餘的list
    final_revenue_list=[]
    final_eps_list=[]

    for stock_number,stock,eps_ in zip(stock_number,stock_list,eps_list):
        if stock_number=='':
            continue
        past_stock_number.append(stock_number)
        try:
            try:
                url = "https://tw.stock.yahoo.com/quote/"+stock_number+".TW/eps"
                driver.get(url)
                time.sleep(1)
                find_past_eps=driver.find_element(By.XPATH,'//*[@id="qsp-eps-table"]/div/div[2]/div/div/ul/li[1]/div/div[2]/span')
                stock_past_eps=find_past_eps.text
                average_stock_past_eps=float(stock_past_eps)/3
                if eps_ != 'none':
                    append_eps(stock,eps_,str(average_stock_past_eps))
                else:
                    append_eps(stock,'none',str(average_stock_past_eps))
            except:
                url = "https://tw.stock.yahoo.com/quote/"+stock_number+".TWO/eps"
                driver.get(url)
                time.sleep(1)
                find_past_eps=driver.find_element(By.XPATH,'//*[@id="qsp-eps-table"]/div/div[2]/div/div/ul/li[1]/div/div[2]/span')
                stock_past_eps=find_past_eps.text
                average_stock_past_eps=float(stock_past_eps)/3
                if eps_ != 'none':
                    append_eps(stock,eps_,str(average_stock_past_eps))
                else:
                    append_eps(stock,'none',str(average_stock_past_eps))
        except NoSuchElementException:
            append_eps(stock,eps_,'none')
        try:
            try:
                url = "https://tw.stock.yahoo.com/quote/"+stock_number+".TW/revenue"
                driver.get(url)
                time.sleep(1)
                find_revenue=driver.find_element(By.XPATH,'//*[@id="qsp-revenue-table"]/div/div[2]/div/div/ul/li[1]/div/div[2]/ul/li[1]/span')
                stock_current_revenue=find_revenue.text
                season_button=driver.find_element(By.XPATH,'//*[@id="qsp-revenue-chart"]/div[2]/div/div[2]/button/span')
                driver.execute_script("arguments[0].click();", season_button)
                time.sleep(1)
                find_past_revenue=driver.find_element(By.XPATH,'//*[@id="qsp-revenue-table"]/div/div[2]/div/div/ul/li[1]/div/div[2]/ul/li[1]/span')
                stock_past_revenue=find_past_revenue.text
                stock_past_revenue = stock_past_revenue.replace(',', '')
                average_stock_past_revenue=int(stock_past_revenue)/3
                append_revenue(stock,stock_current_revenue,str(average_stock_past_revenue))
            except:
                url = "https://tw.stock.yahoo.com/quote/"+stock_number+".TWO/revenue"
                driver.get(url)
                time.sleep(1)
                find_revenue=driver.find_element(By.XPATH,'//*[@id="qsp-revenue-table"]/div/div[2]/div/div/ul/li[1]/div/div[2]/ul/li[1]/span')
                stock_current_revenue=find_revenue.text
                season_button=driver.find_element(By.XPATH,'//*[@id="qsp-revenue-chart"]/div[2]/div/div[2]/button/span')
                driver.execute_script("arguments[0].click();", season_button)
                time.sleep(1)
                find_past_revenue=driver.find_element(By.XPATH,'//*[@id="qsp-revenue-table"]/div/div[2]/div/div/ul/li[1]/div/div[2]/ul/li[1]/span')
                stock_past_revenue=find_past_revenue.text
                stock_past_revenue = stock_past_revenue.replace(',', '')
                average_stock_past_revenue=int(stock_past_revenue)/3
                append_revenue(stock,stock_current_revenue,str(average_stock_past_revenue))
        except NoSuchElementException:
            append_revenue(stock,'none','none')

    if final_revenue_list and final_eps_list:
      print(final_revenue_list)
      print(final_eps_list)
      driver.quit()
'''
    for revenue,eps in zip(final_revenue_list,final_eps_list):
        revenue_grow_up_percentage=(float(revenue['最近一月營收(千元)'].replace(',', ''))-float(revenue['最近一季平均月營收(千元)']))/float(revenue['最近一季平均月營收(千元)'])*100
        eps_grow_up_percentage=(float(eps['最近一月盈餘(元)'])-float(eps['最近一季平均月盈餘(元)']))/float(eps['最近一季平均月盈餘(元)'])*100
        revenue_grow_up_percentage_str = "{:.2f}".format(revenue_grow_up_percentage)
        eps_grow_up_percentage_str = "{:.2f}".format(eps_grow_up_percentage)
        message=revenue['股票']+"\n最近一月營收(千元):"+revenue['最近一月營收(千元)'].replace(',', '')+"\n最近一季平均月營收(千元):"+revenue['最近一季平均月營收(千元)']+"\n成長:"+revenue_grow_up_percentage_str+"%"+"\n最近一月盈餘(元):"+eps['最近一月盈餘(元)']+"\n最近一季平均月盈餘(元):"+eps['最近一季平均月盈餘(元)']+"\n成長:"+eps_grow_up_percentage_str+"%"
        bot.send_message(-1001970783350,message)'''

