from datetime import datetime, timezone

from sqlalchemy import Column, Date, String, BigInteger, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

PP_TRACKING_TABLE_NAME = "pp_tracking"
RESOURCE_METRICS_TABLE_NAME = "resource_metrics"


class PPTracking(Base):
    __tablename__ = PP_TRACKING_TABLE_NAME
    date = Column(Date, primary_key=True)
    resource = Column(String, primary_key=True)
    total_harvest_pp = Column(BigInteger)
    total_base_pp_after_cap = Column(BigInteger)


class ResourceMetrics(Base):
    __tablename__ = RESOURCE_METRICS_TABLE_NAME

    date = Column(Date, primary_key=True)
    id = Column(String)  # assuming `id` is unique text/UUID
    token_symbol = Column(String, primary_key=True)

    resource_quantity = Column(Float, nullable=False)
    resource_volume = Column(Float, nullable=False)
    resource_volume_1 = Column(Float)
    resource_volume_30 = Column(Float)

    resource_price = Column(Float, nullable=False)

    dec_quantity = Column(Float, nullable=False)
    dec_volume = Column(Float, nullable=False)
    dec_volume_1 = Column(Float)
    dec_volume_30 = Column(Float)

    dec_price = Column(Float, nullable=False)

    total_shares = Column(Float, nullable=False)

    created_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_updated_date = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    dec_usd_value = Column(Float, nullable=False)
    grain_equivalent = Column(Float, nullable=False)
    factor = Column(Float, nullable=False)
