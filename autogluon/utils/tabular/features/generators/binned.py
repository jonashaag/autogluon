import copy
import logging

import numpy as np
from pandas import DataFrame

from .abstract import AbstractFeatureGenerator
from .. import binning
from ..feature_metadata import R_INT, R_FLOAT, S_BINNED

logger = logging.getLogger(__name__)


# TODO: Add more parameters (#bins, possibly pass in binning function as an argument for full control)
class BinnedFeatureGenerator(AbstractFeatureGenerator):
    def __init__(self, inplace=False, **kwargs):
        super().__init__(**kwargs)
        self.inplace = inplace

    def _fit_transform(self, X: DataFrame, **kwargs) -> (DataFrame, dict):
        self._bin_map = self._get_bin_map(X=X)
        X_out = self._transform(X)
        type_group_map_special = copy.deepcopy(self.feature_metadata_in.type_group_map_special)
        type_group_map_special[S_BINNED] += list(X_out.columns)
        return X_out, type_group_map_special

    def _transform(self, X: DataFrame) -> DataFrame:
        return self._transform_bin(X)

    def _infer_features_in(self, X, y=None) -> list:
        features_to_bin = self.feature_metadata_in.get_features(valid_raw_types=[R_INT, R_FLOAT])
        return features_to_bin

    def _get_bin_map(self, X: DataFrame) -> dict:
        return binning.generate_bins(X, list(X.columns))

    def _transform_bin(self, X: DataFrame):
        if self._bin_map:
            if not self.inplace:
                X = X.copy(deep=True)
            for column in self._bin_map:
                X[column] = binning.bin_column(series=X[column], mapping=self._bin_map[column])
            X = X.astype(np.uint8)  # TODO: output dtype based on #bins
        return X