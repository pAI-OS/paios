from starlette.responses import JSONResponse
from backend.managers.LlmsManager import LlmsManager
from backend.pagination import parse_pagination_params
from backend.schemas import LlmSchema

class LlmsView:
    def __init__(self):
        self.llmm = LlmsManager()

    async def get(self, id: str):
        llm = await self.llmm.get_llm(id)
        if llm is None:
            return JSONResponse(headers={"error": "LLM not found"}, status_code=404)
        llm_schema = LlmSchema(id=llm.id, name=llm.name, full_name=f"{llm.provider}/{llm.name}",
                               provider=llm.provider, api_base=llm.api_base, is_active=llm.is_active)
        return JSONResponse(llm_schema.model_dump(), status_code=200)

    async def search(self, filter: str = None, range: str = None, sort: str = None):
        result = parse_pagination_params(filter, range, sort)
        if isinstance(result, JSONResponse):
            return result

        offset, limit, sort_by, sort_order, filters = result

        llms, total_count = await self.llmm.retrieve_llms(limit=limit, offset=offset, sort_by=sort_by, sort_order=sort_order, filters=filters)
        results = [LlmSchema(id=llm.id, name=llm.name, full_name=f"{llm.provider}/{llm.name}",
                             provider=llm.provider, api_base=llm.api_base,
                             is_active=llm.is_active)
                    for llm in llms]
        headers = {
            'X-Total-Count': str(total_count),
            'Content-Range': f'shares {offset}-{offset + len(llms) - 1}/{total_count}'
        }
        return JSONResponse([llm.model_dump() for llm in results], status_code=200, headers=headers)

    async def completion(self, id: str, body: dict):
        print("completion.  body: {}".format(body))
        messages = []
        if 'messages' in body and body['messages']:
            messages = body['messages']
        llm = await self.llmm.get_llm(id)
        if llm:
            print("Selected LLM is {}".format(llm.llm_name))
            response = self.llmm.completion(llm, messages)
            if response:
                return JSONResponse(response.model_dump(), status_code=200)
            else:
                return JSONResponse(status_code=400, content={"message": "Completion failed"})
        else:
            return JSONResponse(status_code=404, content={"message": "LLM not found"})
