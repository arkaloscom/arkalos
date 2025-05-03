
from fastapi.responses import Response as FastAPIResponse, HTMLResponse, JSONResponse

def response(data=None, status_code: int = 200):
    return Response.json(data, status_code)

class Response(FastAPIResponse):
    
    @staticmethod
    def json(data=None, status_code: int = 200):
        return JSONResponse(content=data, status_code=status_code)
