import os
import sys
import uuid
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from core import Logger, ProjectConfig
from storage.cache.website.article_index import ArticleIndexStore
from storage.resource.website.article import ArticleResourceStore
from typedef import ArticleDocument

ARTICLES_DIR = ProjectConfig.get_articles_path()


def _normalize_article_path(path: str) -> str:
    return os.path.normpath(path).replace('\\', '/').replace(os.sep, '/')


def sync_file(file_path: str):
    """同步单个 Markdown 文件的元数据到 JSON 索引（不存 content）"""
    doc: ArticleDocument = ArticleResourceStore.get_file_doc(file_path)
    if not doc:
        Logger.info(f"❗ 无法处理文件: {file_path}")
        return
    entry = {'id': doc['id'], 'path': doc['path'], 'meta': doc['meta']}
    action = '更新' if ArticleIndexStore.upsert(doc['id'], entry) else '插入'
    Logger.info(f"✔ {action} 文件: {doc['path']}")


def get_markdown_paths() -> set[str]:
    """获取当前文章目录下所有 Markdown 文件的相对路径"""
    paths = set()
    for root, _, files in os.walk(ARTICLES_DIR):
        for filename in files:
            if not filename.lower().endswith('.md'):
                continue
            rel = os.path.relpath(os.path.join(root, filename), ARTICLES_DIR)
            paths.add(_normalize_article_path(rel))
    return paths


def prune_missing_articles(existing_paths: set[str]) -> int:
    """删除数据库中已不存在于文件系统的文章记录"""
    removed_articles = ArticleIndexStore.prune_paths(existing_paths, _normalize_article_path)
    for article_id, removed in removed_articles:
        Logger.info(f"✖ 删除失效记录: {removed.get('path', article_id)}")
    return len(removed_articles)


class MarkdownEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.md'):
            Logger.info(f"检测到新文件: {event.src_path}")
            sync_file(event.src_path)

    def on_modified(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.md'):
            Logger.info(f"检测到修改: {event.src_path}")
            sync_file(event.src_path)

    def on_moved(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.md'):
            Logger.info(f"检测到重命名: {event.src_path} -> {event.dest_path}")
            sync_file(event.dest_path)
            rel = os.path.relpath(event.src_path, ARTICLES_DIR)
            pid = uuid.uuid5(uuid.NAMESPACE_URL, rel).hex[:16]
            if ArticleIndexStore.delete(pid):
                Logger.info(f"✖ 删除旧记录: {rel}")

    def on_deleted(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.md'):
            rel = os.path.relpath(event.src_path, ARTICLES_DIR)
            pid = uuid.uuid5(uuid.NAMESPACE_URL, rel).hex[:16]
            if ArticleIndexStore.delete(pid):
                Logger.info(f"✖ 删除记录: {rel}")


def initial_sync():
    """首次启动时同步已有文件，并清理已不存在的数据库记录"""
    Logger.info("开始初次全量同步...")
    count = 0
    for root, _, files in os.walk(ARTICLES_DIR):
        for f in files:
            if f.lower().endswith('.md'):
                sync_file(os.path.join(root, f))
                count += 1

    pruned_count = prune_missing_articles(get_markdown_paths())
    Logger.info(f"初次同步完成，共同步 {count} 个文件，清理 {pruned_count} 条失效记录。")


def start_watch(isWatch: bool = True):
    """启动文件监控服务"""
    if not os.path.isdir(ARTICLES_DIR):
        Logger.info(f"目录不存在: {ARTICLES_DIR}")
        sys.exit(1)

    initial_sync()

    if not isWatch:
        Logger.info("非监控模式，已完成初次同步。")
        return

    Logger.info("开始监控目录变动，按 Ctrl+C 停止")
    event_handler = MarkdownEventHandler()
    observer = Observer()
    observer.schedule(event_handler, ARTICLES_DIR, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        Logger.info("监控停止，退出中...")
        observer.stop()
    observer.join()
    Logger.info("Bye!")
