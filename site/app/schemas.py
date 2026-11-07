import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class BouquetFilterParams(BaseModel):
    budget: Optional[str] = None          # '0-3500', '3500-5500', '5500-10000', '10000-15000', '15000-plus'
    size: Optional[str] = None            # 'compact', 'standard', 'large'
    palette: Optional[str] = None         # 'tender', 'vibrant', 'white', 'deep', 'seasonal'
    occasion: Optional[str] = None        # 'mom', 'friend', 'wife', 'birthday', 'just_because'
    ready_today: Optional[bool] = False   # True = только в наличии сегодня
    sort: Optional[str] = "popular"       # 'popular', 'price_asc', 'price_desc'


class LeadRequestSchema(BaseModel):
    bouquet_id: Optional[int] = None
    custom_reference_info: Optional[str] = None
    budget_range: Optional[str] = None
    budget_amount: Optional[int] = None
    size_code: Optional[str] = None
    palette: Optional[str] = None
    occasion: Optional[str] = None
    delivery_date: Optional[str] = "Сегодня"
    delivery_time_slot: Optional[str] = "Как можно скорее"
    customer_name: Optional[str] = Field(None, max_length=100)
    customer_phone: str = Field(..., example="+79161234567")
    delivery_type: str = Field("delivery", pattern="^(delivery|pickup)$")
    delivery_address: Optional[str] = None
    comment: Optional[str] = Field(None, max_length=1000)

    @field_validator("customer_phone")
    @classmethod
    def clean_and_validate_phone(cls, v: str) -> str:
        if not v:
            raise ValueError("Номер телефона обязателен")
        digits = re.sub(r"\D", "", v)
        if len(digits) == 11 and digits[0] in ("7", "8"):
            digits = "7" + digits[1:]
        elif len(digits) == 10:
            digits = "7" + digits
        else:
            raise ValueError("Пожалуйста, укажите корректный российский номер телефона")
        return f"+{digits}"
