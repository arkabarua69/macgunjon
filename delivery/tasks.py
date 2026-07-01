import logging
from celery import shared_task
from .services import expire_old_tokens

logger = logging.getLogger(__name__)


@shared_task
def cleanup_expired_tokens():
    count = expire_old_tokens()
    logger.info(f'Cleanup expired tokens task completed: {count} expired')
    return count
