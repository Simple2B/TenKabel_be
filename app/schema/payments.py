from pydantic import BaseModel

from app import schema as s


class PaymentTab(BaseModel):
    total_earnings: float
    money_currency: str = "$"

    unpaid_payments: float
    approve_payments: float
    send_payments: float

    unpaid_commissions: float
    approve_commissions: float
    send_commissions: float


class Payment(BaseModel):
    job_id: int
    job_uuid: str
    job_name: str
    job_payment: int
    status: s.enums.PaymentStatus


class Commission(BaseModel):
    job_id: int
    job_uuid: str
    job_name: str
    job_commission: int
    status: s.enums.PaymentStatus


class PaymentList(BaseModel):
    payments: list[Payment]


class CommissionList(BaseModel):
    commissions: list[Commission]
