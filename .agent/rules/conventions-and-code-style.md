---
trigger: always_on
---

# Python Conventions
* Use uv for dependency management and running python code
  * The default python version is 3.12, so be sure to use newer style type hinting (e.g. dict instead of Dict) and consider other modern python features. Use type hinting for all function signatures.
* Use pytest for unit tests

# General Code Conventions
* Write clean, readable code with an experienced dev reviewer in mind. Keep functions small and do not give them too many responsibilities.
* Minimize comments, only use in code where one cannot derive the reason for an implementation decision or where it is necessary (e.g. public facing API in open source library). Do not restate the code in comments.

# System Info
This project is on a 2020 Apple Macbook Air with an M1 chip running MacOSX Monterey