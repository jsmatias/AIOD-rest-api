# Questions 

1. End point `platforms/{platform}/datasets/v1/` should return same as `/datasets/v1/` when set `platform=zenodo` as we just have datasets from zenodo atm?
   ```bash
   curl -X 'GET' \
   'http://localhost/platforms/zenodo/datasets/v1?schema=aiod&offset=0&limit=100' \
   -H 'accept: application/json'
   ```

2. `GET` endpoint `platforms/{platform}/datasets/v1/` returns `id=10405` as one of the elements, but when I try `platforms/{platform}/datasets/v1/10405` it says 404 not found. 
    ```
        {
            "detail": "Dataset '10405' of 'zenodo' not found in the database."
        }
    ```

3. ✅ Data url. In an example of a call `/datasets/v1/{identifier}/`, the url of the data can be found in the distribution:
    ```json
    ...
    "distribution": [
        {
        "platform": "example",
        "platform_identifier": "1",
        "checksum": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "checksum_algorithm": "sha256",
        "copyright": "2010-2020 Example Company. All rights reserved.",
        "content_url": "https://www.example.com/dataset/file.csv",
        "content_size_kb": 10000,
        "date_published": "2022-01-01T15:15:00.000",
        "description": "Description of this file.",
        "encoding_format": "text/csv",
        "name": "Name of this file.",
        "technology_readiness_level": 1
        }
    ],
    ...
    ```
    But for an actual call, `distribution` seems to be always empty. Should we get the url from another place? For ex. I can find this info in a JSON from the `same_as` url from zenodo.

4. Regarding the AIAssets: 
   1. These AIAssets are all the models that inherit the `AIAsset` class in https://github.com/aiondemand/AIOD-rest-api/blob/develop/src/database/model/ai_asset/ai_asset.py, right? For example, `datasets`, `case_study`, `computational_asset`, etc.
   2. Then, all the AIAssets should have the endpoints to retrieve the actual data: `api/<aiasset>/v1/{identifier}/data` and `api/<aiasset>/v1/{identifier}/data/{distribution_idx}`, correct?  
5. Regarding the routers: I see that all the models (i.e. `platforms`, `case_studies`, `computational_assets`, etc.) are routed with the same end points, by inheriting the `ResourceRouter` class from https://github.com/aiondemand/AIOD-rest-api/blob/develop/src/routers/resource_router.py. And I also see that there is n `AIAssetRouter` class in 