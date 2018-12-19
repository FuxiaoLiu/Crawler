'''
The auditor program

'''
import sys 
import requests
from requests.exceptions import RequestException
import csv
from lxml import etree
import re
import pandas as pd 

# 有时候request链接会随机出现错误，需要让这个循环在出现错误的时候不break，继续执行
'''
ConnectionError: HTTPConnectionPool(host='cmispub.cicpa.org.cn', port=80): Max retries exceeded with url: /cicpa2_web/PersonIndexAction.do (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000000B53BFE4908>: Failed to establish a new connection: [WinError 10013] An attempt was made to access a socket in a way forbidden by its access permissions',))
'''



names   = []
gender  = []
duty    = []
Isparty = []
diploma = []
major   = []
school  = []
branch  = []
approvetime = []
Ispartner = []
birth = []
id_no = []
aname = []
real_name = []


# 定义筛选函数 
def search_match(pattern,text):
    match = re.search(pattern,text)
    result = ""
    if match:
        x = match.group()
        #print(x)
        x = x.replace(' ', '')
        x = x.replace('\t', '')
        x = x.strip()
        x = x.split('\n')
        result = x[-1]
        if result == "</td>":
            result = x[-3]
    else:
        result = " "
    print(result)
    return result

with open('auditor.csv', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        names.append(row[0])
        #print(row)

names.remove(names[0])
#names.remove(names[15])

#print(names)
    
for i, n in enumerate(names):
    #if i > 3:
        #break
    print(n)
    name1 = n 
    name = n.encode('GB2312', 'ignore')   
    print(name)
    
    
    # 调试 **
    # name = names[7].encode('GB2312')
    # aname.append(i)
    # name = "刘旻".encode('GB2312')

    data={  "isStock": "00", 
            "method": "indexQuery",
            "perCode":"",
            "perName": name, 
            "queryType":"2"
        }
    try:
        r = requests.post("http://cmispub.cicpa.org.cn/cicpa2_web/PersonIndexAction.do", data=data)
    except RequestException as e:
        print(e)
        continue
    #print(r.text)
    # 处理如果没有搜索到会计师的窗框
    if '没有任何信息' in r.text:
        print("no information")
        #aname.remove(i)
        continue
             
    selector = etree.HTML(r.text)
    id_2 = selector.xpath('//a[contains(text(), names[1])]/@href')
    #print(id_2[0])
    if "#" in id_2:
        id_2.remove("#")
   # id_2 = [l for l in id_2 if not re.search('javascript:gotoPage(383);', l)]      
    id_2 = [l for l in id_2 if not re.search('javascript:gotoPage\(\d+\)', l)]     
 
                  ## 处理如果搜到多个会计师的状况
    for y in id_2:
        #y = id_2[14]
        aname.append(name1)
        #print(y)
        id_1 = y.split('\'')
        #print(id_1[1])
        url = 'http://cmispub.cicpa.org.cn/cicpa2_web/07/' + id_1[1]+'.shtml'
        #print(url)
        try:
            r=requests.get(url)
        except RequestException as e:
            print(e)
            continue
        r.encoding='GB2312'
        #print(r.text)
        a = r.text 
        #print(a)
        # 正则表达式的表示方式
        # birthday 
        pattern = re.compile(r'出生日期\s+</td>\s+<td class=\"data_tb_content\"  width=\'12\%\'>\n.+\n')
        birth.append(search_match(pattern,r.text))
        
        # gender 
        pattern = re.compile(r'性别\s+</td>\s+<td class=\"data_tb_content\"  width=\'12\%\'>\n.+\n')
        gender.append(search_match(pattern,r.text))
        
        #duty 
        pattern = re.compile(r'所内职务\s+</td>\s+<td class=\"data_tb_content\" width=\'12\%\'>\n.+\n')
        duty.append(search_match(pattern,r.text))
        
        # Isparty 
        pattern = re.compile(r'是否党员\s+</td>\s+<td class=\"data_tb_content\"  width=\'12\%\'>\n.+\n')
        Isparty.append(search_match(pattern,r.text))
        
        # real_name 
        pattern = re.compile(r'姓名\s+</td>\s+<td class=\"data_tb_content\"  width=\'12\%\'>\n.+\n')
        real_name.append(search_match(pattern,r.text))
        
        # diploma 
        pattern = re.compile(r'学历\s+</td>\s+<td class=\"data_tb_content\">\n.+\n')
        diploma.append(search_match(pattern,r.text))
        
        # major 
        pattern = re.compile(r'所学专业\s+</td>\s+<td class=\"data_tb_content\">\n.+\n.+\n.+')
        major.append(search_match(pattern,r.text))
        
        ## 学校有一些有乱码，需要加if选择
        # school 
        pattern = re.compile(r'毕业学校\s+</td>\s+<td class=\"data_tb_content\">\n.+\n')
        if search_match(pattern,r.text) == '<tdclass=\"data_tb_content\">' :
            school.append("无")
        else:
            school.append(search_match(pattern,r.text)) 
        
        # branch 
        pattern = re.compile(r'所在事务所\s+</td>\s+<td class=\"data_tb_content\" colspan=\'6\'>\n.+\n')
        branch.append(search_match(pattern,r.text))
        
        # approvetime 
        pattern = re.compile(r'批准注册时间\s+</td>\s+<td class=\"data_tb_content\" colspan=\'2\'>\n.+\n')
        approvetime.append(search_match(pattern,r.text))
        
        #id_no 
        pattern = re.compile(r'注册会计师证书编号\s+</td>\s+<td class=\"data_tb_content\" colspan=\'2\'>\n.+\n')
        id_no.append(search_match(pattern,r.text))
        
        #Ispartner 
        pattern = re.compile(r'是否合伙人（股东）\s+</td>\s+<td class=\"data_tb_content\" colspan=\'2\'>\n.+\n')
        Ispartner.append(search_match(pattern,r.text))

d = {
        'names': aname,
        'birth':birth,
        'gender':gender,
        'duty':duty,
        'Isparty': Isparty, 
        'real_name':real_name,
        'diploma':diploma,
        'major':major,
        'school':school,
        'branch':branch,
        'approvetime':approvetime,
        'id_no':id_no,
        'Ispartner':Ispartner
    }
df = pd.DataFrame(data=d)
df.to_csv("result.csv", sep='\t', encoding='GB2312')

