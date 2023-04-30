import re
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

links = set()

website = ""

for year in range(15, 23):
    for month_int in range(1, 12):
        month = str(month_int)
        if len(month) == 1:
            month = "0" + month
        url = f"https://www.{website}/search?q=*&action=getTitles&widgetId=BlogArchive1&widgetType=BlogArchive&responseType=js&path=https%3A%2F%2Fwww.{website}%2F20{year}%2F{month}%2F"
        print(f"getting : {url}, size of set = {len(links)}")
        page = requests.get(url, timeout=5)

        # Wait for the page to load
        # WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, "post-title")))
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, "html.parser")
            links.update(re.findall(re.compile(f"https://{website}/\d{4}/\d{2}/.*?\.html"), page.content.decode("utf-8").split("'posts': [")[1]))
            print(links)


old_values = pd.read_csv("result.csv")

broken_urls = pd.read_csv("broken_urls.csv")['urls'].values

urls = [url for url in links if url not in old_values["urls"].values]
urls = [url for url in urls if url not in broken_urls]

blog_data = {"date": [], "title": [], "text": [], "urls": []}


def finish(good_data, bad_data):
    write_data = pd.concat([old_values, pd.DataFrame(good_data)])
    write_data.to_csv("result.csv", index=False)
    pd.DataFrame({'url': bad_data}).to_csv("broken_urls.csv")


for url in links:
    try:
        print(f"getting url {url}")
        page = requests.get(url, timeout=5)

        if page.status_code == 404:
            print("page does not exist")
            broken_urls = np.append(broken_urls, url)
            continue

        soup = BeautifulSoup(page.content, "html.parser")
        blog_data["title"].append(soup.select_one("h1.post-title.entry-title").text)
        blog_data["date"].append(soup.select_one("div.post-meta-wrapper").text.strip())
        blog_data["text"].append(soup.select_one("div.post-body-inner").text)
        blog_data["urls"].append(url)

        print(blog_data)

    except KeyboardInterrupt:
        finish(blog_data, broken_urls)
        exit()

    except Exception as e:
        print(f"crashed on {url} : {e}")
        finish(blog_data, broken_urls)
        exit()

finish(blog_data, broken_urls)

