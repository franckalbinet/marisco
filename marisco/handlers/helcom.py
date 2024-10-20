# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/handlers/helcom.ipynb.

# %% auto 0
__all__ = ['fname_in', 'fname_out_nc', 'fname_out_csv', 'zotero_key', 'ref_id', 'default_smp_types', 'fixes_nuclide_names',
           'lut_nuclides', 'coi_val', 'coi_units_unc', 'fixes_biota_species', 'lut_biota', 'fixes_biota_tissues',
           'lut_tissues', 'lut_biogroup', 'lut_taxon', 'fixes_sediments', 'lut_sediments', 'lut_units', 'lut_dl',
           'coi_dl', 'lut_filtered', 'lut_method', 'kw', 'load_data', 'RemapNuclideNameCB', 'ParseTimeCB',
           'SanitizeValue', 'unc_rel2stan', 'NormalizeUncCB', 'get_taxon_info_lut', 'RemapTaxonInformationCB',
           'RemapSedimentCB', 'RemapUnitCB', 'RemapDetectionLimitCB', 'RemapFiltCB', 'AddSampleLabCodeCB',
           'AddMeasurementNoteCB', 'RemapStationIdCB', 'RemapSedSliceTopBottomCB', 'LookupDryWetRatio',
           'ParseCoordinates', 'get_common_rules', 'get_specific_rules', 'get_renaming_rules',
           'SelectAndRenameColumnCB', 'get_attrs', 'enums_xtra', 'encode']

# %% ../../nbs/handlers/helcom.ipynb 6
import pandas as pd 
import numpy as np
from functools import partial 
import fastcore.all as fc 
from pathlib import Path 
from dataclasses import asdict
from typing import List, Dict, Callable, Tuple, Any 
from collections import OrderedDict, defaultdict
import re

from marisco.utils import (
    has_valid_varname, 
    match_worms, 
    Remapper, 
    ddmm_to_dd,
    match_maris_lut, 
    Match, 
    get_unique_across_dfs
)

from marisco.callbacks import (
    Callback, 
    Transformer, 
    EncodeTimeCB, 
    AddSampleTypeIdColumnCB,
    AddNuclideIdColumnCB, 
    LowerStripNameCB, 
    SanitizeLonLatCB, 
    ReshapeLongToWide, 
    CompareDfsAndTfmCB, 
    RemapCB
)

from marisco.metadata import (
    GlobAttrsFeeder, 
    BboxCB, 
    DepthRangeCB, 
    TimeRangeCB, 
    ZoteroCB, 
    KeyValuePairCB
)

from marisco.configs import (
    nuc_lut_path, 
    nc_tpl_path, 
    cfg, 
    cache_path, 
    cdl_cfg, 
    Enums, 
    lut_path, 
    species_lut_path, 
    sediments_lut_path, 
    bodyparts_lut_path, 
    detection_limit_lut_path, 
    filtered_lut_path, 
    area_lut_path, 
    get_lut, 
    unit_lut_path
)

from marisco.serializers import (
    NetCDFEncoder, 
    OpenRefineCsvEncoder
)

import warnings
warnings.filterwarnings('ignore')

# %% ../../nbs/handlers/helcom.ipynb 10
fname_in = '../../_data/accdb/mors/csv'
fname_out_nc = '../../_data/output/100-HELCOM-MORS-2024.nc'
fname_out_csv = '../../_data/output/100-HELCOM-MORS-2024.csv'
zotero_key ='26VMZZ2Q' # HELCOM MORS zotero key
ref_id = 100 # HELCOM MORS reference id as defined by MARIS

# %% ../../nbs/handlers/helcom.ipynb 13
default_smp_types = [('SEA', 'seawater'), ('SED', 'sediment'), ('BIO', 'biota')]

# %% ../../nbs/handlers/helcom.ipynb 14
def load_data(src_dir: str|Path, # The directory where the source CSV files are located
              smp_types: list=default_smp_types # A list of tuples, each containing the file prefix and the corresponding sample type name
             ) -> Dict[str, pd.DataFrame]: # A dictionary with sample types as keys and their corresponding dataframes as values
    "Load HELCOM data and return the data in a dictionary of dataframes with the dictionary key as the sample type."
    src_path = Path(src_dir)
    
    def load_and_merge(file_prefix: str) -> pd.DataFrame:
        try:
            df_meas = pd.read_csv(src_path / f'{file_prefix}02.csv')
            df_smp = pd.read_csv(src_path / f'{file_prefix}01.csv')
            return pd.merge(df_meas, df_smp, on='KEY', how='left')
        except FileNotFoundError as e:
            print(f"Error loading files for {file_prefix}: {e}")
            return pd.DataFrame()  # Return an empty DataFrame if files are not found
    
    return {smp_type: load_and_merge(file_prefix) for file_prefix, smp_type in smp_types}

# %% ../../nbs/handlers/helcom.ipynb 36
fixes_nuclide_names = {
    'cs134137': 'cs134_137_tot',
    'cm243244': 'cm243_244_tot',
    'pu239240': 'pu239_240_tot',
    'pu238240': 'pu238_240_tot',
    'cs143': 'cs137',
    'cs145': 'cs137',
    'cs142': 'cs137',
    'cs141': 'cs137',
    'cs144': 'cs137',
    'k-40': 'k40',
    'cs140': 'cs137',
    'cs146': 'cs137',
    'cs139': 'cs137',
    'cs138': 'cs137'
    }

# %% ../../nbs/handlers/helcom.ipynb 40
# Create a lookup table for nuclide names
lut_nuclides = lambda df: Remapper(provider_lut_df=df,
                                   maris_lut_fn=nuc_lut_path,
                                   maris_col_id='nuclide_id',
                                   maris_col_name='nc_name',
                                   provider_col_to_match='value',
                                   provider_col_key='value',
                                   fname_cache='nuclides_helcom.pkl').generate_lookup_table(fixes=fixes_nuclide_names, 
                                                                                            as_df=False, overwrite=False)

# %% ../../nbs/handlers/helcom.ipynb 41
class RemapNuclideNameCB(Callback):
    "Remap data provider nuclide names to MARIS nuclide names."
    def __init__(self, 
                 fn_lut: Callable # Function that returns the lookup table dictionary
                ):
        fc.store_attr()

    def __call__(self, tfm: Transformer):
        df_uniques = get_unique_across_dfs(tfm.dfs, col_name='NUCLIDE', as_df=True)
        lut = {k: v.matched_maris_name for k, v in self.fn_lut(df_uniques).items()}    
        for k in tfm.dfs.keys():
            tfm.dfs[k]['NUCLIDE'] = tfm.dfs[k]['NUCLIDE'].replace(lut)

# %% ../../nbs/handlers/helcom.ipynb 50
class ParseTimeCB(Callback):
    "Parse and standardize time information in the dataframe."
    def __call__(self, tfm: Transformer):
        for df in tfm.dfs.values():
            self._process_dates(df)
            self._define_beg_period(df)

    def _process_dates(self, df: pd.DataFrame) -> None:
        "Process and correct date and time information in the DataFrame."
        df['time'] = self._parse_date(df)
        self._handle_missing_dates(df)
        self._fill_missing_time(df)

    def _parse_date(self, df: pd.DataFrame) -> pd.Series:
        "Parse the DATE column if present."
        return pd.to_datetime(df['DATE'], format='%m/%d/%y %H:%M:%S', errors='coerce')

    def _handle_missing_dates(self, df: pd.DataFrame):
        "Handle cases where DAY or MONTH is 0 or missing."
        df.loc[df["DAY"] == 0, "DAY"] = 1
        df.loc[df["MONTH"] == 0, "MONTH"] = 1
        
        missing_day_month = (df["DAY"].isna()) & (df["MONTH"].isna()) & (df["YEAR"].notna())
        df.loc[missing_day_month, ["DAY", "MONTH"]] = 1

    def _fill_missing_time(self, df: pd.DataFrame) -> None:
        "Fill missing time values using YEAR, MONTH, and DAY columns."
        missing_time = df['time'].isna()
        df.loc[missing_time, 'time'] = pd.to_datetime(
            df.loc[missing_time, ['YEAR', 'MONTH', 'DAY']], 
            format='%Y%m%d', 
            errors='coerce'
        )

    def _define_beg_period(self, df: pd.DataFrame) -> None:
        "Create a standardized date representation for Open Refine."
        df['begperiod'] = df['time']

# %% ../../nbs/handlers/helcom.ipynb 59
coi_val = {'seawater' : {'val': 'VALUE_Bq/m³'},
           'biota':  {'val': 'VALUE_Bq/kg'},
           'sediment': {'val': 'VALUE_Bq/kg'}}

# %% ../../nbs/handlers/helcom.ipynb 60
class SanitizeValue(Callback):
    "Sanitize value/measurement by removing blank entries and populating `value` column."
    def __init__(self, 
                 coi: Dict[str, Dict[str, str]] # Columns of interest. Format: {group_name: {'val': 'column_name'}}
                 ): 
        fc.store_attr()

    def __call__(self, tfm: Transformer):
        for grp, df in tfm.dfs.items():
            value_col = self.coi[grp]['val']
            df.dropna(subset=[value_col], inplace=True)
            df['value'] = df[value_col]

# %% ../../nbs/handlers/helcom.ipynb 64
def unc_rel2stan(
    df: pd.DataFrame, # DataFrame containing measurement and uncertainty columns
    meas_col: str, # Name of the column with measurement values
    unc_col: str # Name of the column with relative uncertainty values (percentages)
) -> pd.Series: # Series with calculated absolute uncertainties
    "Convert relative uncertainty to absolute uncertainty."
    return df.apply(lambda row: row[unc_col] * row[meas_col] / 100, axis=1)

# %% ../../nbs/handlers/helcom.ipynb 66
# Columns of interest
coi_units_unc = [('seawater', 'VALUE_Bq/m³', 'ERROR%_m³'),
                 ('biota', 'VALUE_Bq/kg', 'ERROR%'),
                 ('sediment', 'VALUE_Bq/kg', 'ERROR%_kg')]

# %% ../../nbs/handlers/helcom.ipynb 68
class NormalizeUncCB(Callback):
    "Convert from relative error % to uncertainty of activity unit."
    def __init__(self, 
                 fn_convert_unc: Callable=unc_rel2stan, # Function converting relative uncertainty to absolute uncertainty
                 coi: List[Tuple[str, str, str]]=coi_units_unc # List of columns of interest
                ):
        fc.store_attr()
    
    def __call__(self, tfm: Transformer):
        for grp, val, unc in self.coi:
            if grp in tfm.dfs:
                df = tfm.dfs[grp]
                df['uncertainty'] = self.fn_convert_unc(df, val, unc)

# %% ../../nbs/handlers/helcom.ipynb 78
fixes_biota_species = {
    'CARDIUM EDULE': 'Cerastoderma edule',
    'LAMINARIA SACCHARINA': 'Saccharina latissima',
    'PSETTA MAXIMA': 'Scophthalmus maximus',
    'STIZOSTEDION LUCIOPERCA': 'Sander luciopercas'}

# %% ../../nbs/handlers/helcom.ipynb 82
lut_biota = lambda: Remapper(provider_lut_df=pd.read_csv(Path(fname_in) / 'RUBIN_NAME.csv'),
                             maris_lut_fn=species_lut_path,
                             maris_col_id='species_id',
                             maris_col_name='species',
                             provider_col_to_match='SCIENTIFIC NAME',
                             provider_col_key='RUBIN',
                             fname_cache='species_helcom.pkl'
                             ).generate_lookup_table(fixes=fixes_biota_species, as_df=False, overwrite=False)

# %% ../../nbs/handlers/helcom.ipynb 88
fixes_biota_tissues = {
    'WHOLE FISH WITHOUT HEAD AND ENTRAILS': 'Whole animal eviscerated without head',
    'ENTRAILS': 'Viscera',
    'SKIN/EPIDERMIS': 'Skin'}

# %% ../../nbs/handlers/helcom.ipynb 91
lut_tissues = lambda: Remapper(provider_lut_df=pd.read_csv('../../_data/accdb/mors/csv/TISSUE.csv'),
                               maris_lut_fn=bodyparts_lut_path,
                               maris_col_id='bodypar_id',
                               maris_col_name='bodypar',
                               provider_col_to_match='TISSUE_DESCRIPTION',
                               provider_col_key='TISSUE',
                               fname_cache='tissues_helcom.pkl'
                               ).generate_lookup_table(fixes=fixes_biota_tissues, as_df=False, overwrite=False)

# %% ../../nbs/handlers/helcom.ipynb 95
lut_biogroup = lambda: get_lut(species_lut_path().parent, species_lut_path().name, 
                               key='species_id', value='biogroup_id')

# %% ../../nbs/handlers/helcom.ipynb 98
# TODO: Include Commonname field after next MARIS data reconciling process.
def get_taxon_info_lut(
    maris_lut:str # Path to the MARIS lookup table (Excel file)
) -> dict: # A dictionary mapping species_id to biogroup_id
    "Retrieve a lookup table for Taxonname from a MARIS lookup table."
    species = pd.read_excel(maris_lut)
    return species[['species_id', 'Taxonname', 'Taxonrank','TaxonDB','TaxonDBID','TaxonDBURL']].set_index('species_id').to_dict()

lut_taxon = lambda: get_taxon_info_lut(species_lut_path())

# %% ../../nbs/handlers/helcom.ipynb 99
class RemapTaxonInformationCB(Callback):
    "Update taxon information based on MARIS species LUT."
    def __init__(self, fn_lut: Callable):
        self.fn_lut = fn_lut

    def __call__(self, tfm: Transformer):
        lut = self.fn_lut()
        df = tfm.dfs['biota']
        
        df['TaxonRepName'] = df.get('RUBIN', 'Unknown')
        
        taxon_columns = ['Taxonname', 'Taxonrank', 'TaxonDB', 'TaxonDBID', 'TaxonDBURL']
        for col in taxon_columns:
            df[col] = df['species'].map(lut[col]).fillna('Unknown')
        
        unmatched = df[df['Taxonname'] == 'Unknown']['species'].unique()
        if len(unmatched) > 0:
            print(f"Unmatched species IDs: {', '.join(unmatched)}")

# %% ../../nbs/handlers/helcom.ipynb 108
fixes_sediments = {
    'NO DATA': '(Not available)'
}

# %% ../../nbs/handlers/helcom.ipynb 110
class RemapSedimentCB(Callback):
    "Update sediment id based on MARIS species LUT (dbo_sedtype.xlsx)."
    def __init__(self, 
                 fn_lut: Callable, # Function that returns the lookup table dictionary
                ):
        fc.store_attr()

    def _fix_inconsistent_sedi(self, df:pd.DataFrame) -> pd.DataFrame:
        "Temporary fix for inconsistent SEDI values. Data provider to confirm and clarify."
        df['SEDI'] = df['SEDI'].replace({56: -99, 73: -99, np.nan: -99})
        return df
    
    def __call__(self, tfm: Transformer):
        "Remap sediment types in the DataFrame using the lookup table and handle specific replacements."
        lut = self.fn_lut()
        
        # Set SedRepName (TBC: what's used for?)
        tfm.dfs['sediment']['SedRepName']  = tfm.dfs['sediment']['SEDI'] 
        
        tfm.dfs['sediment'] = self._fix_inconsistent_sedi(tfm.dfs['sediment'])
        tfm.dfs['sediment']['sed_type'] = tfm.dfs['sediment']['SEDI'].apply(lambda x: self._get_sediment_type(x, lut))

    def _get_sediment_type(self, 
                           sedi_value: int, # The `SEDI` value from the DataFrame
                           lut: dict # The lookup table dictionary
                          ) -> Match: # The Match object
        "Get the matched_id from the lookup table and print SEDI if the matched_id is -1."
        match = lut.get(sedi_value, Match(-1, None, None, None))
        
        if match.matched_id == -1:
            self._print_unmatched_sedi(sedi_value)
        return match.matched_id

    def _print_unmatched_sedi(self, 
                              sedi_value: int # The `SEDI` value from the DataFram
                             ) -> None:
        "Print the SEDI value if the matched_id is -1."
        print(f"Unmatched SEDI: {sedi_value}")

# %% ../../nbs/handlers/helcom.ipynb 111
lut_sediments = lambda: Remapper(provider_lut_df=pd.read_csv(Path(fname_in) / 'SEDIMENT_TYPE.csv'),
                                 maris_lut_fn=sediments_lut_path,
                                 maris_col_id='sedtype_id',
                                 maris_col_name='sedtype',
                                 provider_col_to_match='SEDIMENT TYPE',
                                 provider_col_key='SEDI',
                                 fname_cache='sediments_helcom.pkl'
                                 ).generate_lookup_table(fixes=fixes_sediments, as_df=False, overwrite=False)

# %% ../../nbs/handlers/helcom.ipynb 121
lut_units = {
    'seawater': 1,  # 'Bq/m3'
    'sediment': 4,  # 'Bq/kgd' for sediment
    'biota': {
        'D': 4,  # 'Bq/kgd'
        'W': 5,  # 'Bq/kgw'
        'F': 5   # 'Bq/kgw' (assumed to be 'Fresh', so set to wet)
    }
}

# %% ../../nbs/handlers/helcom.ipynb 122
class RemapUnitCB(Callback):
    "Set the `unit` id column in the DataFrames based on a lookup table."
    def __init__(self, 
                 lut_units: dict=lut_units # Dictionary containing renaming rules for different unit categories
                ):
        fc.store_attr()

    def __call__(self, tfm: Transformer):
        for grp in tfm.dfs.keys():
            if grp in ['seawater', 'sediment']:
                tfm.dfs[grp]['unit'] = self.lut_units[grp]
            else:
                tfm.dfs[grp]['unit'] = tfm.dfs[grp]['BASIS'].apply(lambda x: lut_units[grp].get(x, 0))

# %% ../../nbs/handlers/helcom.ipynb 127
lut_dl = lambda: pd.read_excel(detection_limit_lut_path(), usecols=['name','id']).set_index('name').to_dict()['id']

# %% ../../nbs/handlers/helcom.ipynb 129
coi_dl = {'seawater' : {'val' : 'VALUE_Bq/m³',
                       'unc' : 'ERROR%_m³',
                       'dl' : '< VALUE_Bq/m³'},
          'biota':  {'val' : 'VALUE_Bq/kg',
                     'unc' : 'ERROR%',
                     'dl' : '< VALUE_Bq/kg'},
          'sediment': {
              'val' : 'VALUE_Bq/kg',
              'unc' : 'ERROR%_kg',
              'dl' : '< VALUE_Bq/kg'}}

# %% ../../nbs/handlers/helcom.ipynb 132
# TO BE REFACTORED
class RemapDetectionLimitCB(Callback):
    "Remap value type to MARIS format."
    def __init__(self, 
                 coi: dict, # Configuration options for column names
                 fn_lut: Callable # Function that returns a lookup table
                ):
        fc.store_attr()

    def __call__(self, tfm: Transformer):
        "Remap detection limits in the DataFrames using the lookup table."
        lut = self.fn_lut()
        
        for grp in tfm.dfs:
            df = tfm.dfs[grp]
            self._update_detection_limit(df, grp, lut)
    
    def _update_detection_limit(self, 
                                df: pd.DataFrame, # The DataFrame to modify
                                grp: str, # The group name to get the column configuration
                                lut: dict # The lookup table dictionary
                               ) -> None:
        "Update detection limit column in the DataFrame based on lookup table and rules."
        detection_col = self.coi[grp]['dl']
        value_col = self.coi[grp]['val']
        uncertainty_col = self.coi[grp]['unc']
        
        # Copy detection limit column
        df['detection_limit'] = df[detection_col]
        
        # Fill values with '=' or 'Not Available'
        condition = ((df[value_col].notna()) & (df[uncertainty_col].notna()) &
                     (~df['detection_limit'].isin(lut.keys())))
        df.loc[condition, 'detection_limit'] = '='
        df.loc[~df['detection_limit'].isin(lut.keys()), 'detection_limit'] = 'Not Available'
        
        # Perform lookup
        df['detection_limit'] = df['detection_limit'].map(lut)

# %% ../../nbs/handlers/helcom.ipynb 140
lut_filtered = {
    'N': 2,
    'n': 2,
    'F': 1
}

# %% ../../nbs/handlers/helcom.ipynb 142
class RemapFiltCB(Callback):
    "Lookup FILT value in dataframe using the lookup table."
    def __init__(self,
                 lut_filtered: dict=lut_filtered, # Dictionary mapping FILT codes to their corresponding names
                ):
        fc.store_attr()

    def __call__(self, tfm):
        for df in tfm.dfs.values():
            if 'FILT' in df.columns:
                df['FILT'] = df['FILT'].map(lambda x: self.lut_filtered.get(x, 0))

# %% ../../nbs/handlers/helcom.ipynb 147
class AddSampleLabCodeCB(Callback):
    "Remap `KEY` column to `samplabcode` in each DataFrame."
    def __call__(self, tfm: Transformer):
        for grp in tfm.dfs:
            self._remap_sample_id(tfm.dfs[grp])
    
    def _remap_sample_id(self, df: pd.DataFrame):
        df['samplabcode'] = df['KEY']

# %% ../../nbs/handlers/helcom.ipynb 152
lut_method = lambda: pd.read_csv(Path(fname_in) / 'ANALYSIS_METHOD.csv').set_index('METHOD').to_dict()['DESCRIPTION']

# %% ../../nbs/handlers/helcom.ipynb 153
class AddMeasurementNoteCB(Callback):
    "Record measurement notes by adding a 'measurenote' column to DataFrames."
    def __init__(self, 
                 fn_lut: Callable # Function that returns the lookup dictionary with `METHOD` as key and `DESCRIPTION` as value
                ):
        fc.store_attr()
        
    def __call__(self, tfm: Transformer):
        lut = self.fn_lut()
        for df in tfm.dfs.values():
            if 'METHOD' in df.columns:
                df['measurementnote'] = df['METHOD'].map(lambda x: lut.get(x, 0))

# %% ../../nbs/handlers/helcom.ipynb 157
class RemapStationIdCB(Callback):
    "Remap Station ID to MARIS format."
    def __init__(self):
        fc.store_attr()

    def __call__(self, tfm: Transformer):
        "Iterate through all DataFrames in the transformer object and remap `STATION` to `station_id`."
        for grp in tfm.dfs.keys(): 
            tfm.dfs[grp]['station'] = tfm.dfs[grp]['STATION']

# %% ../../nbs/handlers/helcom.ipynb 161
class RemapSedSliceTopBottomCB(Callback):
    "Remap Sediment slice top and bottom to MARIS format."
    def __call__(self, tfm: Transformer):
        "Iterate through all DataFrames in the transformer object and remap sediment slice top and bottom."
        tfm.dfs['sediment']['top'] = tfm.dfs['sediment']['UPPSLI']
        tfm.dfs['sediment']['bottom'] = tfm.dfs['sediment']['LOWSLI']

# %% ../../nbs/handlers/helcom.ipynb 166
class LookupDryWetRatio(Callback):
    "Lookup dry-wet ratio and format for MARIS."
    def __call__(self, tfm: Transformer):
        "Iterate through all DataFrames in the transformer object and apply the dry-wet ratio lookup."
        for grp in tfm.dfs.keys():
            if 'DW%' in tfm.dfs[grp].columns:
                self._apply_dry_wet_ratio(tfm.dfs[grp])

    def _apply_dry_wet_ratio(self, df: pd.DataFrame) -> None:
        "Apply dry-wet ratio conversion and formatting to the given DataFrame."
        df['dry_wet_ratio'] = df['DW%']
        # Convert 'DW%' = 0% to NaN.
        df.loc[df['dry_wet_ratio'] == 0, 'dry_wet_ratio'] = np.NaN


# %% ../../nbs/handlers/helcom.ipynb 173
class ParseCoordinates(Callback):
    """
    Get geographical coordinates from columns expressed in degrees decimal format 
    or from columns in degrees/minutes decimal format where degrees decimal format is missing.
    """
    def __init__(self, 
                 fn_convert_cor: Callable # Function that converts coordinates from degree-minute to decimal degree format
                 ):
        self.fn_convert_cor = fn_convert_cor

    def __call__(self, tfm:Transformer):
        for df in tfm.dfs.values():
            self._format_coordinates(df)

    def _format_coordinates(self, df:pd.DataFrame) -> None:
        coord_cols = self._get_coord_columns(df.columns)
        
        for coord in ['lat', 'lon']:
            decimal_col, minute_col = coord_cols[f'{coord}_d'], coord_cols[f'{coord}_m']
            
            condition = df[decimal_col].isna() | (df[decimal_col] == 0)
            df[coord] = np.where(condition,
                                 df[minute_col].apply(self._safe_convert),
                                 df[decimal_col])
        
        df.dropna(subset=['lat', 'lon'], inplace=True)

    def _get_coord_columns(self, columns) -> dict:
        return {
            'lon_d': self._find_coord_column(columns, 'LON', 'dddddd'),
            'lat_d': self._find_coord_column(columns, 'LAT', 'dddddd'),
            'lon_m': self._find_coord_column(columns, 'LON', 'ddmmmm'),
            'lat_m': self._find_coord_column(columns, 'LAT', 'ddmmmm')
        }

    def _find_coord_column(self, columns, coord_type, coord_format) -> str:
        pattern = re.compile(f'{coord_type}.*{coord_format}', re.IGNORECASE)
        matching_columns = [col for col in columns if pattern.search(col)]
        return matching_columns[0] if matching_columns else None

    def _safe_convert(self, value) -> str:
        if pd.isna(value):
            return value
        try:
            return self.fn_convert_cor(value)
        except Exception as e:
            print(f"Error converting value {value}: {e}")
            return value

# %% ../../nbs/handlers/helcom.ipynb 184
def get_common_rules(
    vars: dict, # Configuration dictionary
    encoding_type: str # Encoding type (`netcdf` or `openrefine`)
    ) -> dict: # Common renaming rules for NetCDF and OpenRefine.
    "Get common renaming rules for NetCDF and OpenRefine."
    common = {
        'KEY': 'key',
        'lat': 'latitude' if encoding_type == 'openrefine' else vars['defaults']['lat']['name'],
        'lon': 'longitude' if encoding_type == 'openrefine' else vars['defaults']['lon']['name'],
        'time': 'begperiod' if encoding_type == 'openrefine' else vars['defaults']['time']['name'],
        'NUCLIDE': 'nuclide_id' if encoding_type == 'openrefine' else 'nuclide',
        'detection_limit': 'detection' if encoding_type == 'openrefine' else vars['suffixes']['detection_limit']['name'],
        'unit': 'unit_id' if encoding_type == 'openrefine' else vars['suffixes']['unit']['name'],
        'value': 'activity' if encoding_type == 'openrefine' else 'value',
        'uncertainty': 'uncertaint' if encoding_type == 'openrefine' else vars['suffixes']['uncertainty']['name'],
        'SDEPTH': 'sampdepth' if encoding_type == 'openrefine' else vars['defaults']['smp_depth']['name'],
        'TDEPTH': 'totdepth' if encoding_type == 'openrefine' else vars['defaults']['tot_depth']['name'],
    }
    
    if encoding_type == 'openrefine':
        common.update({
            'samptype_id': 'samptype_id',
            'station': 'station',
            'samplabcode': 'samplabcode',
            'SALIN': 'salinity',
            'TTEMP': 'temperatur',
            'FILT': 'filtered',
            'measurenote': 'measurenote'
        })
    else:
        common.update({
            'counting_method': vars['suffixes']['counting_method']['name'],
            'sampling_method': vars['suffixes']['sampling_method']['name'],
            'preparation_method': vars['suffixes']['preparation_method']['name'],
            'SALIN': vars['suffixes']['salinity']['name'],
            'TTEMP': vars['suffixes']['temperature']['name'],
        })
    
    return common

# %% ../../nbs/handlers/helcom.ipynb 185
def get_specific_rules(
    vars: dict, # Configuration dictionary
    encoding_type: str # Encoding type (`netcdf` or `openrefine`)
    ) -> dict: # Specific renaming rules for NetCDF and OpenRefine.
    "Get specific renaming rules for NetCDF and OpenRefine."
    if encoding_type == 'netcdf':
        return {
            'biota': {
                'species': vars['bio']['species']['name'],
                'body_part': vars['bio']['body_part']['name'],
                'bio_group': vars['bio']['bio_group']['name']
            },
            'sediment': {
                'sed_type': vars['sed']['sed_type']['name'],
                'top': vars['sed']['top']['name'],
                'bottom': vars['sed']['bottom']['name'],
            }
        }
    elif encoding_type == 'openrefine':
        return {
            'biota': {
                'species': 'species_id',
                'Taxonname': 'Taxonname',
                'TaxonRepName': 'TaxonRepName',
                'Taxonrank': 'Taxonrank',
                'TaxonDB': 'TaxonDB',
                'TaxonDBID': 'TaxonDBID',
                'TaxonDBURL': 'TaxonDBURL',
                'body_part': 'bodypar_id',
                'dry_wet_ratio': 'percentwt',
            },
            'sediment': {
                'sed_type': 'sedtype_id',
                'top': 'sliceup',
                'bottom': 'slicedown',
                'SedRepName': 'SedRepName',
                'dry_wet_ratio': 'percentwt',
            }
        }

# %% ../../nbs/handlers/helcom.ipynb 186
def get_renaming_rules(
    encoding_type: str = 'netcdf' # Encoding type (`netcdf` or `openrefine`)
    ) -> dict: # Renaming rules for NetCDF and OpenRefine.
    "Get renaming rules for NetCDF and OpenRefine."
    vars = cdl_cfg()['vars']
    
    if encoding_type not in ['netcdf', 'openrefine']:
        raise ValueError("Invalid encoding_type provided. Please use 'netcdf' or 'openrefine'.")
    
    common_rules = get_common_rules(vars, encoding_type)
    specific_rules = get_specific_rules(vars, encoding_type)
    
    rules = defaultdict(dict)
    for sample_type in ['seawater', 'biota', 'sediment']:
        rules[sample_type] = common_rules.copy()
        rules[sample_type].update(specific_rules.get(sample_type, {}))
    
    return dict(rules)

# %% ../../nbs/handlers/helcom.ipynb 187
class SelectAndRenameColumnCB(Callback):
    "Select and rename columns in a DataFrame based on renaming rules for a specified encoding type."
    def __init__(self, 
                 fn_renaming_rules: Callable, # A function that returns an OrderedDict of renaming rules 
                 encoding_type: str='netcdf', # The encoding type (`netcdf` or `openrefine`) to determine which renaming rules to use
                 verbose: bool=False # Whether to print out renaming rules that were not applied
                 ):
        fc.store_attr()

    def __call__(self, tfm: Transformer):
        "Apply column selection and renaming to DataFrames in the transformer, and identify unused rules."
        try:
            renaming_rules = self.fn_renaming_rules(self.encoding_type)
        except ValueError as e:
            print(f"Error fetching renaming rules: {e}")
            return

        for group in tfm.dfs.keys():
            # Get relevant renaming rules for the current group
            group_rules = self._get_group_rules(renaming_rules, group)

            if not group_rules:
                continue

            # Apply renaming rules and track keys not found in the DataFrame
            df = tfm.dfs[group]
            df, not_found_keys = self._apply_renaming(df, group_rules)
            tfm.dfs[group] = df
            
            # Print any renaming rules that were not used
            if not_found_keys and self.verbose:
                print(f"\nGroup '{group}' has the following renaming rules not applied:")
                for old_col in not_found_keys:
                    print(f"Key '{old_col}' from renaming rules was not found in the DataFrame.")

    def _get_group_rules(self, 
                         renaming_rules: OrderedDict, # Renaming rules
                         group: str # Group name to filter rules
                         ) -> OrderedDict: # Renaming rules applicable to the specified group
        "Retrieve and merge renaming rules for the specified group based on the encoding type."
        relevant_rules = [rules for key, rules in renaming_rules.items() if group in key]
        merged_rules = OrderedDict()
        for rules in relevant_rules:
            merged_rules.update(rules)
        return merged_rules

    def _apply_renaming(self, 
                        df: pd.DataFrame, # DataFrame to modify
                        rename_rules: OrderedDict # Renaming rules
                        ) -> tuple: # (Renamed and filtered df, Column names from renaming rules that were not found in the DataFrame)
        """
        Select columns based on renaming rules and apply renaming, only for existing columns
        while maintaining the order of the dictionary columns."""
        existing_columns = set(df.columns)
        valid_rules = OrderedDict((old_col, new_col) for old_col, new_col in rename_rules.items() if old_col in existing_columns)

        # Create a list to maintain the order of columns
        columns_to_keep = [col for col in rename_rules.keys() if col in existing_columns]
        columns_to_keep += [new_col for old_col, new_col in valid_rules.items() if new_col in df.columns]

        df = df[list(OrderedDict.fromkeys(columns_to_keep))]

        # Apply renaming
        df.rename(columns=valid_rules, inplace=True)

        # Determine which keys were not found
        not_found_keys = set(rename_rules.keys()) - existing_columns
        return df, not_found_keys


# %% ../../nbs/handlers/helcom.ipynb 197
kw = ['oceanography', 'Earth Science > Oceans > Ocean Chemistry> Radionuclides',
      'Earth Science > Human Dimensions > Environmental Impacts > Nuclear Radiation Exposure',
      'Earth Science > Oceans > Ocean Chemistry > Ocean Tracers, Earth Science > Oceans > Marine Sediments',
      'Earth Science > Oceans > Ocean Chemistry, Earth Science > Oceans > Sea Ice > Isotopes',
      'Earth Science > Oceans > Water Quality > Ocean Contaminants',
      'Earth Science > Biological Classification > Animals/Vertebrates > Fish',
      'Earth Science > Biosphere > Ecosystems > Marine Ecosystems',
      'Earth Science > Biological Classification > Animals/Invertebrates > Mollusks',
      'Earth Science > Biological Classification > Animals/Invertebrates > Arthropods > Crustaceans',
      'Earth Science > Biological Classification > Plants > Macroalgae (Seaweeds)']

# %% ../../nbs/handlers/helcom.ipynb 198
def get_attrs(
    tfm: Transformer, # Transformer object
    zotero_key: str, # Zotero dataset record key
    kw: list = kw # List of keywords
    ) -> dict: # Global attributes
    "Retrieve all global attributes."
    return GlobAttrsFeeder(tfm.dfs, cbs=[
        BboxCB(),
        DepthRangeCB(),
        TimeRangeCB(cfg()),
        ZoteroCB(zotero_key, cfg=cfg()),
        KeyValuePairCB('keywords', ', '.join(kw)),
        KeyValuePairCB('publisher_postprocess_logs', ', '.join(tfm.logs))
        ])()

# %% ../../nbs/handlers/helcom.ipynb 200
def enums_xtra(
    tfm: Transformer, # Transformer object
    vars: list # List of variables to extract from the transformer
    ):
    "Retrieve a subset of the lengthy enum as `species_t` for instance."
    enums = Enums(lut_src_dir=lut_path(), cdl_enums=cdl_cfg()['enums'])
    xtras = {}
    for var in vars:
        unique_vals = tfm.unique(var)
        if unique_vals.any():
            xtras[f'{var}_t'] = enums.filter(f'{var}_t', unique_vals)
    return xtras

# %% ../../nbs/handlers/helcom.ipynb 202
def encode(
    fname_in: str, # Input file name
    fname_out_nc: str, # Output file name
    nc_tpl_path: str, # NetCDF template file name
    **kwargs # Additional arguments
    ) -> None:
    "Encode data to NetCDF."
    dfs = load_data(fname_in)
    tfm = Transformer(dfs, cbs=[AddSampleTypeIdColumnCB(),
                            LowerStripNameCB(col_src='NUCLIDE'),
                            RemapNuclideNameCB(lut_nuclides),
                            AddNuclideIdColumnCB(col_value='NUCLIDE'),
                            ParseTimeCB(),
                            EncodeTimeCB(cfg()),
                            SanitizeValue(coi_val),       
                            NormalizeUncCB(),
                            RemapCB(fn_lut=lut_biota, col_remap='species', col_src='RUBIN', dest_grps='biota'),
                            RemapCB(lut_tissues, 'body_part', 'TISSUE', 'biota'),
                            RemapCB(lut_biogroup, 'bio_group', 'species', 'biota'),
                            RemapTaxonInformationCB(lut_taxon),
                            RemapSedimentCB(lut_sediments),
                            RemapUnitCB(),
                            RemapDetectionLimitCB(coi_dl, lut_dl),
                            RemapFiltCB(lut_filtered),
                            AddSampleLabCodeCB(),
                            AddMeasurementNoteCB(lut_method),
                            RemapStationIdCB(),
                            RemapSedSliceTopBottomCB(),
                            LookupDryWetRatio(),
                            ParseCoordinates(ddmm_to_dd),
                            SanitizeLonLatCB(),
                            SelectAndRenameColumnCB(get_renaming_rules, encoding_type='netcdf'),
                            ReshapeLongToWide()
                            ])
    tfm()
    encoder = NetCDFEncoder(tfm.dfs, 
                            src_fname=nc_tpl_path,
                            dest_fname=fname_out_nc, 
                            global_attrs=get_attrs(tfm, zotero_key=zotero_key, kw=kw),
                            verbose=kwargs.get('verbose', False),
                            enums_xtra=enums_xtra(tfm, vars=['species', 'body_part'])
                           )
    encoder.encode()
