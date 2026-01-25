# ARCO and Modern Geospatial

There's some pretty sweet tooling out there for efficiently teasing out answers to big geospatial data problems without needing an [AWS Snowmobile](https://aws.amazon.com/blogs/aws/aws-snowmobile-move-exabytes-of-data-to-the-cloud-in-weeks/)* truck's trove of hard-drives locally to store the data.

## What is ARCO ([Article by Lobelia Earth](https://blog.lobelia.earth/arco-the-smartest-way-to-access-big-geospatial-data-eaf689eff3c9))
One of the acronyms that's gaining a lot of hype in the geospatial community these days is ARCO, which stands for Analysis-Ready, Cloud-Optimized.

### Analysis-Ready (AR)
Analysis-ready means that the data is cleaned, standardized, and ready to answer whatever research or business questions your heart desires.
* Dealing with non-AR data might involve processing raw satellite data, doing geographic projections, or merging non-uniform datasets.
* Dealing with AR data in a geospatial context means you can expect standard variables, time-scales, and latitude/longitude (and perhaps pressure levels in an atmospheric context).

### Cloud-Optimized (CO)
Cloud-optimized means that the data is stored in a format that makes data retrieval and processing across various different dimensions efficient.

#### Zarr and friends!
* A popular file format for cloud-optimized geospatial data is [Zarr](https://zarr.dev/), which structures "cubes" of data into smaller "chunks". E.g. if I have a 8x8 cube of data, I can decompose it into four 4x4 chunks. This generalizes to higher dimensions and meshes well with object storage systems common to cloud providers (e.g. Amazon S3).
* To further converge on an ecosystem where everything is cloud-optimized Zarr datacubes, one can make use of [VirtualiZarr](https://virtualizarr.readthedocs.io/en/stable/) (or its spiritual predecessor [Kerchunk](https://fsspec.github.io/kerchunk/)) to create "virtual" (zero-copy!) Zarr datacubes with chunks pointing directly to the relevant bytes of various other file formats like NetCDF, GRIB, and HDF5.
  * This virtual Zarr abstraction is powerful because it lets you build towards a unified cloud-native interface even when working with various different datasources that might not have the capability to migrate their source data to a cloud-native format.
  * Question to ponder: what about going the opposite way? What if I'm running legacy systems that expect different input formats? Can I cheaply convert Zarr to NetCDF and then run a model that expects NetCDF inputs?
* A relatively new option to further productionize cloud-optimized datacubes as a first-class database is an open-source technology called [Icechunk](https://icechunk.io/en/stable/overview/) which provides commit history and transaction guarantees. This is important because it makes auditing changes and executing rollbacks possible. Icechunk plays nicely alongside virtual Zarr files too. If I have an operational forecasting system, I'd ideally want my data to be robust to issues with models, partial failures, and the general suite of data integrity problems one can expect when running something in the real world.

---
\* *sidenote: where are these AWS Snowmobile trucks living these days...? And is a multi-petabyte climate-controlled storage container a valid combined winter camping/winter weather modeling setup...?*
