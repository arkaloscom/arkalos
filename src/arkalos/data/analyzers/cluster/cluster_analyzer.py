
from typing import Any
import numpy as np
import polars as pl
import pandas as pd
import altair as alt
from sklearn.cluster import AgglomerativeClustering, KMeans, DBSCAN # type: ignore
from kneed import KneeLocator # type: ignore
from sklearn.neighbors import NearestNeighbors # type: ignore

from arkalos.data.visualizers.dendrogram import Dendrogram
from arkalos.data.visualizers.elbow_plot import ElbowPlot
from arkalos.data.visualizers.corr_heatmap import CorrHeatmap
from arkalos.data.visualizers.cluster_bar_chart import ClusterBarChart

class ClusterAnalyzer:

    _df: pl.DataFrame
    _clusterColName: str
    _clusteringDone: bool
    _corrHeatmap: CorrHeatmap|None
    _dendrogram: Dendrogram|None
    _elbowPlot: ElbowPlot|None
    _clusterBarChart: ClusterBarChart|None



    def __init__(self, 
        data: pl.DataFrame|pd.DataFrame|list[dict[str, Any]], 
        cluster_col_name: str = '_cluster'
    ):
        if not isinstance(data, pl.DataFrame):
            data = pl.DataFrame(data)
        self._df = data
        self._clusterColName = cluster_col_name
        self._clusteringDone = False
        self._dendrogram = None
        self._elbowPlot = None
        self._clusterBarChart = None
        self._corrHeatmap = None



    def _getCorrHeatmap(self) -> CorrHeatmap:
        if self._corrHeatmap is None:
            self._corrHeatmap = CorrHeatmap(self._df)
        return self._corrHeatmap

    def createCorrHeatmap(self) -> alt.Chart:
        return self._getCorrHeatmap().create()



    def _getDendrogram(self) -> Dendrogram:
        if self._dendrogram is None:
            self._dendrogram = Dendrogram(self._df).withLineAuto()
        return self._dendrogram

    def createDendrogram(self) -> alt.Chart:
        return self._getDendrogram().create()

    def findNClustersViaDendrogram(self) -> int:
        '''Find optimal cluster number by cutting dendrogram'''
        return self._getDendrogram().countClustersAuto()



    def _getElbowPlot(self) -> ElbowPlot:
        if self._elbowPlot is None:
            self._elbowPlot = ElbowPlot(self._df)
        return self._elbowPlot

    def createElbowPlot(self) -> alt.Chart:
        return self._getElbowPlot().create()

    def findNClustersViaElbow(self) -> int:
        '''Find optimal cluster number using elbow method'''
        return self._getElbowPlot().countClustersAuto()



    def _clusterAddCol(self, cluster_col: np.ndarray) -> None:
        self._df = self._df.with_columns(pl.Series(self._clusterColName, cluster_col))
        self._clusteringDone = True

    def _clusterHierarchicalBottomUp(self, n_clusters: int) -> np.ndarray:
        return AgglomerativeClustering(n_clusters=n_clusters).fit_predict(self._df)
    
    def _clusterKMeans(self, n_clusters: int) -> np.ndarray:
        return KMeans(n_clusters=n_clusters, random_state=42, n_init=10).fit_predict(self._df)
    
    def clusterHierarchicalBottomUp(self, n_clusters: int) -> None:
        cluster_labels = self._clusterHierarchicalBottomUp(n_clusters)
        self._clusterAddCol(cluster_labels)

    def clusterKMeans(self, n_clusters: int) -> None:
        cluster_labels = self._clusterKMeans(n_clusters)
        self._clusterAddCol(cluster_labels)



    def _getClusterBarChart(self) -> ClusterBarChart:
        if self._clusterBarChart is None:
            self._clusterBarChart = ClusterBarChart(self._df, self._clusterColName)
        return self._clusterBarChart

    def createClusterBarChart(self) -> alt.VConcatChart:
        if not self._clusteringDone:
            raise ValueError('Can\'t create Cluster Bar Chart. ' \
            'Cluster data first with any of the cluster...() methods')
        return self._getClusterBarChart().create()



    def printSummary(self) -> None:
        if not self._clusteringDone:
            raise ValueError('Can\'t create Summary of Clusters. ' \
            'Cluster data first with any of the cluster...() methods')
        unique_clusters = self._df.select(pl.col(self._clusterColName).unique()).to_series().to_list()
        total_records = len(self._df)

        for cluster_id in unique_clusters:
            cluster_df = self._df.filter(self._df[self._clusterColName] == cluster_id)
            cluster_size = len(cluster_df)
            
            # Calculate feature importance (based on deviation from global mean)
            key_features: list = []

            print('Cluster:', cluster_id)
            print('Count:', cluster_size)
            print('%:', round(cluster_size / total_records * 100, 2))
            print('Top features (with significant deviation):')
            
            for col in cluster_df.columns:
                if col == '_cluster':
                    continue
                global_mean = float(self._df[col].mean()) # type: ignore
                global_std = float(self._df[col].std())  # type: ignore
                
                if global_std == 0:
                    continue  # Skip features with no variation
                
                mean = float(cluster_df[col].mean())  # type: ignore
                min = float(cluster_df[col].min())  # type: ignore
                max = float(cluster_df[col].max())  # type: ignore
                std = float(cluster_df[col].std() or 0)  # type: ignore
                deviation = (mean - global_mean) / global_std

                # Only include features with significant deviation
                if abs(deviation) > 0.5:
                    direction = '^' if deviation > 0 else 'v'
                    
                    key_features.append({
                        'feature': col,
                        'importance': abs(round(deviation, 2)),
                        'direction': direction,
                        'avg': round(mean, 1),
                        'min': round(min, 1),
                        'max': round(max, 1),
                        'std': round(std, 1),
                        'imp': str(abs(round(deviation, 2))) + ' ' + direction,
                    })
            
            key_features.sort(key=lambda x: x['importance'], reverse=True)

            if key_features:
                print(pd.DataFrame(key_features)[['feature', 'imp', 'min', 'max', 'avg', 'std']])

            print()
