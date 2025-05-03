
from typing import Literal

from arkalos import router

from app.domains.example.example import Example

type ChartType = Literal['bar']|Literal['pie']|Literal['line']|Literal['scatter']|Literal['area']

@router.get('/dashboard-chart')
async def chart(type: ChartType = 'bar'):
    example = Example()
    return example.chartSpec(type)
