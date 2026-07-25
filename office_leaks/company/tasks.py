import logging
import json
from huey.contrib.djhuey import periodic_task
from huey import crontab
from core.redis_client import get_redis_client

logger = logging.getLogger(__name__)

REDIS_KEY_TOP_RATED = "company:top_rated"

@periodic_task(crontab(hour='*/12', minute='0'))
def update_top_rated_companies():
    """
    Periodic task that runs every 12 hours.
    It retrieves the top-rated companies from the database,
    deletes the old top-rated key in Redis, and stores the new list.
    """
    logger.info("Starting update_top_rated_companies task...")
    try:
        # Lazy import of Repository layer to avoid circular dependencies during worker startup
        from company.db.repositories.company_repo import CompanyRepo
        
        # Query top 10 companies by current_rate in descending order
        companies = CompanyRepo.get_top_rated_companies(limit=10)
        
        # Serialize the companies data using list comprehension
        company_list = [
            {
                "id": company.id,
                "creation": company.creation.isoformat() if company.creation else None,
                "name": company.name,
                "address": company.address,
                "industry": company.industry,
                "logo": company.logo,
                "founded_at": str(company.founded_at) if company.founded_at else None,
                "website": company.website,
                "linkedin": company.linkedin,
                "instagram": company.instagram,
                "facebook": company.facebook,
                "current_rate": company.current_rate,
            }
            for company in companies
        ]
        if company_list:
            r = get_redis_client()
            
            # Put new top rated serialized data directly (implicit overwrite prevents race conditions)
            serialized_data = json.dumps(company_list)
            r.set(REDIS_KEY_TOP_RATED, serialized_data, ex=13 * 3600)
            
            logger.info(f"Successfully updated top rated companies in Redis: {len(company_list)} companies cached under key '{REDIS_KEY_TOP_RATED}'.")
            return len(company_list)
        return 0
    except Exception as e:
        logger.error(f"Error updating top rated companies in Redis: {e}", exc_info=True)
        raise
