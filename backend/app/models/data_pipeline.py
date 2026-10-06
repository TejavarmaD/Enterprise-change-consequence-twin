from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models import Base


class DataPipeline(Base):
    __tablename__ = "data_pipelines"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_data_asset_id: Mapped[int | None] = mapped_column(
        ForeignKey("data_assets.id"),
        nullable=True,
    )
    output_data_asset_id: Mapped[int | None] = mapped_column(
        ForeignKey("data_assets.id"),
        nullable=True,
    )