from storage.resource.website.config import WebsiteResourceStore
from typedef import LiveDemoResource


class LiveDemoService:
    _resources = WebsiteResourceStore()

    @classmethod
    def get_all(cls) -> list[LiveDemoResource]:
        return cls._resources.get_livedemo_items()

    @classmethod
    def replace_all(cls, items: list[LiveDemoResource]) -> bool:
        return cls._resources.set_livedemo_items(items)
