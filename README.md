# FreedomOS
| main  | dev |
| ----- | --- |
| [![CI Ouroboros (main)](https://github.com/therubic-canada/FreedomOS/actions/workflows/ci-ouroboros.yml/badge.svg?branch=main)](https://github.com/therubic-canada/FreedomOS/actions/workflows/ci-ouroboros.yml?query=branch%3Amain) | [![CI Ouroboros (dev)](https://github.com/therubic-canada/FreedomOS/actions/workflows/ci-ouroboros.yml/badge.svg?branch=dev)](https://github.com/therubic-canada/FreedomOS/actions/workflows/ci-ouroboros.yml?query=branch%3Adev) |
| [![CI Client (main)](https://github.com/therubic-canada/FreedomOS/actions/workflows/ci-client.yml/badge.svg?branch=main)](https://github.com/therubic-canada/FreedomOS/actions/workflows/ci-client.yml?query=branch%3Amain) | [![CI Client (dev)](https://github.com/therubic-canada/FreedomOS/actions/workflows/ci-client.yml/badge.svg?branch=dev)](https://github.com/therubic-canada/FreedomOS/actions/workflows/ci-client.yml?query=branch%3Adev) |
| [![Coverage (main)](../assets/badges/main/coverage.svg)](https://miniature-chainsaw-73orq2g.pages.github.io/coverage_reports/main/) | [![Coverage (dev)](../assets/badges/dev/coverage.svg)](https://miniature-chainsaw-73orq2g.pages.github.io/coverage_reports/dev/) |

## Overview
FreedomOS is a platform allowing interfacing between a human or computer with The Rubic's FreedomPick robot. It includes a [frontend](client) allowing users to manually send requests and monitor the robot. It also includes a message passing middleware called [ouroboros](ouroboros) which handles communication between the frontend, the database, and the robot.
