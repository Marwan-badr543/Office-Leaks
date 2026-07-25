import logging
import json
import redis
import os
import datetime
from typing import Optional, Tuple
from groq import Groq
from tavily import TavilyClient
from django.db import transaction
from core.redis_client import get_redis_client
from core.exceptions import NotFoundError, ValidationError, ExternalServiceError
from core.storage import R2StorageService
from ..db.repositories.company_repo import CompanyRepo
from ..db.models import Company
from user.db.models import User

logger = logging.getLogger(__name__)


class CompanyAIDetails:
    def __init__(
        self,
        name: str,
        address: str,
        industry: str,
        founded_at: Optional[datetime.date] = None,
        website: Optional[str] = None,
        linkedin: Optional[str] = None,
        instagram: Optional[str] = None,
        facebook: Optional[str] = None,
        logo_url: Optional[str] = None,
    ) -> None:
        self.name = name
        self.address = address
        self.industry = industry
        self.founded_at = founded_at
        self.website = website
        self.linkedin = linkedin
        self.instagram = instagram
        self.facebook = facebook
        self.logo_url = logo_url


class CompanyServices():

    @classmethod
    def _fetch_company_data_from_ai(cls, company_name: str) -> CompanyAIDetails:
        groq_api_key = os.environ.get("GROQ_API_KEY")
        tavily_api_key = os.environ.get("TAVILY_API_KEY")
        if not groq_api_key:
            raise ValidationError("GROQ_API_KEY is not configured in environment.")
        if not tavily_api_key:
            raise ValidationError("TAVILY_API_KEY is not configured in environment.")

        try:
            tavily_client = TavilyClient(api_key=tavily_api_key)
            groq_client = Groq(api_key=groq_api_key)

            from ..db.model_choices import CompanyIndustry
            valid_industries = [choice[0] for choice in CompanyIndustry.choices]

            # 1. Search Tavily for company details
            search_query = f"Company '{company_name}' details: headquarters address, website, industry, logo url, founded date, linkedin, facebook, instagram"
            search_res = tavily_client.search(query=search_query, max_results=5)
            
            # Combine search results as context
            context = "\n\n".join([
                f"Source: {res.get('url')}\nContent: {res.get('content')}"
                for res in search_res.get('results', [])
            ])

            prompt = f"""
            You are a precise data extractor.
            Analyze the following web search results about the company '{company_name}':

            --- Context ---
            {context}
            --- End Context ---

            Extract details about the company and return them strictly in the following key-value format.
            Do not add any preamble, markdown blocks, conversation, or text other than the key-value list.
            If you cannot find any information about this company or it does not exist, reply with exactly: not found

            If the company exists, use this template:
            COMPANY_FOUND: TRUE
            NAME: <Exact company name, e.g. Google LLC>
            ADDRESS: <Headquarters address/location, e.g. Mountain View, CA, USA>
            INDUSTRY: <Classify the company into exactly one of these valid keys: {", ".join(valid_industries)}>
            FOUNDED_AT: <Founding date in YYYY-MM-DD format, or None if unknown>
            WEBSITE: <Website URL or None if unknown>
            LINKEDIN: <LinkedIn company page URL or None if unknown>
            INSTAGRAM: <Instagram profile URL or None if unknown>
            FACEBOOK: <Facebook page URL or None if unknown>
            LOGO_URL: <Direct logo image URL from search, or None if unknown>

            Rule: If any value is not found, reply with "None".
            """

            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama-3.3-70b-versatile",
            )
            text_resp = chat_completion.choices[0].message.content.strip()

            if "not found" in text_resp.lower() or "company_found: false" in text_resp.lower():
                raise NotFoundError("Company not found by AI.")

            lines = text_resp.split('\n')
            parsed_data = {}
            for line in lines:
                if ':' in line:
                    key, val = line.split(':', 1)
                    parsed_data[key.strip().upper()] = val.strip()

            def clean_val(k: str) -> Optional[str]:
                val = parsed_data.get(k)
                if not val or val.lower() == 'none' or val == '':
                    return None
                return val

            def clean_val_truncate(k: str, max_len: int = 100) -> Optional[str]:
                val = clean_val(k)
                if val and len(val) > max_len:
                    return val[:max_len]
                return val

            name = clean_val_truncate('NAME', 100) or company_name[:100]
            address = clean_val_truncate('ADDRESS', 300) or "Global"
            
            industry = clean_val('INDUSTRY')
            if not industry or industry not in valid_industries:
                industry = 'OTHER'

            founded_at = clean_val('FOUNDED_AT')
            valid_founded_date = None
            if founded_at:
                try:
                    valid_founded_date = datetime.datetime.strptime(founded_at, "%Y-%m-%d").date()
                except ValueError:
                    try:
                        year = int(founded_at.split('-')[0])
                        valid_founded_date = datetime.date(year, 1, 1)
                    except Exception:
                        valid_founded_date = None

            website = clean_val_truncate('WEBSITE', 100)
            linkedin = clean_val_truncate('LINKEDIN', 100)
            instagram = clean_val_truncate('INSTAGRAM', 100)
            facebook = clean_val_truncate('FACEBOOK', 100)
            logo_url = clean_val_truncate('LOGO_URL', 255)

            return CompanyAIDetails(
                name=name,
                address=address,
                industry=industry,
                founded_at=valid_founded_date,
                website=website,
                linkedin=linkedin,
                instagram=instagram,
                facebook=facebook,
                logo_url=logo_url
            )

        except NotFoundError:
            raise
        except Exception as e:
            logger.exception("Groq/Tavily API call failed")
            raise ExternalServiceError(f"Error calling AI: {str(e)}")

    @classmethod
    def get_or_create_company_with_ai(cls, company_name: str, user: User) -> Tuple[Company, bool]:
        if not company_name or not company_name.strip():
            raise ValidationError("Company name is required.")

        company_name = company_name.strip()

        existing_company = CompanyRepo.get_company_by_name_exact(company_name)
        if existing_company:
            return (existing_company, False)

        ai_details = cls._fetch_company_data_from_ai(company_name)

        company_data = {
            'name': ai_details.name,
            'address': ai_details.address,
            'industry': ai_details.industry,
            'founded_at': ai_details.founded_at,
            'website': ai_details.website,
            'linkedin': ai_details.linkedin,
            'instagram': ai_details.instagram,
            'facebook': ai_details.facebook,
            'logo': ai_details.logo_url,
            'user': user
        }

        with transaction.atomic():
            new_company = CompanyRepo.create_company(company_data)
            return (new_company, True)

    @staticmethod
    def create_company(validated_data):
        with transaction.atomic():
            return CompanyRepo.create_company(validated_data)

    @staticmethod
    def update_company(cmpny_id, cmpny_data):
        if not CompanyRepo.get_company_with_id(cmpny_id):
            raise NotFoundError(f"Company with id {cmpny_id} not found.")

        with transaction.atomic():
            return CompanyRepo.update_company(cmpny_id, cmpny_data)

    @staticmethod
    def delete_company(cmpny_id):
        company = CompanyRepo.get_company_with_id(cmpny_id)
        if not company:
            raise NotFoundError(f"Company with id {cmpny_id} not found.")
        
        with transaction.atomic():
            CompanyRepo.delete_company(company)
            return company

    @staticmethod
    def _get_top_rated_from_redis():
        try:
            r = get_redis_client()
            cached_data = r.get("company:top_rated")
            if not cached_data:
                return None
            return json.loads(cached_data)
        except (redis.RedisError, json.JSONDecodeError) as e:
            logger.error(f"Redis fetch failed: {e}")
            raise ExternalServiceError(f"ExternalServiceError in Redis read: {e}")

    @staticmethod
    def _map_dicts_to_companies(company_list):
        companies = []
        for c in company_list:
            companies.append(Company(
                id=c.get("id"),
                creation=c.get("creation"),
                name=c.get("name"),
                address=c.get("address"),
                industry=c.get("industry"),
                logo=c.get("logo"),
                founded_at=c.get("founded_at"),
                website=c.get("website"),
                linkedin=c.get("linkedin"),
                instagram=c.get("instagram"),
                facebook=c.get("facebook"),
                current_rate=c.get("current_rate")
            ))
        return companies

    @staticmethod
    def get_companies(page: int, page_size: int, filters: dict = None) -> dict:
        return CompanyRepo.get_companies(page, page_size, filters)

    @staticmethod
    def upload_company_logo(company_id, user, image_file):
        """
        Upload a logo for a company to R2.

        Validates:
        1. Company exists
        2. The requesting user owns the company (prevents unauthorized logo changes)
        3. Image passes type/size/magic-bytes validation (handled by R2StorageService)

        If the company already has a logo, the old one is deleted from R2
        after the new one is successfully uploaded and the DB is updated.
        """
        company = CompanyRepo.get_company_with_id(company_id)
        if not company:
            raise NotFoundError(f"Company with id {company_id} not found.")

        if company.user_id != user.id:
            raise ValidationError("You do not own this company.")

        old_filename = company.logo

        # Upload new image first — if validation or upload fails, nothing is changed
        new_filename = R2StorageService.upload_image(image_file)

        # Update DB
        CompanyRepo.update_company_logo(company_id, new_filename)

        # Delete old logo from R2 AFTER successful DB update
        if old_filename:
            R2StorageService.delete_image(old_filename)

        return new_filename

    @staticmethod
    def delete_company_logo(company_id, user):
        """
        Remove the company's logo from both R2 and the database.
        """
        company = CompanyRepo.get_company_with_id(company_id)
        if not company:
            raise NotFoundError(f"Company with id {company_id} not found.")

        if company.user_id != user.id:
            raise ValidationError("You do not own this company.")

        filename = company.logo
        if not filename:
            raise ValidationError("This company has no logo to delete.")

        # Clear DB first, then delete from R2
        CompanyRepo.update_company_logo(company_id, None)
        R2StorageService.delete_image(filename)

    @staticmethod
    def search_companies(name_search: str, limit: int = 10):
        if not name_search or not name_search.strip():
            return []
        return CompanyRepo.search_companies_by_name(name_search.strip(), limit)

    @staticmethod
    def get_top_and_trending() -> dict:
        """
        Retrieve the top 10 rated companies and top 6 trending categories.
        Reads from Redis cache with DB fallback if cache is empty or fails.
        """
        # 1. Fetch top rated companies from Redis or DB fallback
        try:
            top_rated = CompanyServices._get_top_rated_from_redis()
            if not top_rated:
                top_rated_objs = CompanyRepo.get_top_rated_companies(limit=10)
                top_rated = [
                    {
                        "id": c.id,
                        "creation": c.creation.isoformat() if c.creation else None,
                        "name": c.name,
                        "address": c.address,
                        "industry": c.industry,
                        "logo": c.logo,
                        "founded_at": str(c.founded_at) if c.founded_at else None,
                        "website": c.website,
                        "linkedin": c.linkedin,
                        "instagram": c.instagram,
                        "facebook": c.facebook,
                        "current_rate": c.current_rate,
                    }
                    for c in top_rated_objs
                ]
        except Exception as e:
            logger.error(f"Redis fetch or parsing for top rated companies failed: {e}")
            top_rated_objs = CompanyRepo.get_top_rated_companies(limit=10)
            top_rated = [
                {
                    "id": c.id,
                    "creation": c.creation.isoformat() if c.creation else None,
                    "name": c.name,
                    "address": c.address,
                    "industry": c.industry,
                    "logo": c.logo,
                    "founded_at": str(c.founded_at) if c.founded_at else None,
                    "website": c.website,
                    "linkedin": c.linkedin,
                    "instagram": c.instagram,
                    "facebook": c.facebook,
                    "current_rate": c.current_rate,
                }
                for c in top_rated_objs
            ]

        # 2. Fetch trending categories from Redis 
        try:
            from review.services.post import PostServices
            trending = PostServices._get_trending_topics_from_redis()
            if not trending:
                trending = None
        except Exception as e:
            logger.error(f"Redis fetch or parsing for trending topics failed: {e}")
            from review.db.repositories.post_repo import PostRepo
            trending_objs = PostRepo.get_trending_categories(limit=6)
            trending = [
                {
                    "category": item["category"],
                    "count": item["count"]
                }
                for item in trending_objs
            ]

        return {
            "top_rated": top_rated,
            "trending": trending
        }