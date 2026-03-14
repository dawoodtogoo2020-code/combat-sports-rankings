from app.ingestion.scrapers.smoothcomp import SmoothCompIngester
from app.ingestion.scrapers.ajp import AjpIngester
from app.ingestion.scrapers.ibjjf import IbjjfIngester
from app.ingestion.scrapers.naga import NagaIngester
from app.ingestion.scrapers.grappling_industries import GrapplingIndustriesIngester
from app.ingestion.scrapers.adcc import AdccIngester

__all__ = [
    "SmoothCompIngester",
    "AjpIngester",
    "IbjjfIngester",
    "NagaIngester",
    "GrapplingIndustriesIngester",
    "AdccIngester",
]
