# 🇪🇺AI-on-Demand Metadata Catalogue

This repository contains code and configurations for the AI-on-Demand Metadata Catalogue.
The metadata catalogue provides a unified view of AI assets and resources stored across the AI landscape.
It collects metadata from platforms such as [_Zendodo_](https://zenodo.org) and [_OpenML_](https://openml.org),
and is connected to European projects like [Bonsapps](https://bonsapps.eu) and [AIDA](https://www.i-aida.org).
Metadata of datasets, models, papers, news, and more from all of these sources is available through a REST API at [api.aiod.eu](https://api.aiod.eu/).

**🧑‍🔬 For most users:** 
Many users will only use the REST API indirectly, for example;
through [My Resources](https://github.com/aiondemand/AIOD-marketplace-frontend/) to browse assets,
through [RAIL](https://github.com/aiondemand/aiod-rail) to conduct ML experiments,
or through the [Python SDK](https://github.com/aiondemand/aiondemand) to access the metadata in Python scripts.
For documentation on how to use the REST API directly, visit the ["Using the API"](Using.md).

**🧑‍💻 For service developers:**
To use the metadata catalogue from your service, use the [Python SDK](https://github.com/aiondemand/aiondemand)
or use the REST API directly as detailed in the ["Using the API"](Using.md) documentation.

**🌍 Hosting:** For information on how to host the metadata catalogue, see the ["Hosting" documentation](Hosting.md).

**🧑‍🔧 API Development:** The ["Developer Guide"](developer/index.md) has information about the code in this repository and how to make contributions.

### Acknowledgement
Funded by the European Union 🇪🇺
