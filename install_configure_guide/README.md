# MARIS Data Formats

The MARIS data is converted to a standardized CSV format for importing into the MARIS database using Open Refine. The standardized variable names for Open Refine are provided in Table 1, and a detailed description of each variable is given below. Additionally, MARIS data is available in NetCDF4 format. The standardized variable names for NetCDF4 are also provided in Table 1, with descriptions for each variable included below.

## Table 1: Standardized Variable Names (Open Refine and NetCDF)
| Friendly Name           | Open Refine Name    | NetCDF Name                    |
|-------------------------|---------------------|--------------------------------|
| Sample quality          | sampquality         |                                |
| Sample type ID          | samptype_id         | *Sample type included as netcdf.group* |
| Laboratory ID           | lab_id              |                                |
| Latitude                | latitude            | lat                            |
| Longitude               | longitude           | lon                            |
| Station                 | station             |                                |
| Sample lab code         | samplabcode         |                                |
| Profile ID              | profile_id          |                                |
| Transect ID             | transect_id         |                                |
| Sampling depth          | sampdepth           | smp_depth                      |
| Total depth             | totdepth            | tot_depth                      |
| Begin period            | begperiod           | time                           |
| End period              | endperiod           |                                |
| Nuclide ID              | nuclide_id          | nuclide                        |
| Detection               | detection           | detection_limit                |
| Activity                | activity            | value                          |
| Uncertainty             | uncertaint          | uncertainty                    |
| Unit ID                 | unit_id             | unit                           |
| Variable type           | vartype             |                                |
| Frequency               | freq                |                                |
| Range low detection     | rl_detection        |                                |
| Range low               | rangelow            |                                |
| Range upper             | rangeupp            |                                |
| Species ID              | species_id          | species                        |
| Biological group        |                     | bio_group                      |
| Taxon name              | Taxonname           |                                |
| Taxon reported name     | TaxonRepName        |                                |
| Common name             | Commonname          |                                |
| Taxon rank              | Taxonrank           |                                |
| Taxon database          | TaxonDB             |                                |
| Taxon database ID       | TaxonDBID           |                                |
| Taxon database URL      | TaxonDBURL          |                                |
| Body part ID            | bodypar_id          | body_part                      |
| Slice up                | sliceup             |                                |
| Slice down              | slicedown           |                                |
| Sediment type ID        | sedtype_id          | sed_type                       |
| Sediment reported name  | SedRepName          |                                |
| Volume                  | volume              |                                |
| Salinity                | salinity            | salinity                       |
| Temperature             | temperatur          | temperature                    |
| Filtered                | filtered            | filtered                       |
| Filter pore             | filtpore            |                                |
| Acidified               | acid                |                                |
| Oxygen                  | oxygen              |                                |
| Sample area             | samparea            |                                |
| Dry weight              | drywt               |                                |
| Wet weight              | wetwt               |                                |
| Percent weight          | percentwt           |                                |
| Sampling method ID      | sampmet_id          | sampling_method                |
| Drying method ID        | drymet_id           |                                |
| Preparation method ID   | prepmet_id          | preparation_method             |
| Counting method ID      | counmet_id          | counting_method                |
| Reference ID            | ref_id              |                                |
| Reference note          | refnote             |                                |
| Sample note             | sampnote            |                                |
| Measurement note        | measurenote         |                                |
| Good for export         | gfe                 |                                |


<h2 style="text-align: center;">Variable Descriptions</h2>

## Sample Quality  

### Description: 
Defines the quality of the sample. Examples include: Good (G), Caution (C), Fail (F).

### Lookup Table (LUT) in use:  
No.  

### Open Refine Variable Name: 
`sampquality`

### Open Refine Data Type:  
string

### NetCDF Variable Name:
Not included in NetCDF 

### NetCDF Data Type: 
Not included in NetCDF

---

## Sample Type ID

### Description:
In MARIS, samples are categorized by type into WATER, BIOTA, SEDIMENT, and SUSPENDED types. The NetCDF data format separates MARIS data into ‘NetCDF groups’ by the sample type. Open Refine formats MARIS data into separate CSV files by sample type.

- **SEAWATER** includes seawater and brackish water.
- **BIOTA** includes various types of biota.
- **SEDIMENT** includes various types of sediments.
- **SUSPENDED** includes various types of suspended matter.

### Lookup Table (LUT) in use:  
No.

### Open Refine Variable Name:
`samptype_id`

### Open Refine Data Type:
An integer value :
 - 1 : ``SEAWATER``
 - 2 : ``BIOTA``
 - 3 : ``SEDIMENT``
 - 4 : ``SUSPENDED``

### NetCDF Variable Name:
*Sample type is included as netcdf.group*

### NetCDF Data Type:
string

---

## Laboratory ID

### Description:
The Laboratory ID identifies the laboratory that processed the sample.

### Lookup Table (LUT) in use:
Yes, [dbo_lab.xlsx](https://github.com/franckalbinet/marisco/blob/main/nbs/files/lut/dbo_lab.xlsx)

### Open Refine Variable Name:
`lab_id`

### Open Refine Data Type:
An integer value (the 'id' defined in the LUT).

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---

## Latitude Decimal

### Description:
Latitude in decimal format (DDD.DDDDD°) with ranges from -90° to 90°.

### Lookup Table (LUT) in use:
No

### Open Refine Variable Name:
`latitude`

### Open Refine Data Type:
Float with values between -90° to 90°.

### NetCDF Variable Name:
`lat`

### NetCDF Data Type:
Float with values between -90° to 90°.

---

## Longitude Decimal

### Description:
Longitude in decimal format (DDD.DDDDD°) with ranges from -180° to 180°.

### Lookup Table (LUT) in use:
No

### Open Refine Variable Name:
`longitude`

### Open Refine Data Type:
Float with values between -180° to 180°.

### NetCDF Variable Name:
`lon`

### NetCDF Data Type:
Float with values between -180° to 180°.

---

## Station

### Description:
The name of the station where the sample was collected.

### Lookup Table (LUT) in use:
No.

### Open Refine Variable Name:
`station`

### Open Refine Data Type:
string

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---

## Sample Lab Code

### Description:
The data provider's sample laboratory code should be stored exactly as provided, without any modifications.

### Lookup Table (LUT) in use:
No.

### Open Refine Variable Name:
`samplabcode`

### Open Refine Data Type:
string

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---

## Profile ID

### Description:
Profile ID is provided as is by the data provider and is an identifier for linking data which are part of a sequence, i.e., a vertical profile.

### Lookup Table (LUT) in use:
No.

### Open Refine Variable Name:
`profile_id`

### Open Refine Data Type:
string

### NetCDF Variable Name:
Not defined in NetCDF.

### NetCDF Data Type:
Not defined in NetCDF.

---

## Transect ID

### Description:
Transect ID is provided as is by the data provider and is an identifier for linking data which are part of a sequence, i.e., a horizontal transect.

### Lookup Table (LUT) in use:
No.

### Open Refine Variable Name:
`transect_id`

### Open Refine Data Type:
string

### NetCDF Variable Name:
Not defined in NetCDF.

### NetCDF Data Type:
Not defined in NetCDF.

---

## Sampling Depth

### Description:
Depth from the water surface in meters at which the sample was taken. A value of "0" indicates that the sample was collected at the surface. A value of "-1" indicates that sample depth information is not available.

### Lookup Table (LUT) in use:
No

### Open Refine Variable Name:
`sampdepth`

### Open Refine Data Type:
Float

### NetCDF Variable Name:
`smp_depth`

### NetCDF Data Type:
Float

---

## Total Depth

### Description:
Total water column depth in meters (m).

### Lookup Table (LUT) in use:
No

### Open Refine Variable Name:
`totdepth`

### Open Refine Data Type:
float

### NetCDF Variable Name:
`tot_depth`

### NetCDF Data Type:
float

---

## Begin Period

### Description:
'Begin Period' refers to the date when the collection of sample(s) began. If only a year is provided in the dataset, set the date to January 1st of that year (e.g., 2024 becomes 2024-01-01). If both a year and month are provided, set the date to the first day of that month (e.g., May 2024 becomes 2024-05-01). Date format of yyyy-mm-dd.

### Lookup Table (LUT) in use:
No

### Open Refine Variable Name:
`begperiod`

### Open Refine Data Type:
DATETIME string in the format (yyyy-mm-dd hh:mm:ss)

### NetCDF Variable Name:
`time`

### NetCDF Data Type:
DATETIME string in the format (yyyy-mm-dd hh:mm:ss)

---

## End Period

### Description:
'End Period' refers to the date when the collection of sample(s) ended. If only a year is provided in the dataset, set the date to January 1st of that year (e.g., 2024 becomes 2024-01-01). If both a year and month are provided, set the date to the first day of that month (e.g., May 2024 becomes 2024-05-01). Date format of yyyy-mm-dd.

### Lookup Table (LUT) in use:
No

### Open Refine Variable Name:
`endperiod`

### Open Refine Data Type:
DATETIME string in the format (yyyy-mm-dd hh:mm:ss)

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---

## Nuclide ID

### Description:
Identifier for a specific nuclide (isotope) within the MARIS database.

### Lookup Table (LUT) in use:
Yes, [dbo_nuclide.xlsx](https://github.com/franckalbinet/marisco/blob/main/nbs/files/lut/dbo_nuclide.xlsx)

### Open Refine Variable Name:
`nuclide_id`

### Open Refine Data Type:
An integer value (the 'id' defined in the LUT).

### NetCDF Variable Name:
`nuclide`

### NetCDF Data Type:
string

---

## Detection Limit

### Description:
The detection limit variable describes the Activity variable as follows:

'<': The reported value for the Activity variable is the Minimum Detectable Activity (MDA) or ISO11029 detection limit.
'=': The Activity variable represents the measured value, and an associated uncertainty should be provided.
'ND': Indicates that neither an activity value nor an MDA (or detection limit) is reported.
'DE': When the reported Activity variable is an aggregation of multiple samples, the detection limit variable is defined as Derived (DE), see Variable Type for more information related to aggregation of activity reported. 

### Lookup Table (LUT) in use:
Yes, [dbo_detectlimit.xlsx](https://github.com/franckalbinet/marisco/blob/main/nbs/files/lut/dbo_detectlimit.xlsx).

### Open Refine Variable Name:
`detection`

### Open Refine Data Type:
An integer value (the 'id' defined in the LUT).

### NetCDF Variable Name:
`detection_limit`

### NetCDF Data Type:
An integer value (the 'id' defined in the LUT).

---

## Activity

### Description:
The measured activity value or MDA for the nuclide reported. Several variables are used to describe the Activity variable, including:

**Nuclide ID**: Describes the nuclide for which the activity is reported.
**Detection Limit**: Indicates whether the reported Activity value is a measured activity value or below the detection limit.
**Unit ID**: Describes the unit associated with the reported Activity variable.
**Uncertainty**: The associated uncertainty of the Activity variable.
**Variable Type**: Describes whether the reported Activity variable is an aggregate, sum, mean, median, etc.

### Lookup Table (LUT) in use:
No.

### Open Refine Variable Name:
`activity`

### Open Refine Data Type:
float

### NetCDF Variable Name:
`value`

### NetCDF Data Type:
float

---

## Uncertainty

### Description:
The uncertainty associated with the measurement of the activity must be reported as a 1 sigma (k=1) measurement uncertainty. This uncertainty should be expressed in the same units as the activity variable.

### Lookup Table (LUT) in use:
No

### Open Refine Variable Name:
`uncertaint`

### Open Refine Data Type:
float

### NetCDF Variable Name:
`uncertainty`

### NetCDF Data Type:
float

---

## Unit ID

### Description:
Represents the ID value from the Lookup Table (LUT) corresponding to the unit of measurement for both the activity variable and the uncertainty variable (if applicable). For seawater measurements, ensure that the unit is converted from 'Bq L⁻¹' to 'Bq m⁻³', and use the corresponding LUT value for 'Bq m⁻³'.

### Lookup Table (LUT) in use:
Yes, [dbo_unit.xlsx](https://github.com/franckalbinet/marisco/blob/main/nbs/files/lut/dbo_unit.xlsx).

### Open Refine Variable Name:
`unit_id`

### Open Refine Data Type:
An integer value (the 'id' defined in the LUT).

### NetCDF Variable Name:
`unit`

### NetCDF Data Type:
An integer value (the 'id' defined in the LUT).

---

## Variable Type

### Description:
Describes the type of aggregation applied to the measurements if they are not reported as individual values. Possible values include:

AM: Arithmetic Mean
GM: Geometric Mean
MED: Median
MAX: Maximum
MIN: Minimum

### Lookup Table (LUT) in use:
No

### Open Refine Variable Name:
`vartype`

### Open Refine Data Type:
string

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---

## Frequency

### Description:
Indicates how often the sample is taken or the measurement is recorded. This variable helps to understand the regularity of data collection and can include details such as daily, weekly, monthly, or any other specified time interval.

### Lookup Table (LUT) in use:
No

### Open Refine Variable Name:
`freq`

### Open Refine Data Type:
string

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---

## Range Low Detection

### Description:
If aggregation occurred when evaluating the Activity variable, the 'Range Low Detection' value describes the 'Range Low' variable as follows:

- '<': The reported value for the Activity variable is the Minimum Detectable Activity (MDA) or ISO11029 detection limit.
- '=': The Activity variable represents the measured value, with an associated uncertainty provided.
- 'ND': Indicates that neither an activity value nor an MDA (or detection limit) is reported.
- 'DE': When the reported Activity variable is an aggregation of multiple samples, the detection limit variable is defined as Derived (DE). See the Variable Type section for more details on aggregation of reported activity.

### Lookup Table (LUT) in use:
Yes, [dbo_detectlimit.xlsx](https://github.com/franckalbinet/marisco/blob/main/nbs/files/lut/dbo_detectlimit.xlsx).

### Open Refine Variable Name:
`rl_detection`

### Open Refine Data Type:
An integer value (the 'id' defined in the LUT).

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---

## Range Low

### Description:
If aggregation is applied to the measurements, the 'Range Low ' variable represents the smallest activity measured within the aggregated dataset. This value should be reported in a format consistent with the unit specified by the Unit ID variable.

### Lookup Table (LUT) in use:
No

### Open Refine Variable Name:
`rangelow`

### Open Refine Data Type:
float

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---

## Range Upper

### Description:
If aggregation is applied to the measurements, the 'Range Upper ' variable represents the largest activity measured within the aggregated dataset. This value should be reported in a format consistent with the unit specified by the Unit ID variable.

### Lookup Table (LUT) in use:
No

### Open Refine Variable Name:
`rangeupp`

### Open Refine Data Type:
float

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---

## Species ID

### Description:
Represents the identifier for the species included in the sample. If a specific species is not provided but a biological group (e.g., 'Fish') is specified, use this group information to define the species.

### Lookup Table (LUT) in use:
Yes, [dbo_species.xlsx](https://github.com/franckalbinet/marisco/blob/main/nbs/files/lut/dbo_species.xlsx).

### Open Refine Variable Name:
`species_id`

### Open Refine Data Type:
An integer value (the 'species_id' defined in the LUT).

### NetCDF Variable Name:
`species`

### NetCDF Data Type:
An integer value (the 'species_id' defined in the LUT).

---

## Biological Group

### Description:
The biological group of the sample, if applicable. Grouping of related species (e.g. crustaceans, molluscs, fish etc.).

### Lookup Table (LUT) in use:
Yes, [dbo_species.xlsx](https://github.com/franckalbinet/marisco/blob/main/nbs/files/lut/dbo_species.xlsx) includes a "biogroup_id" for all species which links to the [dbo_biogroup.xlsx](https://github.com/franckalbinet/marisco/blob/main/nbs/files/lut/dbo_biogroup.xlsx) look-up.

### Open Refine Variable Name:
None

### Open Refine Data Type:
None

### NetCDF Variable Name:
`bio_group`

### NetCDF Data Type:
An integer value (the 'biogroup_id' defined in the LUT).

---

## Taxon Name

### Description:
Scientific name of the taxon.

### Lookup Table (LUT) in use:
No, 'Taxon Name' is defined for each species in the [dbo_species.xlsx](https://github.com/franckalbinet/marisco/blob/main/nbs/files/lut/dbo_specie s.xlsx) look-up.

### Open Refine Variable Name:
`Taxonname`

### Open Refine Data Type:
string

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---

## Taxon Reported Name

### Description:
Taxon name reported by the data provider.

### Lookup Table (LUT) in use:
No

### Open Refine Variable Name:
`TaxonRepName`

### Open Refine Data Type:
string

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---

## Common Name

### Description:
Common name of the species or organism.

### Lookup Table (LUT) in use:
No

### Open Refine Variable Name:
`Commonname`

### Open Refine Data Type:
string

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---

## Taxon Rank

### Description:
Rank of the taxon in the biological classification system.

### Lookup Table (LUT) in use:
No, 'Taxon Rank' is defined for each species in the [dbo_species.xlsx](https://github.com/franckalbinet/marisco/blob/main/nbs/files/lut/dbo_specie s.xlsx) look-up.

### Open Refine Variable Name:
`Taxonrank`

### Open Refine Data Type:
string

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---

## Taxon Database

### Description:
Database or repository where taxon information is stored.

### Lookup Table (LUT) in use:
No, 'Taxon Database' is defined for each species in the [dbo_species.xlsx](https://github.com/franckalbinet/marisco/blob/main/nbs/files/lut/dbo_specie s.xlsx) look-up.

### Open Refine Variable Name:
`TaxonDB`

### Open Refine Data Type:
string

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---

## Taxon Database ID

### Description:
Identifier for the taxon in the taxon database.

### Lookup Table (LUT) in use:
No, 'Taxon Database ID' is defined for each species in the [dbo_species.xlsx](https://github.com/franckalbinet/marisco/blob/main/nbs/files/lut/dbo_specie s.xlsx) look-up.

### Open Refine Variable Name:
`TaxonDBID`

### Open Refine Data Type:
string

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---

## Taxon Database URL

### Description:
URL the taxon database.

### Lookup Table (LUT) in use:
No, 'Taxon Database URL' is defined for each species in the [dbo_species.xlsx](https://github.com/franckalbinet/marisco/blob/main/nbs/files/lut/dbo_specie s.xlsx) look-up.

### Open Refine Variable Name:
`TaxonDBURL`

### Open Refine Data Type:
string

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---

## Body Part ID

### Description:
Represents the identifier for the specific body part of the sample.

### Lookup Table (LUT) in use:
Yes, [dbo_bodypar.xlsx](https://github.com/franckalbinet/marisco/blob/main/nbs/files/lut/dbo_bodypar.xlsx).

### Open Refine Variable Name:
`bodypar_id`

### Open Refine Data Type:
An integer value (the 'bodypar_id' defined in the LUT).

### NetCDF Variable Name:
`body_part`

### NetCDF Data Type:
An integer value (the 'bodypar_id' defined in the LUT).

---

## Slice Up

### Description:
Top of sediment core interval relative to the water-sediment interface (cm).

### Lookup Table (LUT) in use:
No

### Open Refine Variable Name:
`sliceup`

### Open Refine Data Type:
float

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---

## Slice Down

### Description:
Bottom of sediment core interval relative to the water-sediment interface (cm).

### Lookup Table (LUT) in use:
No

### Open Refine Variable Name:
`slicedown`

### Open Refine Data Type:
float

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---

## Sediment Type ID

### Description:
Represents the classification of sediment according to the Udden-Wentworth scale.

### Lookup Table (LUT) in use:
Yes, [dbo_sedtype.xlsx](https://github.com/franckalbinet/marisco/blob/main/nbs/files/lut/dbo_sedtype.xlsx).

### Open Refine Variable Name:
`sedtype_id`

### Open Refine Data Type:
An integer value (the 'sedtype_id' defined in the LUT).

### NetCDF Variable Name:
`sed_type`

### NetCDF Data Type:
An integer value (the 'sedtype_id' defined in the LUT).

---

## Sediment Reported Name

### Description:
Name of the sediment as reported by the data provider. The sediment name should be stored exactly as provided, without any modifications.

### Lookup Table (LUT) in use:
No.

### Open Refine Variable Name:
`SedRepName`

### Open Refine Data Type:
string

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---

## Volume

### Description:
Volume of the sample.

### Lookup Table (LUT) in use:
No.

### Open Refine Variable Name:
`volume`

### Open Refine Data Type:
float

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---

## Salinity

### Description:
Salinity of the sample, expressed in practical salinity units (PSU).If required, consult TEOS-10 guidelines (www.teos-10.org/) for converting from Absolute Salinity (g/kg) to Practical Salinity.

### Lookup Table (LUT) in use:
No

### Open Refine Variable Name:
`salinity`

### Open Refine Data Type:
float

### NetCDF Variable Name:
`salinity`

### NetCDF Data Type:
float

---

## Temperature

### Description:
Temperature of the sample (°C).

### Lookup Table (LUT) in use:
No

### Open Refine Variable Name:
`temperatur`

### Open Refine Data Type:
float

### NetCDF Variable Name:
`temperature`

### NetCDF Data Type:
float

---

## Filtered

### Description:
Indicates whether the sample was filtered:
- Y : Sample was filtered.
- N : Sample was not filtered.
- NA : Not applicable or information not available.

### Lookup Table (LUT) in use:
No

### Open Refine Variable Name:
`filtered`

### Open Refine Data Type:
string

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---

## Filter Pore Mesh size

### Description:
The pore size of the filter used, if applicable, expressed in micrometers (µm).

### Lookup Table (LUT) in use:
No

### Open Refine Variable Name:
`filtpore`

### Open Refine Data Type:
float

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---

## Acidified

### Description:
Indicates if the sample was acidified.
- A: Sample acidified
- NA: Sample not acidified

### Lookup Table (LUT) in use:
No

### Open Refine Variable Name:
`acid`

### Open Refine Data Type:
string

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---

## Oxygen

### Description:
Dissolved oxygen concentration.

### Lookup Table (LUT) in use:
No

### Open Refine Variable Name:
`oxygen`

### Open Refine Data Type:
float

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---

## Sample Area

### Description:
Sample surface area of sediment (cm2).

### Lookup Table (LUT) in use:
No

### Open Refine Variable Name:
`samparea`

### Open Refine Data Type:
float

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---

## Dry Weight

### Description:
Dry weight of the sample, expressed in grams (g).

### Lookup Table (LUT) in use:
No

### Open Refine Variable Name:
`drywt`

### Open Refine Data Type:
float

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---

## Wet Weight

### Description:
Wet weight of the sample, expressed in grams (g).

### Lookup Table (LUT) in use:
No

### Open Refine Variable Name:
`wetwt`

### Open Refine Data Type:
float

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---

## Percent Weight

### Description:
Expressed as a percentage. This is calculated by dividing the dry weight by the wet weight and then multiplying by 100. The reported value should be greater than 0 and less than 100. 

### Lookup Table (LUT) in use:
No

### Open Refine Variable Name:
`percentwt`

### Open Refine Data Type:
float

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---

## Sampling Method ID

### Description:
Identifier for the method used to collect the sample.

### Lookup Table (LUT) in use:
Yes, [dbo_sampmet.xlsx](https://github.com/franckalbinet/marisco/blob/main/nbs/files/lut/dbo_sampmet.xlsx).

### Open Refine Variable Name:
`sampmet_id`

### Open Refine Data Type:
An integer value (the 'sampmet_id' defined in the LUT).

### NetCDF Variable Name:
`sampling_method`

### NetCDF Data Type:
An integer value (the 'sampmet_id' defined in the LUT).

---

## Drying Method ID

### Description:
Identifier for the method used to dry the sample.

### Lookup Table (LUT) in use:
Yes, [dbo_sampmet.xlsx]

### Open Refine Variable Name:
`drymet_id`

### Open Refine Data Type:
An integer value (the 'id' defined in the LUT).

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---

## Preparation Method ID

### Description:
Identifier for the method used to prepare the sample.

### Lookup Table (LUT) in use:
Yes, [dbo_prepmet.xlsx](https://github.com/franckalbinet/marisco/blob/main/nbs/files/lut/dbo_prepmet.xlsx).
### Open Refine Variable Name:
`prepmet_id`

### Open Refine Data Type:
An integer value (the 'prepmet_id' defined in the LUT).

### NetCDF Variable Name:
`preparation_method`

### NetCDF Data Type:
An integer value (the 'prepmet_id' defined in the LUT).


---

## Counting Method ID

### Description:
Identifier for the method used to count the sample.

### Lookup Table (LUT) in use:
Yes, [dbo_counmet.xlsx](https://github.com/franckalbinet/marisco/blob/main/nbs/files/lut/dbo_counmet.xlsx).

### Open Refine Variable Name:
`counmet_id`

### Open Refine Data Type:
An integer value (the 'counmet_id' defined in the LUT).

### NetCDF Variable Name:
`counting_method`

### NetCDF Data Type:
An integer value (the 'counmet_id' defined in the LUT).

---

## Reference ID

### Description:
Identifier which identifies the source provider of the data.


### Lookup Table (LUT) in use:
Yes, [dbo_ref.xlsx]

### Open Refine Variable Name:
`ref_id`

### Open Refine Data Type:
An integer value (the 'id' defined in the LUT).

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---

## Reference Note

### Description:
Notes or comments related to the reference or source.

### Lookup Table (LUT) in use:
No

### Open Refine Variable Name:
`refnote`

### Open Refine Data Type:
string

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---

## Sample Note

### Description:
Notes or comments related to the sample.

### Lookup Table (LUT) in use:
No

### Open Refine Variable Name:
`sampnote`

### Open Refine Data Type:
string

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---

## Measurement Note

### Description:
Notes or comments related to the measurement process.

### Lookup Table (LUT) in use:
No

### Open Refine Variable Name:
`measurenote`

### Open Refine Data Type:
string

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---

## Good for Export

### Description:
Indicates if the sample data is deemed good for export.

### Lookup Table (LUT) in use:
No

### Open Refine Variable Name:
`gfe`

### Open Refine Data Type:
string

### NetCDF Variable Name:
Not included in NetCDF.

### NetCDF Data Type:
Not included in NetCDF.

---
