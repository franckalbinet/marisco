# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/handlers/maris_legacy.ipynb.

# %% auto 0
__all__ = ['fname_in', 'dir_dest', 'cois_renaming_rules', 'dl_name_to_id', 'kw', 'DataLoader', 'get_zotero_key', 'get_fname',
           'CastStationToStringCB', 'DropNAColumnsCB', 'SanitizeDetectionLimitCB', 'ParseTimeCB', 'get_attrs', 'encode']

# %% ../../nbs/handlers/maris_legacy.ipynb 6
from tqdm import tqdm
from pathlib import Path
import fastcore.all as fc
import pandas as pd
import numpy as np
from typing import Optional, List

from marisco.callbacks import (
    Callback, 
    Transformer, 
    SanitizeLonLatCB, 
    EncodeTimeCB, 
    RenameColumnsCB, 
    SelectColumnsCB,
    UniqueIndexCB
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
    NC_GROUPS,
    lut_path,
    cfg,
    nc_tpl_path,
    Enums, 
    get_lut
    )

from ..encoders import NetCDFEncoder

import warnings
warnings.filterwarnings('ignore')

# %% ../../nbs/handlers/maris_legacy.ipynb 10
# fname_in = Path().home() / 'pro/data/maris/2024-11-20 MARIS_QA_shapetype_id=1.txt'
fname_in = Path().home() / 'pro/data/maris/2025-06-03 MARIS_QA_shapetype_id = 1.txt'

dir_dest = '../../_data/output/dump'

# %% ../../nbs/handlers/maris_legacy.ipynb 15
class DataLoader:
    "Load specific MARIS dataset through its ref_id."
    LUT = {
        'Biota': 'BIOTA', 
        'Seawater': 'SEAWATER', 
        'Sediment': 'SEDIMENT', 
        'Suspended matter': 'SUSPENDED_MATTER'
    }

    def __init__(self, 
                 fname: str, # Path to the MARIS global dump file
                 exclude_ref_id: Optional[List[int]]=[9999] # Whether to filter the dataframe by ref_id
                 ):
        fc.store_attr()
        self.df = self._load_data()

    def _load_data(self):
        df = pd.read_csv(self.fname, sep='\t', encoding='utf-8', low_memory=False)
        return df[~df.ref_id.isin(self.exclude_ref_id)] if self.exclude_ref_id else df

    def __call__(self, 
                 ref_id: int # Reference ID of interest
                 ) -> dict: # Dictionary of dataframes
        df = self.df[self.df.ref_id == ref_id].copy() if ref_id else self.df.copy()
        return {self.LUT[name]: grp for name, grp in df.groupby('samptype') if name in self.LUT}

# %% ../../nbs/handlers/maris_legacy.ipynb 16
def get_zotero_key(dfs):
    "Retrieve Zotero key from MARIS dump."
    return dfs[next(iter(dfs))][['zoterourl']].iloc[0].values[0].split('/')[-1]

# %% ../../nbs/handlers/maris_legacy.ipynb 17
def get_fname(dfs):
    "Get NetCDF filename."
    return f"{next(iter(dfs.values()))['ref_id'].iloc[0]}.nc"

# %% ../../nbs/handlers/maris_legacy.ipynb 23
cois_renaming_rules = {
    'sample_id': 'SMP_ID',
    'latitude': 'LAT',
    'longitude': 'LON',
    'begperiod': 'TIME',
    'sampdepth': 'SMP_DEPTH',
    'totdepth': 'TOT_DEPTH',
    'station': 'STATION',
    'uncertaint': 'UNC',
    'unit_id': 'UNIT',
    'detection': 'DL',
    'area_id': 'AREA',
    'species_id': 'SPECIES',
    'biogroup_id': 'BIO_GROUP',
    'bodypar_id': 'BODY_PART',
    'sedtype_id': 'SED_TYPE',
    'volume': 'VOL',
    'salinity': 'SAL',
    'temperatur': 'TEMP',
    'sampmet_id': 'SAMP_MET',
    'prepmet_id': 'PREP_MET',
    'counmet_id': 'COUNT_MET',
    'activity': 'VALUE',
    'nuclide_id': 'NUCLIDE',
    'sliceup': 'TOP',
    'slicedown': 'BOTTOM'
}

# %% ../../nbs/handlers/maris_legacy.ipynb 28
class CastStationToStringCB(Callback):
    "Convert STATION column to string type, filling any missing values with empty string"
    def __call__(self, tfm):
        for k in tfm.dfs.keys():
            if 'STATION' in tfm.dfs[k].columns:
                tfm.dfs[k]['STATION'] = tfm.dfs[k]['STATION'].fillna('').astype('string')

# %% ../../nbs/handlers/maris_legacy.ipynb 32
class DropNAColumnsCB(Callback):
    "Drop variable containing only NaN or 'Not available' (id=0 in MARIS lookup tables)."
    def __init__(self, na_value=0): fc.store_attr()
    def isMarisNA(self, col): 
        return len(col.unique()) == 1 and col.iloc[0] == self.na_value
    
    def dropMarisNA(self, df):
        na_cols = [col for col in df.columns if self.isMarisNA(df[col])]
        return df.drop(labels=na_cols, axis=1)
        
    def __call__(self, tfm):
        for k in tfm.dfs.keys():
            tfm.dfs[k] = tfm.dfs[k].dropna(axis=1, how='all')
            tfm.dfs[k] = self.dropMarisNA(tfm.dfs[k])

# %% ../../nbs/handlers/maris_legacy.ipynb 36
dl_name_to_id = lambda: get_lut(lut_path(), 
                                'dbo_detectlimit.xlsx', 
                                key='name', 
                                value='id')

# %% ../../nbs/handlers/maris_legacy.ipynb 38
class SanitizeDetectionLimitCB(Callback):
    "Assign Detection Limit name to its id based on MARIS nomenclature."
    def __init__(self,
                 fn_lut=dl_name_to_id,
                 dl_name='DL'):
        fc.store_attr()

    def __call__(self, tfm):
        lut = self.fn_lut()
        for k in tfm.dfs.keys():
            tfm.dfs[k][self.dl_name] = tfm.dfs[k][self.dl_name].replace(lut)

# %% ../../nbs/handlers/maris_legacy.ipynb 42
class ParseTimeCB(Callback):
    "Parse time column from MARIS dump."
    def __init__(self,
                 time_name='TIME'):
        fc.store_attr()
        
    def __call__(self, tfm):
        for k in tfm.dfs.keys():
            tfm.dfs[k][self.time_name] = pd.to_datetime(tfm.dfs[k][self.time_name], format='ISO8601')

# %% ../../nbs/handlers/maris_legacy.ipynb 52
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

# %% ../../nbs/handlers/maris_legacy.ipynb 53
def get_attrs(tfm, zotero_key, kw=kw):
    "Retrieve global attributes from MARIS dump."
    return GlobAttrsFeeder(tfm.dfs, cbs=[
        BboxCB(),
        DepthRangeCB(),
        TimeRangeCB(),
        ZoteroCB(zotero_key, cfg=cfg()),
        KeyValuePairCB('keywords', ', '.join(kw)),
        KeyValuePairCB('publisher_postprocess_logs', ', '.join(tfm.logs))
        ])()

# %% ../../nbs/handlers/maris_legacy.ipynb 55
def encode(
    fname_in: str, # Path to the MARIS dump data in CSV format
    dir_dest: str, # Path to the folder where the NetCDF output will be saved
    **kwargs # Additional keyword arguments
    ):
    "Encode MARIS dump to NetCDF."
    dataloader = DataLoader(fname_in)
    ref_ids = kwargs.get('ref_ids')
    if ref_ids is None:
        ref_ids = dataloader.df.ref_id.unique()
    print('Encoding ...')
    for ref_id in tqdm(ref_ids, leave=False):
        # if ref_id == 736: continue
        dfs = dataloader(ref_id=ref_id)
        print(get_fname(dfs))
        tfm = Transformer(dfs, cbs=[
            SelectColumnsCB(cois_renaming_rules),
            RenameColumnsCB(cois_renaming_rules),
            CastStationToStringCB(),
            DropNAColumnsCB(),
            SanitizeDetectionLimitCB(),
            ParseTimeCB(),
            EncodeTimeCB(),
            SanitizeLonLatCB(),
            UniqueIndexCB(),
            ])
        
        tfm()
        encoder = NetCDFEncoder(tfm.dfs, 
                                dest_fname=Path(dir_dest) / get_fname(dfs), 
                                global_attrs=get_attrs(tfm, zotero_key=get_zotero_key(dfs), kw=kw),
                                verbose=kwargs.get('verbose', False)
                                )
        encoder.encode()
