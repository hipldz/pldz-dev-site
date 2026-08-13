from typedef import CommentRecord
from storage.db.website.comment import CommentRepository


class CommentService:
    @classmethod
    def get_all_comments_by_id(cls, article_id: str) -> list[CommentRecord]:
        return CommentRepository.get_all_comments_by_id(article_id)

    @classmethod
    def add_comment(cls, article_id: str, comment: CommentRecord, parent_id: str) -> bool:
        return CommentRepository.add_comment(article_id, comment, parent_id)

    @classmethod
    def delete_comment(cls, article_id: str, comment_id: str) -> bool:
        return CommentRepository.delete_comment(article_id, comment_id)
