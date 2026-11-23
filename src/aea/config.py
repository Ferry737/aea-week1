"""Week-1 run configuration. Frozen and fully serializable."""

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RunConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    seed: int
    tick_minutes: int = 1
    agents: int = Field(default=5, gt=0)
    ticks: int = Field(default=100, gt=0)
    money_supply_minor: int = Field(default=1_000_000, gt=0)
    wage_minor: int = Field(default=100, gt=0)
    consume_minor: int = Field(default=50, gt=0)
    consume_probability: float = Field(default=0.30, ge=0.0, le=1.0)
    reserve_minor: int = Field(default=1_000, ge=0)
    currency: str = "CRD"

    @model_validator(mode="after")
    def supply_covers_one_wage(self) -> "RunConfig":
        if self.money_supply_minor < self.wage_minor:
            raise ValueError("money_supply_minor must cover at least one wage")
        return self
