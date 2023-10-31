from fastapi.responses import Response
from http import HTTPStatus
from httpx import AsyncClient
from typing import Literal
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.engine import Engine

from .resource_router import ResourceRouter


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
            """Retrieve a distribution of the actual data for a dataset
            identified by its identifier."""
            # 1. Get resource from id
            metadata = self.get_resource(
                engine=engine, identifier=identifier, schema=schema, platform=None
            )
            # 2. get the url filed pointing to the actual data
            distribution = metadata.distribution  # type:ignore
            # print(distribution)
            if distribution_idx >= len(distribution):
                raise HTTPException(
                    status_code=HTTPStatus.NOT_FOUND, detail="Distribution not found!"
                )

            if distribution[distribution_idx].content_url:
                url = distribution[distribution_idx].content_url
                encoding_format = distribution[distribution_idx].encoding_format
                filename = distribution[distribution_idx].name

                # print(url)
                # print(encoding_format)
                # print(filename)

            else:
                raise HTTPException(
                    status_code=HTTPStatus.NOT_FOUND, detail="URL to download data not found!"
                )

            # import requests

            # url = metadata.same_as
            # response = requests.get(url, allow_redirects=True)
            # if response.ok:
            #     url = response.json()["files"][0]["links"]["download"]
            #     filename = response.json()["files"][0]["filename"]
            #     encoding_format = "text/csv"
            #     print(url)
            # else:
            #     raise HTTPException(
            #         status_code=response.status_code,
            # detail=f"Failed to fetch metadata from {url}"
            #     )

            try:
                async with AsyncClient() as client:
                    response = await client.get(url)

                if response.status_code != status.HTTP_200_OK:
                    raise HTTPException(
                        status_code=response.status_code, detail=f"Failed to fetch data from {url}"
                    )

                content = response.content
                headers = {
                    "Content-Disposition": f"attachment; filename={filename}",
                    "Content-Type": f"{encoding_format}",
                }
                return Response(content=content, headers=headers)

            except Exception as exc:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Unexpected exception while processing your request. {exc}",
                ) from exc

        async def get_resource_data_default(
            identifier: str,
            schema: Literal[tuple(self._possible_schemas)] = "aiod",  # type:ignore
        ):
            """Retrieve the first distribution (as default) of the actual data
            for a dataset identified by its identifier."""
            return await get_resource_data(identifier=identifier, schema=schema, distribution_idx=0)

        if default:
            return get_resource_data_default

        return get_resource_data
