import threading

if __name__ == '__main__':
    # 初始化 core 内的配置和日志
    from core import ProjectConfig, Logger
    settings = ProjectConfig.load_env()
    Logger.init_logger()
    for warning in settings.warnings:
        Logger.warning(f"配置提示: {warning}")
    Logger.info("Project configuration and logger initialized.")

    from storage.cache.website.image import ImageCacheStore
    removed_count, removed_bytes = ImageCacheStore.cleanup()
    if removed_count:
        Logger.info(f"Image cache cleanup: removed {removed_count} files ({removed_bytes} bytes)")

    # 直接调用 start_watch() 会阻塞主线程，使用线程可以避免这个问题
    from workers.website.article_indexer import start_watch
    threading.Thread(target=start_watch, args=(True,), daemon=True).start()

    # 创建管理员账户
    from services.identity.authorization import AuthorizationService
    AuthorizationService.init_admin()

    # 启动 fastapi 应用
    from routes import run_dev
    run_dev()
