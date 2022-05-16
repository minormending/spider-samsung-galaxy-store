from typing import Iterable, List
import scrapy
from scrapy.http import Request, Response

from samsung_galaxy_store import Category, AppSummary, App

from scrapy_samsung_galaxy_store.middlewares import JsonResponse


class SpiderSpider(scrapy.Spider):
    name = "galaxy-store"
    CATEGORY_APPS_PAGE_SIZE = 500

    def start_requests(self) -> Request:
        yield Request(url="api://categories", callback=self.parse_categories)

    def parse_categories(self, response: JsonResponse) -> Iterable[Request | Category]:
        categories: List[Category] = response.json()
        for category in categories:
            yield category
            yield Request(
                url=f"api://category_apps/{category.id}",
                meta={
                    "category": category,
                    "start": 1,
                    "end": self.CATEGORY_APPS_PAGE_SIZE,
                },
                callback=self.parse_category_apps,
            )

    def parse_category_apps(self, response: JsonResponse) -> Iterable[Request | App]:
        request: Request = response.request
        category: Category = request.meta.get("category")
        apps: List[AppSummary] = response.json()
        for app in apps:
            yield app
            yield Request(
                url=f"api://app/{app.guid}",
                meta={
                    "category": category,
                    "app": app,
                },
                callback=self.parse_app_details,
            )
            break
        if len(apps) == self.CATEGORY_APPS_PAGE_SIZE:
            start: int = request.meta.get("start")
            yield Request(
                url=f"api://category_apps/{category.id}",
                meta={
                    "category": category,
                    "start": start + self.CATEGORY_APPS_PAGE_SIZE,
                    "end": self.CATEGORY_APPS_PAGE_SIZE,
                },
                callback=self.parse_category_apps,
            )

    def parse_app_details(self, response: JsonResponse) -> Iterable[App]:
        app: App = response.json()
        yield app
