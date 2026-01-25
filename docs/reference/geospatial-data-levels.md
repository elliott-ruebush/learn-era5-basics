# Geospatial Data Levels 
[NASA EOS Article](https://www.earthdata.nasa.gov/learn/earth-observation-data-basics/data-processing-levels)

What kinds of geospatial data are out there? How do we get from a satellite orbiting the earth and broadcasting some sensor outputs to a prediction for the temperature in Chicago tomorrow?

There are obviously whole fields of science and modeling behind that second question, but let's think briefly about the hierarchy of geospatial data to start. NASA clearly outlines the generally accepted levels in an article from their Earth Observing System (EOS) team. Below are my brief attempts at summarizing each level (see NASA's article for a more robust explanation).

#### Level 0
Straight-up bytes in a signal from your favorite satellite

#### Level 1
Raw sensor with a few annotations/adjustments

#### Level 2
Raw data, but converted to geophysical variables (e.g. your L1 thermal infrared sensor output could be converted to a temperature value)

#### Level 3
Geophysical variables on a nice, uniform grid and timescale. Friendly level for analysis!

#### Level 4
Derived or modeled output based on lower level data
