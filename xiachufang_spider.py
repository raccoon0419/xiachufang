import requests
from lxml import etree
import json


def strip_str(list):
    lst = []
    for i in list:
        i = i.strip()
        lst.append(i)
    return lst

def rm_kong(list):
    for i,v in enumerate(list):
        if v == '' or "、":
            list.pop(i)
    return list


class XCF_Spiser(object):
    def __init__(self):
        self.start_url = 'http://www.xiachufang.com/category/40076/'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}

    def parse_url(self,url):
        print(url)
        response = requests.get(url,headers=self.headers)
        html_str = response.content
        return html_str

    def get_content_list(self,html_str):
        html = etree.HTML(html_str)
        li_list = html.xpath('//div[contains(@class,"pure-u-2-3")]//div[@class="normal-recipe-list"]/ul/li')
        content_list = []
        for li in li_list:
            item={}
            item['menu_title'] = strip_str(li.xpath(".//div[contains(@class,'info')]/p[@class='name']/a/text()"))
            item['foods'] = rm_kong(strip_str(li.xpath(".//div[contains(@class,'info')]/p[contains(@class,'ing')]//text()")))
            item['foods'] = [','.join(item['foods'])]
            item['img'] = li.xpath(".//div[contains(@class,'cover')]/img/@data-src")
            item['img'] = [i.split("@")[0] for i in item["img"]]
            item['author'] =li.xpath(".//div[contains(@class,'info')]/p[@class='author']/a/text()")
            item['stats'] = strip_str(li.xpath(".//div[contains(@class,'info')]/p[@class='stats']//text()"))
            item['content_url'] = li.xpath(".//div[contains(@class,'info')]/p[@class='name']/a/@href")
            content_url = "http://www.xiachufang.com" + item["content_url"][0]
            detail_content = self.parse_url(content_url)
            self.get_detail_content(detail_content,item)

            content_list.append(item)

        # 下一页url

        next_url = html.xpath("//a[text()='下一页']/@href")
        if next_url:
            next_url = 'http://www.xiachufang.com' + next_url[0]
            return content_list,next_url
        else:
            return content_list,None

    def get_detail_content(self,detail_content,item):
        html = etree.HTML(detail_content)
        item['step_text'] = list(filter(None,strip_str(html.xpath("//div[@class='steps']//li//text()"))))
        item['step_img_url'] = html.xpath("//div[@class='steps']//li/img/@src")

        return item

    def save_content_list(self,content_list):
        for content in content_list:
            with open('xiachufang.txt','a',encoding='utf-8') as f:
                f.write(json.dumps(content,ensure_ascii=False))
                f.write('\n')

    def run(self):
        # 1.构建url地址
        start_url = self.start_url
        # 2.请求地址，获取响应
        html_str = self.parse_url(start_url)
        # 3.提取数据,获得内容
        content_list,next_url = self.get_content_list(html_str)
        # 4.保存信息
        self.save_content_list(content_list)
        while next_url:
            html_str = self.parse_url(next_url)
            content_list,next_url = self.get_content_list(html_str)
            self.save_content_list(content_list)


if __name__ == '__main__':
    xcf = XCF_Spiser()
    xcf.run()
