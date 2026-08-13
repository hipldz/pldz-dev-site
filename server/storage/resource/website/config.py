import json
import typing
from pathlib import Path
from core import Logger, ProjectConfig
from typedef import LiveDemoResource


class WebsiteResourceStore:
    """
    加载live demo配置
    """

    def __init__(self) -> None:
        config_file = ProjectConfig.get_livedemo_config_path()
        # 读取这个路径的json文件
        try:
            with open(config_file, 'r', encoding='utf-8') as file:
                self.livedemo_config = json.load(file)
        except FileNotFoundError:
            Logger.error(f"LiveDemo配置文件未找到: {config_file}")
            self.livedemo_config = {}
        except json.JSONDecodeError:
            Logger.error(f"LiveDemo配置文件格式错误: {config_file}")
            self.livedemo_config = {}
        except Exception as e:
            Logger.error(f"加载LiveDemo配置时发生错误: {e}")
            self.livedemo_config = {}

    def get_livedemo_items(self) -> typing.List[LiveDemoResource]:
        """
        获取LiveDemo配置中的所有项目
        """
        items = []
        for item in self.livedemo_config.get('data', []):
            try:
                items.append(LiveDemoResource(
                    title=item['title'],
                    folder=item['folder'],
                    url=item['url'],
                    thumbnail=item['thumbnail'],
                    previewgif=item['previewgif'],
                    sourcelink=item['sourcelink'],
                    date=item['date'],
                    description=item.get('description', '')
                ))
            except KeyError as e:
                Logger.error(f"LiveDemo.json 配置项缺少必要字段: {e}")
        return items

    def set_livedemo_items(self, items: typing.List[LiveDemoResource]) -> bool:
        """
        设置LiveDemo配置中的所有项目
        """
        self.livedemo_config['data'] = items
        config_file = ProjectConfig.get_livedemo_config_path()
        try:
            Path(config_file).parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w', encoding='utf-8') as file:
                json.dump(self.livedemo_config, file, ensure_ascii=False, indent=4)
            Logger.info(f"LiveDemo配置已更新: {config_file}")
            self.get_livedemo_items()
            return True
        except Exception as e:
            Logger.error(f"保存LiveDemo配置时发生错误: {e}")
            return False
