from django.shortcuts import render
from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from django.contrib import messages
# Create your views here.

def home(request):
    return render(request, 'index.html')

options = Options()
options.add_argument("--headless")
driverc = "./assets/chromedriver.exe"
driver = webdriver.Chrome(driverc, options=options)
def matching_product_index(search_items, search):
    match_list = []
    final_search_list = []
    search_list = re.split("[- ( ) . / ? * % $ +]", search)
    for i in range(search_list.count('')):
        search_list.remove('')
    for i in search_list:
        final_search_list.append(i.upper())
    for i in search_items:
        count = 0
        final_list1 = []
        list1 = re.split("[- / ( ) .]", i)
        for j in range(list1.count('')):
            list1.remove('')
        for j in list1:
            final_list1.append(j.upper())
        for word in final_search_list:
            if word in final_list1:
                count += 2
            else:
                count -= 1
        match_list.append(count)
        # print(match_list)
        if match_list:
            return match_list.index(max(match_list))
    return -1


def optimal(fprice, frating, aprice, arating):
    if fprice=="" or frating=="" or aprice=="" or arating=="":
        return None
    price1 = int(((re.sub(",", "", fprice))[1:]))
    price2 = int(re.sub(",", "", aprice))
    rating1 = float(frating)
    rating2 = float(arating)

    if price1 < price2:
        if rating1 >= rating2:
            return True; #flipkart
        else:
            return (price1 / rating1) >= (price2 / rating2)
    elif price2 == price1:
        if rating1 > rating2:
            return True
        elif rating1 == rating2:
            return None
        else:
            return False
    else:
        if rating2 >= rating1:
            return False
        else:
            return (price1 / rating1) >= (price2 / rating2)


def Flipkart(search_query):
    Product_name = ""
    Product_price = ""
    Product_rating = ""
    Product_image = "static/connection error.jpeg"
    final_link = ""
    url = "https://www.flipkart.com/search?q={0}".format(search_query)
    try:
        driver.get(url)
    except:
        print("connection error")
    else:
        page_content = driver.page_source
        print(url)

        soup = BeautifulSoup(page_content, "html.parser")

        Search_results_links = soup.findAll("a", class_="_1fQZEK")
        Search_results = soup.findAll("div", class_="_4rR01T")
        if len(Search_results_links) == 0:
            Search_results_links = soup.findAll("a", class_="s1Q9rs")
            Search_results = soup.findAll("a", class_="s1Q9rs")
        if len(Search_results_links) == 0:
            Search_results_links = soup.findAll("a", class_="IRpwTa")
            Search_results = soup.findAll("a", class_="IRpwTa")
        Results = []
        for i in Search_results[:10]:
            Results.append(i.text)

        match_link = Search_results_links[matching_product_index(Results, search_query)]

        link_text = match_link.get("href")
        final_link = "https://www.flipkart.com" + link_text

        driver.get(final_link)
        page = driver.page_source
        soup1 = BeautifulSoup(page, "html.parser")

        image = soup1.find("img", class_="_396cs4 _2amPTt _3qGmMb")
        span_name = soup1.find("h1", class_="yhB1nd")
        span_price = soup1.find("div", class_="_30jeq3 _16Jk6d")
        span_rating = soup1.find("div", class_="_3LWZlK")

        if span_name:
            Product_name = span_name.text.strip()
        else:
            Product_name = ""

        if span_price:
            Product_price = span_price.text.strip()
        else:
            Product_price = ""

        if span_rating:
            Product_rating = span_rating.text.strip()
        else:
            Product_rating = ""

        if image:
            Product_image = image['src']

    return {"name": Product_name, "price": Product_price, "rating": Product_rating, "image": Product_image, "link": final_link}


def amazon(search_object):
    Product_name = ""
    Product_price = ""
    Product_rating = ""
    Product_image = "static/connection error.jpeg"
    final_link = ""
    # print("https://www.amazon.in/s?k={0}".format(search_object))
    try:
        driver.get("https://www.amazon.in/s?k={0}".format(search_object))
    except:
        print("https://www.amazon.in/s?k={0}".format(search_object))
    else:
        page_content = driver.page_source

        soup = BeautifulSoup(page_content, "html.parser")

        Results = []
        # Find all divs with the specified class
        divs = soup.findAll("div",
                            class_="sg-col-20-of-24 s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16")

        if len(divs):
            Search_results = soup.find_all("span", class_="a-size-medium a-color-base a-text-normal")
            for i in Search_results[:10]:
                Results.append(i.text)
            idx = matching_product_index(Results, search_object)
            if idx == -1:
                return None
            match_div = divs[idx]
            image = match_div.find("img", class_="s-image")
            span_name = match_div.find("span", class_="a-size-medium a-color-base a-text-normal")
            span_price = match_div.find("span", class_="a-price-whole")
            span_rating = match_div.find("span", class_="a-icon-alt")
            link = match_div.find("a", class_="a-link-normal s-no-outline")
            final_link = "https://www.amazon.in" + link.get("href")
        else:
            divs = soup.find_all("div", class_="a-section a-spacing-base a-text-center")
            if len(divs) == 0:
                divs = soup.find_all("div", class_="a-section a-spacing-base")
            if len(divs):
                Search_results = soup.find_all("span", class_="a-size-base-plus a-color-base a-text-normal")
                for i in Search_results[:10]:
                    Results.append(i.text)
                idx = matching_product_index(Results, search_object)
                if idx == -1:
                    return None
                match_div = divs[idx]
                image = match_div.find("img", class_="s-image")
                span_name = match_div.find("span", class_="a-size-base-plus a-color-base a-text-normal")
                span_price = match_div.find("span", class_="a-price-whole")
                span_rating = match_div.find("span", class_="a-size-base puis-bold-weight-text")
                link = match_div.find("a", class_="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal")
                final_link = "https://www.amazon.in" + link.get("href")
            else:
                span_name = None
                span_price = None
                span_rating = None
                image = None
                final_link = None

        if span_name:
            Product_name = span_name.text.strip()
        else:
            Product_name = ""

        if span_price:
            Product_price = span_price.text.strip()
        else:
            Product_price = ""

        if span_rating:
            Product_rating = span_rating.text.strip()[:3]
        else:
            Product_rating = ""

        if image:
            Product_image = image['src']

    return {"name": Product_name, "price": Product_price, "rating": Product_rating, "image": Product_image, "link": final_link}


def result(request):
    s = request.GET['name'].replace(" ", "+")
    amz_details = amazon(s)
    fkdetails = Flipkart(re.sub("[- ( ) , . /   ]", "+", amz_details["name"]))
    if fkdetails is None or amz_details is None:
        messages.warning(request, "please search specifically")
        print("$$$$$$$$$")
        return render(request,"index.html")
    # print(re.sub("[- ( ) , . /]","+",fkdetails["name"]))
    optimalProduct = optimal(fkdetails["price"],fkdetails["rating"],amz_details["price"],amz_details["rating"])
    return render(request, 'result.html',
                  {"fname": fkdetails["name"], "fprice": fkdetails["price"], "frating": fkdetails["rating"],
                   "fimage": fkdetails["image"],"flink":fkdetails["link"], "aname": amz_details["name"], "aprice": amz_details["price"],
                   "arating": amz_details["rating"], "aimage": amz_details["image"],"alink": amz_details["link"],"recomendation":optimalProduct
     })
