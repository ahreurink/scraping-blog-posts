import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

old_values = pd.read_csv("result.csv")

website = ""
all_urls = [f"https://{website}/articles/{i}" for i in range(0, 1)]

broken_urls = pd.read_csv("broken_urls.csv")['urls'].values

urls = [url for url in all_urls if url not in old_values["urls"].values]
urls = [url for url in urls if url not in broken_urls]

blog_data = {"date": [], "title": [], "text": [], "urls": []}


def finish(good_data, bad_data):
    write_data = pd.concat([old_values, pd.DataFrame(good_data)])
    write_data.to_csv("scraper_titels.csv", index=False)
    pd.DataFrame({'url': bad_data}).to_csv("broken_urls.csv")


for url in urls:
    try:
        print(f"getting url {url}")
        page = requests.get(url, timeout=5)

        if page.status_code == 404:
            print("page does not exist")
            broken_urls = np.append(broken_urls, url)
            continue

        soup = BeautifulSoup(page.content, "html.parser")
        blog_data["title"].append(soup.select_one("h2.node-title"))
        blog_data["date"].append(soup.select_one("div.submitted").text)
        blog_data["text"].append(soup.select_one("div.field.field-name-body.field-type-text-with-summary.field-label-hidden").text.replace("<p>", "").replace("</p>", ""))
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
