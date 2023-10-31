from fastapi.responses import Response
from httpx import AsyncClient
from typing import Literal
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.engine import Engine

from .resource_router import ResourceRouter, _wrap_as_http_exception


class ResourceAIAssetRouter(ResourceRouter):
    def create(self, engine: Engine, url_prefix: str) -> APIRouter:
        version = f"v{self.version}"
        default_kwargs = {
            "response_model_exclude_none": True,
            "deprecated": self.deprecated_from is not None,
            "tags": [self.resource_name_plural],
        }

        router = self._create(engine, url_prefix)

        router.add_api_route(
            path=f"{url_prefix}/{self.resource_name_plural}/{version}/{{identifier}}/data",
            endpoint=self.get_resource_data_func(engine, default=True),
            name=self.resource_name,
            response_model=str,
            **default_kwargs,
        )

        router.add_api_route(
            path=f"{url_prefix}/{self.resource_name_plural}/{version}/{{identifier}}/data/"
            f"{{distribution_idx}}",
            endpoint=self.get_resource_data_func(engine, default=False),
            name=self.resource_name,
            response_model=str,
            **default_kwargs,
        )

        return router

    def get_resource_data_func(self, engine: Engine, default: bool):
        """
        Returns a function to download the actual data from resources.
        This function returns a function (instead of being that function directly) because the
        docstring and the variables are dynamic, and used in Swagger.
        """

        async def get_resource_data(
            identifier: str,
            distribution_idx: int,
            schema: Literal[tuple(self._possible_schemas)] = "aiod",  # type:ignore
        ):
            f"""Retrieve a distribution of the actual data for {self.resource_name}
            identified by its identifier."""
            # 1. Get resource from id
            metadata = self.get_resource(
                engine=engine, identifier=identifier, schema=schema, platform=None
            )
            # 2. get the url field from distribution pointing to the actual data
            distribution = metadata.distribution  # type:ignore
            if not distribution:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Distribution not found."
                )
            elif distribution_idx >= len(distribution):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Distribution index out of range.",
                )

            try:
                url = distribution[distribution_idx].content_url
                encoding_format = distribution[distribution_idx].encoding_format
                filename = distribution[distribution_idx].name

                async with AsyncClient() as client:
                    response = await client.get(url)

                content = response.content
                headers = {
                    "Content-Disposition": f"attachment; filename={filename}",
                    "Content-Type": f"{encoding_format}",
                }
                return Response(content=content, headers=headers)

            except Exception as exc:
                raise _wrap_as_http_exception(exc)

        async def get_resource_data_default(
            identifier: str,
            schema: Literal[tuple(self._possible_schemas)] = "aiod",  # type:ignore
        ):
            f"""Retrieve the first distribution (index 0 as default) of the actual data
            for a {self.resource_name} identified by its identifier."""
            return await get_resource_data(identifier=identifier, schema=schema, distribution_idx=0)

        if default:
            return get_resource_data_default

        return get_resource_data
