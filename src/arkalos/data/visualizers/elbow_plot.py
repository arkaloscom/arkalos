
import polars as pl
import pandas as pd
import numpy as np
import altair as alt
from sklearn.cluster import KMeans # type: ignore
from kneed import KneeLocator # type: ignore

class ElbowPlot:
    
    DEFAULT_PADDING: dict[str, int] = {
        "left": 12, "top": 12, "right": 12, "bottom": 12
    }
    DEFAULT_WIDTH: int = 600
    DEFAULT_HEIGHT: int = 400
    DEFAULT_TITLE = 'Elbow Method for Optimal k'
    DEFAULT_TITLE_X = 'Number of Clusters'
    DEFAULT_TITLE_Y = 'Inertia (Within-Cluster Sum of Squares)'

    _data: np.ndarray|pl.DataFrame|pd.DataFrame
    _maxClusters: int
    _inertias: list
    _elbowDf: pd.DataFrame

    def __init__(self, data: np.ndarray|pl.DataFrame|pd.DataFrame, max_clusters: int = 10):
         self._data = data
         self._maxClusters = max_clusters
         self._inertias = self._createKMeansInertias()
         self._elbowDf = self._createElbowDataFrame(self._inertias)

    def create(self) -> alt.Chart:
        return self._createAltairChart()
    
    def countClustersAuto(self) -> int:
        # Find the elbow point
        try:
            kneedle = KneeLocator(
                range(1, self._maxClusters + 1), 
                self._inertias, 
                curve='convex', 
                direction='decreasing'
            )
            optimalK = kneedle.elbow
            if optimalK is None:
                # Fallback to simple heuristic
                optimalK = 2  # Default to 2 clusters
        except:
            # Simple heuristic if knee detection fails
            diffs = np.diff(self._inertias)
            optimalK = np.argmin(diffs) + 2
            
        return optimalK
    
    def _createKMeansInertias(self) -> list:
        inertias = []
        for k in range(1, self._maxClusters + 1):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(self._data)
            inertias.append(kmeans.inertia_)
        return inertias
    
    def _createElbowDataFrame(self, inertias):
        return pd.DataFrame({
            'clusters': list(range(1, self._maxClusters + 1)),
            'inertia': inertias
        })
    
    def _createXAxis(self) -> alt.X:
        return alt.X('clusters:Q', title=self.DEFAULT_TITLE_X)

    def _createYAxis(self) -> alt.Y:
        return alt.Y('inertia:Q', title=self.DEFAULT_TITLE_Y)
    
    def _createTitle(self, title_text: str) -> alt.TitleParams:
        return alt.TitleParams(
            title_text,
            anchor='middle',
            offset=4,
            fontSize=16,
            fontWeight=600
        )
    
    def _createAltairChart(self) -> alt.Chart:
        chart = alt.Chart(self._elbowDf).mark_line(point=True).encode(
            x=self._createXAxis(),
            y=self._createYAxis(),
        ).properties(
            title=self.DEFAULT_TITLE,
            width=self.DEFAULT_WIDTH,
            height=self.DEFAULT_HEIGHT
        )

        optimalK = self.countClustersAuto()
        
        # Add vertical line for optimal k
        vline = alt.Chart(pd.DataFrame({'x': [optimalK]})).mark_rule(color='red').encode(
            x='x:Q'
        )
        
        # Add annotation for optimal k
        text = alt.Chart(pd.DataFrame({'x': [optimalK], 'y': [max(self._inertias) * 0.9]})).mark_text(
            align='left',
            baseline='middle',
            dx=5,
            fontSize=12
        ).encode(
            x='x:Q',
            y='y:Q',
            text=alt.value(f'Optimal k = {optimalK}')
        )
        
        return chart + vline + text
    