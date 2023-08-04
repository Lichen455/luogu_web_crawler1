#以下是爬p题号的爬虫
import requests
import numpy as np
from bs4 import BeautifulSoup
import re
import time
from sympy import true, false
import codecs


# 包含无效的转义序列，函数返回 True
def has_invalid_escape_sequences(s):
    try:
        codecs.decode(s, 'unicode_escape')
        return False
    except UnicodeDecodeError:
        return True


# "提高组]"前面的字符串全部删掉
def remove_text(text: str, keyword: str = "提高组]") -> str:
    result = text.split(keyword, 1)[-1]
    return result


# "普及组]"前面的字符串全部删掉
def remove_text2(text: str, keyword: str = "普及组]") -> str:
    result = text.split(keyword, 1)[-1]
    return result


# 是否包含网址，若包含，不采用该数据
def contains_url(text: str) -> bool:
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    match = re.search(url_pattern, text)
    return bool(match)


# 单独提取 “题目描述”的上一行，是为题目
def extract_title(text: str) -> str:
    if text.find("题目背景") != -1:
        match = re.search(r'^(.*)$\n^.*题目背景', text, re.MULTILINE)
    else:
        match = re.search(r'^(.*)$\n^.*题目描述', text, re.MULTILINE)
    if match:
        return match.group(1)
    else:
        return None


# 截取方式2 截取题目描述到三行空格内的内容

def extract_2(text):
    if text.find("题目背景") != -1:
        start = text.find('题目背景')
    else:
        start = text.find('题目描述')
    if start == -1:
        return ''
    start = text.rfind('\n', 0, start)
    if start == -1:
        start = 0
    end = text.find('\n\n\n', start)
    if end == -1:
        end = len(text)
    return text[start:end].strip().replace('\n\n', '\n')


# 删除文本中所有以 $ 符号开头和结尾，中间有一个任意字符的子字符串
def remove_signs(text):
    return re.sub(r'\$(.)\$', r'\1', text)


# 删掉前九个字符
def remove_9chars(text):
    if len(text) < 9:
        return ''
    # 删除前十个字符，换上题目名称 把两行换行缩减为1行
    return "题目名称：" + text[10:].replace('\n\n', '\n')


# 提取NOIP到三行换行内的文字
def extract(text):
    start = text.find('NOIP')
    if start == -1:
        return ''
    start += len('NOIP')
    end = text.find('\n\n\n', start)
    if end == -1:
        return ''
    return text[start:end].strip()


num = 10000 - 1
numlast = 15000

while num < numlast:
    try:
        time.sleep(0.8)
        num += 1
        # time.sleep(0.5)
        # 目标 URL
        url = 'https://www.luogu.com.cn/problem/P'
        url += str(num)
        head = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"}
        response = requests.get(url, headers=head)
        # 发送 HTTP 请求
        response.encoding = 'utf-8'

        # 设置变量
        str1 = ""
        # 检查响应状态码
        if response.status_code == 200:
            # 解析 HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找所有段落标签
            paragraphs = soup.find_all('div')
            span = soup.find_all('span')
            # 遍历所有段落并打印文本内容
            for p in paragraphs:
                # print(p.text)
                str1 += p.text
            # .replace('\n', '\\n')
            data = "题目名称:" + remove_text2(remove_text(extract_title(str1))) + "\n" + remove_signs(extract_2(str1))
            data = data.replace('\n', ' ').replace('\r', ' ').replace('\"', ' ')
            data = data.replace('\\', '\\\\').replace('\u0009', ' ').replace('\t', ' ')
            if (contains_url(remove_signs(extract_2(str1))) == false and has_invalid_escape_sequences(
                    data) == False and len(data) >= 130):
                with open("train3.json", 'a', encoding='utf-8') as f:
                    f.write(
                        "{\"content\": \"请出一道编程算法题目，只出题干，不包括解题过程,格式一致\",\"summary\": \"" + data + "\"}" + "\n")
                    f.close()
            else:
                if contains_url(remove_signs(extract_2(str1))) == true: print(
                    "\033[31m[Warning] 存在url链接，数据已去除\033[0m")
                if len(data) < 130: print("\033[31m[Warning] 字符数量太少，疑似提取错误\033[0m")
            print("\n" + data)
            print(contains_url(remove_signs(extract_2(str1))), has_invalid_escape_sequences(data))
            print(num)
        else:
            print('请求失败', ' 响应码：' + response.status_code)
    except:
        print("异常：题目不存在或者无法访问题目" + "编号：" + str(num))