from pydantic import BaseModel

class Config(BaseModel):
    furryhub_apikey: str # = "3775698293_ekac_zhuiyeapi_furryhub_AC7n4"  # 添加默认值作为回退方案