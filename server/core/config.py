import os
import dotenv

from .settings import Settings

class ProjectConfig:
    '''
    整个项目的配置文件
    '''
    # 当前文件相对于项目main.py的层级
    DIR_LOOP = 2

    PROJECT_ROOT = ''
    settings: Settings | None = None

    @classmethod
    def load_env(cls) -> Settings:
        """
        加载环境变量文件 .env
        """

        # 确定项目根目录
        cls.PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
        for _ in range(ProjectConfig.DIR_LOOP):
            cls.PROJECT_ROOT = os.path.dirname(cls.PROJECT_ROOT)

        # 加载环境文件；缺失时继续使用默认配置，并交由 Settings 给出提示。
        env_file_path = cls.get_abs_path('', '.env')
        initial_warnings: tuple[str, ...] = ()
        if not os.path.exists(env_file_path):
            initial_warnings = (f"环境变量文件 .env 未找到，将使用环境变量和默认值: {env_file_path}",)
        else:
            dotenv.load_dotenv(env_file_path, override=False)

        cls.settings = Settings.from_env(initial_warnings=initial_warnings)
        return cls.settings

    @classmethod
    def get_settings(cls) -> Settings:
        """Return the loaded settings, or a non-blocking snapshot for imported tools/tests."""
        if cls.settings is None:
            cls.settings = Settings.from_env()
        return cls.settings

    @classmethod
    def get_abs_path(cls, folder: str = '', file_name: str = '') -> str:
        '''
        获取任何项目文件的绝对路径
        '''
        path = os.path.normpath(os.path.join(cls.PROJECT_ROOT, folder, file_name))
        return path

    @classmethod
    def get_statics_path(cls) -> str:
        '''
        获得静态资源的绝对路径
        '''
        return cls.get_abs_path('server/statics')

    @classmethod
    def get_resource_path(cls) -> str:
        '''
        获得资源文件的绝对路径
        '''
        resources_path = cls.get_settings().resources_path
        return cls.get_abs_path(resources_path)

    @classmethod
    def get_images_path(cls) -> str:
        '''
        获得存储图像的绝对路径
        '''
        image_path = cls.get_settings().images_path
        return cls.get_abs_path(image_path)

    @classmethod
    def get_articles_path(cls) -> str:
        '''
        获得存储文章的绝对路径
        '''
        articles_path = cls.get_settings().articles_path
        return cls.get_abs_path(articles_path)

    @classmethod
    def get_cache_path(cls) -> str:
        """
        获取缓存目录的路径
        """
        cache_path = cls.get_settings().cache_path
        return cls.get_abs_path(cache_path)

    @classmethod
    def get_webp_cache_path(cls) -> str:
        """
        获取缓存目录的路径
        """
        return cls.get_abs_path(cls.get_settings().webp_cache_path)

    @classmethod
    def get_article_index_path(cls) -> str:
        """Return the rebuildable article index cache file."""
        return cls.get_abs_path(cls.get_settings().cache_path, 'article-index/index.json')

    @classmethod
    def get_livedemo_config_path(cls) -> str:
        """
        获取livedemo配置的json文件
        """
        return cls.get_website_config_path('livedemo.json')

    @classmethod
    def get_website_config_path(cls, filename: str) -> str:
        return os.path.join(cls.get_resource_path(), 'website', 'config', filename)

    @classmethod
    def get_website_legal_path(cls, filename: str) -> str:
        return os.path.join(cls.get_resource_path(), 'website', 'legal', filename)

    @classmethod
    def get_db_path(cls) -> str:
        """
        获取 JSON 数据库文件目录的绝对路径
        """
        db_path = cls.get_settings().db_path
        return cls.get_abs_path(db_path)

    @classmethod
    def get_db_file_path(cls, category: str, filename: str) -> str:
        return os.path.join(cls.get_db_path(), category, filename)

    @classmethod
    def get_article_views_db_path(cls) -> str:
        return cls.get_db_file_path('content', 'article_views.json')

    @classmethod
    def get_www_path(cls) -> str:
        """
        Get the directory that stores static site deployments.
        """
        www_path = cls.get_settings().www_path
        return cls.get_abs_path(www_path)
