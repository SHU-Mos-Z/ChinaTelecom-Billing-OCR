# coding: utf-8
from sqlalchemy import Column, DateTime, Float, ForeignKey, String, text
from sqlalchemy.dialects.mysql import ENUM, TINYINT, YEAR
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Clas(Base):
    __tablename__ = 'class'

    class_id = Column(String(60, 'utf8_unicode_ci'), primary_key=True)
    class_name = Column(String(60, 'utf8_unicode_ci'), nullable=False)


class Worker(Base):
    __tablename__ = 'worker'

    worker_id = Column(String(60, 'utf8_unicode_ci'), primary_key=True)
    class_id = Column(ForeignKey('class.class_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    worker_name = Column(String(60, 'utf8_unicode_ci'), nullable=False)
    role = Column(ENUM('normal', 'class_manager', 'center_manager', 'system_manager'), nullable=False)
    pwd = Column(String(120, 'utf8_unicode_ci'), nullable=False)

    _class = relationship('Clas')


class ServiceRecord(Base):
    __tablename__ = 'service_record'

    service_record_id = Column(String(60, 'utf8_unicode_ci'), primary_key=True)
    service_name = Column(String(60, 'utf8_unicode_ci'), nullable=False)
    invoice_type = Column(ENUM('pdf', 'ofd', 'image'), nullable=False)
    service_time = Column(DateTime)
    upload_time = Column(DateTime)
    buyer_company_id = Column(String(60, 'utf8_unicode_ci'))
    seller_company_id = Column(String(60, 'utf8_unicode_ci'))
    buyer_company_name = Column(String(60, 'utf8_unicode_ci'))
    seller_company_name = Column(String(60, 'utf8_unicode_ci'))
    worker_id = Column(ForeignKey('worker.worker_id'), nullable=False, index=True)
    cost = Column(String(60, 'utf8_unicode_ci'), nullable=False)
    total = Column(Float, nullable=False)
    total_tax = Column(Float, nullable=False)
    is_exception = Column(TINYINT(1), nullable=False, server_default=text("'0'"))

    worker = relationship('Worker')


class WorkerQuotaMonthly(Base):
    __tablename__ = 'worker_quota_monthly'

    worker_id = Column(ForeignKey('worker.worker_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                       nullable=False)
    year_ = Column(YEAR(4), primary_key=True, nullable=False)
    quota_01 = Column(Float(16), nullable=False, server_default=text("'0.00'"))
    quota_02 = Column(Float(16), nullable=False, server_default=text("'0.00'"))
    quota_03 = Column(Float(16), nullable=False, server_default=text("'0.00'"))
    quota_04 = Column(Float(16), nullable=False, server_default=text("'0.00'"))
    quota_05 = Column(Float(16), nullable=False, server_default=text("'0.00'"))
    quota_06 = Column(Float(16), nullable=False, server_default=text("'0.00'"))
    quota_07 = Column(Float(16), nullable=False, server_default=text("'0.00'"))
    quota_08 = Column(Float(16), nullable=False, server_default=text("'0.00'"))
    quota_09 = Column(Float(16), nullable=False, server_default=text("'0.00'"))
    quota_10 = Column(Float(16), nullable=False, server_default=text("'0.00'"))
    quota_11 = Column(Float(16), nullable=False, server_default=text("'0.00'"))
    quota_12 = Column(Float(16), nullable=False, server_default=text("'0.00'"))

    worker = relationship('Worker')
