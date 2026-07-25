from django.db import models
from django.utils.translation import gettext_lazy as _

class CompanyIndustry(models.TextChoices):
    # --- Technology & Media ---
    SOFTWARE_DEV = 'SOFTWARE_DEV', _('Software Development & AI')
    IT_SERVICES = 'IT_SERVICES', _('IT Services & Consulting')
    INTERNET_SAAS = 'INTERNET_SAAS', _('Internet & SaaS Platforms')
    TELECOM = 'TELECOM', _('Telecommunications & Networking')
    CYBERSECURITY = 'CYBERSECURITY', _('Cybersecurity')
    GAME_DEV = 'GAME_DEV', _('Game Development')
    MEDIA_PROD = 'MEDIA_PROD', _('Media Production & Content')
    
    # --- Financial Services ---
    BANKING = 'BANKING', _('Banking & Financial Institutions')
    INVESTMENT = 'INVESTMENT', _('Investment & Asset Management')
    FINTECH = 'FINTECH', _('Financial Technology (FinTech)')
    INSURANCE = 'INSURANCE', _('Insurance')
    VENTURE_CAPITAL = 'VENTURE_CAPITAL', _('Venture Capital & Private Equity')

    # --- Professional Services ---
    ACCOUNTING = 'ACCOUNTING', _('Accounting & Auditing')
    CONSULTING = 'CONSULTING', _('Management Consulting')
    LEGAL = 'LEGAL', _('Legal Services')
    HR_RECRUITING = 'HR_RECRUITING', _('Human Resources & Recruiting')
    MARKETING_ADV = 'MARKETING_ADV', _('Marketing, Advertising & PR')
    DESIGN_UX = 'DESIGN_UX', _('Design & UI/UX')

    # --- Healthcare & Pharma ---
    HOSPITALS = 'HOSPITALS', _('Hospitals & Medical Care')
    PHARMA = 'PHARMA', _('Pharmaceuticals')
    MEDICAL_DEVICES = 'MEDICAL_DEVICES', _('Medical Devices')
    BIOTECH = 'BIOTECH', _('Biotechnology & Research')

    # --- Manufacturing & Industrial ---
    MANUFACTURING = 'MANUFACTURING', _('General Manufacturing')
    AUTOMOTIVE = 'AUTOMOTIVE', _('Automotive & Vehicles')
    AEROSPACE = 'AEROSPACE', _('Aerospace & Defense')
    ELECTRONICS = 'ELECTRONICS', _('Electronics & Appliances')
    CHEMICALS = 'CHEMICALS', _('Chemicals & Petrochemicals')
    TEXTILES = 'TEXTILES', _('Textiles, Apparel & Fashion')
    FURNITURE_MFG = 'FURNITURE_MFG', _('Furniture & Wood Product Manufacturing')

    # --- Retail & Commerce ---
    E_COMMERCE = 'E_COMMERCE', _('E-Commerce')
    RETAIL = 'RETAIL', _('Retail Stores & Malls')
    WHOLESALE = 'WHOLESALE', _('Wholesale & Distribution')
    FMCG = 'FMCG', _('Fast-Moving Consumer Goods (FMCG)')
    FURNITURE_RETAIL = 'FURNITURE_RETAIL', _('Furniture & Home Furnishings Retail')

    # --- Construction & Real Estate ---
    CONSTRUCTION = 'CONSTRUCTION', _('Construction & Civil Engineering')
    REAL_ESTATE = 'REAL_ESTATE', _('Real Estate Development & Brokerage')
    ARCHITECTURE = 'ARCHITECTURE', _('Architecture & Urban Planning')

    # --- Logistics & Transport ---
    LOGISTICS = 'LOGISTICS', _('Logistics & Supply Chain')
    TRANSPORTATION = 'TRANSPORTATION', _('Freight & Transportation')
    AVIATION = 'AVIATION', _('Airlines & Aviation Services')

    # --- Energy & Mining ---
    OIL_GAS = 'OIL_GAS', _('Oil & Gas')
    RENEWABLE_ENERGY = 'RENEWABLE_ENERGY', _('Renewable Energy & Environment')
    UTILITIES = 'UTILITIES', _('Utilities (Power, Water, Waste)')
    MINING_METALS = 'MINING_METALS', _('Mining & Metals')

    # --- Hospitality & Entertainment ---
    HOSPITALITY = 'HOSPITALITY', _('Hotels, Tourism & Hospitality')
    FOOD_BEVERAGE = 'FOOD_BEVERAGE', _('Restaurants & Food Services')
    ENTERTAINMENT = 'ENTERTAINMENT', _('Entertainment, Arts & Gaming')
    SPORTS = 'SPORTS', _('Sports & Fitness')

    # --- Education ---
    HIGHER_EDUCATION = 'HIGHER_EDUCATION', _('Higher Education & Universities')
    K12_EDUCATION = 'K12_EDUCATION', _('Primary & Secondary Education')
    E_LEARNING = 'E_LEARNING', _('E-Learning & EdTech')

    # --- Government & Non-Profit ---
    GOVERNMENT = 'GOVERNMENT', _('Government & Public Sector')
    NON_PROFIT = 'NON_PROFIT', _('NGOs & Non-Profit Organizations')
    INTERNATIONAL_AFFAIRS = 'INTERNATIONAL_AFFAIRS', _('International Affairs & Diplomacy')

    # --- Agriculture ---
    AGRICULTURE = 'AGRICULTURE', _('Agriculture, Livestock & Forestry')

    # --- Other ---
    OTHER = 'OTHER', _('Other Industries')


