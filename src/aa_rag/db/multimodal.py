from typing import Optional

from pydantic import Field

from aa_rag.oss import OSSStoreInitParams


class StoreImageParams(OSSStoreInitParams):
    image: Optional[str] = Field(default=None, description="Base64 encoded image.")
    img_desc: Optional[str] = Field(
        default=None, description="The description of image."
    )
