from fastapi import Request

from saleor_app.saleor.exceptions import IgnoredPrincipalError


class IgnoredIssuingPrincipalChecker:
    def __init__(self, principal_ids: list[str], raise_exception: bool = True):
        self.principal_ids = principal_ids
        self.raise_exception = raise_exception

    async def __call__(self, request: Request):
        json_data = await request.json()
        for payload in json_data:
            if (
                (meta := payload.get("meta"))
                and meta["issuing_principal"]["id"] in self.principal_ids
                and self.raise_exception
            ):
                raise IgnoredPrincipalError(self.principal_ids)
