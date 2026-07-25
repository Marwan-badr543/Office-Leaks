import logging
import os
from django.apps import AppConfig

logger = logging.getLogger(__name__)


class CompanyConfig(AppConfig):
    name = 'company'

    def ready(self):
        """
        Run update_top_rated_companies on server startup to populate Redis cache
        immediately instead of waiting for the 12-hour periodic schedule.
        
        The RUN_MAIN check prevents double-execution in Django's dev server
        which imports modules twice (once for the reloader, once for the main process).
        """
        run_main = os.environ.get('RUN_MAIN')
        if run_main == 'true' or run_main is None:
            try:
                from core.redis_client import get_redis_client
                r = get_redis_client()
                r.flushall()
                logger.info("Successfully flushed all Redis cache on server startup.")
            except Exception as e:
                logger.warning(f"Failed to flush Redis on server startup: {e}")

            try:
                from company.tasks import update_top_rated_companies
                # Call directly (not as Huey task) so it runs synchronously on startup
                update_top_rated_companies.call_local()
                logger.info("Successfully ran update_top_rated_companies on server startup.")
            except Exception as e:
                # Non-fatal: periodic task will catch up; don't crash server startup
                logger.warning(f"Failed to run startup task update_top_rated_companies: {e}")
