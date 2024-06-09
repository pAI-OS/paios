import json
from starlette.responses import JSONResponse

def parse_pagination_params(filter=None, range=None, sort=None):
    try:
        # Parse range parameter
        if range:
            range_list = json.loads(range)
            if isinstance(range_list, list) and len(range_list) == 2:
                offset, limit = range_list
                limit = limit - offset + 1
            else:
                return JSONResponse({"error": "Invalid range format"}, status_code=400)
        else:
            offset, limit = 0, 100

        # Parse sort parameter
        if sort:
            sort_list = json.loads(sort)
            if isinstance(sort_list, list) and len(sort_list) == 2:
                sort_by, sort_order = sort_list
            else:
                return JSONResponse({"error": "Invalid sort format"}, status_code=400)
        else:
            sort_by, sort_order = None, 'asc'

        # Parse filter parameter
        if filter:
            filters = json.loads(filter)
        else:
            filters = None

        return offset, limit, sort_by, sort_order, filters

    except (ValueError, TypeError):
        return JSONResponse({"error": "Invalid query parameter format"}, status_code=400)
