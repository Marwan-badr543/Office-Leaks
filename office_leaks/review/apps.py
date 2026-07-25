import logging
import os
from django.apps import AppConfig

logger = logging.getLogger(__name__)


class ReviewConfig(AppConfig):
    name = 'review'

    def ready(self):
        """
        Run update_trending_categories_task on server startup to populate Redis cache
        immediately instead of waiting for the 12-hour periodic schedule.
        
        The RUN_MAIN check prevents double-execution in Django's dev server
        which imports modules twice (once for the reloader, once for the main process).
        """
        run_main = os.environ.get('RUN_MAIN')
        if run_main == 'true' or run_main is None:
            try:
                from review.tasks import update_trending_categories_task
                # Call directly (not as Huey task) so it runs synchronously on startup
                update_trending_categories_task.call_local()
                logger.info("Successfully ran update_trending_categories_task on server startup.")
            except Exception as e:
                # Non-fatal: periodic task will catch up; don't crash server startup
                logger.warning(f"Failed to run startup task update_trending_categories_task: {e}")
