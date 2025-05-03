
from typing import Literal
from arkalos import router, Log

@router.get('/logs')
async def logs(
    type: Literal['error']|Literal['info'] = 'error', 
    month: str = '',
    page: int = 1
):
    data = Log.logger().readLog(type, month, page)
    page_count = Log.logger().readLogCountPages(type, month)
    if data is False:
        return {
        'data': [],
        'page_count': 0
    }
    return {
        'data': data,
        'page_count': page_count
    }
