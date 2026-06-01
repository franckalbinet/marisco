# Changelog

All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.10] - 2026-06-01

### Maintenance
- Migrated to nbdev3

---

## [1.0.9] - 2025-10-06

### New Features
- HELCOM handler: added station name in output
- TEPCO handler: added variable-length string variable type (e.g. station name), unit conversion, and export-to-CSV renaming
- Added `SMP_ID_PROVIDER` field to trace back original data provider sample IDs
- Added `station` field across all groups in CDL

### Bugs Squashed
- Fixed HELCOM detection limit assignment logic
- Fixed TEPCO value, unit, detection limit, and uncertainty remapping from column names

---

## [1.0.0] - 2025-02-18

### New Features
- New CLI command `maris_nc_to_csv`: converts NetCDF files to CSV ready for MARIS DB import
- New CLI command `maris_db_to_nc`: converts MARIS DB exports to NetCDF
- New CLI command `maris_to_nc`: encodes raw handler output to NetCDF
- Added capability to encode string variables in NetCDF output

---
