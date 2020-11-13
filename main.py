import json
import sys
from typing import List, Dict

import requests
from lxml import html, etree  # type: ignore
from lxml.html import Element  # type: ignore
from requests import Response

if len(sys.argv) < 2:
    print('You need to specify the url')
    sys.exit()

url = sys.argv[1]


class HboGo:
    def __init__(self, url: str) -> None:
        self.base_url: str = 'https://hbogo.cz'
        self.url: str = url
        self.cz_name_path: str = '//div[@class="breadcrumbs"]/a[2]/text()[1]'
        self.original_name_path: str = '//div[@class="meta"]/span[@class="original-title"]/text()[1]'
        self.year_path: str = '//div[@class="meta"]/text()[1]'
        self.genre_path: str = '//div[@class="meta"]/text()[2]'
        self.rating_1_path: str = '//span[@class="hboRate"]/span[@class="ratingValue"]/text()[1]'
        self.rating_2_path: str = '//span[@class="hboRate"]/span[@class="bestRating"]/text()[1]'
        self.episodes_href_path: str = '//div[@id="episodes"]//a/@href'
        self.episodes_title_path: str = '//div[@id="episodes"]//a//span[@class="title"]/text()'
        self.page = self.__get_page()
        self.tree = self.__get_tree()

    def __get_page(self) -> Response:
        return requests.get(self.url)

    def __get_tree(self) -> Element:
        return html.fromstring(self.page.content, parser=etree.HTMLParser(encoding='utf-8'))

    def __get_cz_title(self) -> str:
        return str(self.tree.xpath(self.cz_name_path)[0])

    def __get_original_title(self) -> str:
        return str(self.tree.xpath(self.original_name_path)[0])

    def __get_year(self) -> str:
        return str(self.tree.xpath(self.year_path)[0])

    def __get_genre(self) -> str:
        return str(self.tree.xpath(self.genre_path)[0])

    def __get_rating(self) -> str:
        return f"{self.tree.xpath(self.rating_1_path)[0]}{self.tree.xpath(self.rating_2_path)[0]}"

    def __get_episodes(self) -> List:
        return [{"url": f"{self.base_url}{url}", "title": str(title)} for url, title in
                zip(self.tree.xpath(self.episodes_href_path), self.tree.xpath(self.episodes_title_path))]

    def __get_dict(self) -> Dict:
        return {
            "title": {
                "cz": self.__get_cz_title(),
                "original": self.__get_original_title(),
            },
            "year": self.__get_year(),
            "genre": self.__get_genre(),
            "rating": self.__get_rating(),
            "episodes": self.__get_episodes(),
        }

    def get_json(self) -> str:
        return json.dumps(self.__get_dict(), ensure_ascii=False)


if __name__ == "__main__":
    print(HboGo(url).get_json())
