
from typing import Any, TypedDict, Literal
from enum import StrEnum
import json

import numpy as np
import pandas as pd
import polars as pl
import altair as alt
import scipy.cluster.hierarchy as hr

from sklearn.cluster import AgglomerativeClustering # type: ignore



class _DendrogramResult(TypedDict):
    color_list: list[str]
    icoord: list[list[int]]
    dcoord: list[list[int]]
    ivl: list[str]
    leaves: list[int] | None
    leaves_color_list: list[str]



# Map Matplotlib color codes to Altair hex values
# https://matplotlib.org/stable/users/explain/colors/colors.html
# default color/property cycle from Tableau T10
class ColorMap(StrEnum):
    C0 = '#1f77b4'  # Blue
    C1 = '#ff7f0e'  # Orange
    C2 = '#2ca02c'  # Green
    C3 = '#d62728'  # Red
    C4 = '#9467bd'  # Purple
    C5 = '#8c564b'  # Brown
    C6 = '#e377c2'  # Pink
    C7 = '#7f7f7f'  # Gray
    C8 = '#bcbd22'  # Olive
    C9 = '#17becf'  # Cyan

    @classmethod
    def codeToHex(cls, code: str, default: str = '#000000') -> str:
        """Retrieve hex color for a code (e.g., 'C0'), with fallback to default."""
        try:
            return cls[code].value
        except KeyError:
            return default



class Dendrogram:

    DEFAULT_PADDING: dict[str, int] = {
        "left": 12, "top": 12, "right": 12, "bottom": 12
    }
    DEFAULT_WIDTH: int = 600
    DEFAULT_HEIGHT: int = 400
    DEFAULT_TITLE = 'Bottom-Up Hierarchical Clustering Dendrogram (Truncated)'
    DEFAULT_TITLE_X = 'Number of points in node (or index of point if no parenthesis)'
    DEFAULT_TITLE_Y = 'Distance'

    _model: AgglomerativeClustering
    _linkageMatrix: np.ndarray
    _dendroData: _DendrogramResult
    _UShapeDataFrame: pd.DataFrame
    _lineAt: float|None

    def __init__( 
        self,
        data: AgglomerativeClustering|pl.DataFrame|pd.DataFrame|np.ndarray|list[dict], 
        p: int=3, 
        **dendrogram_kwargs
    ):
        model = data
        if not isinstance(model, AgglomerativeClustering):
            model = self._createModelFromData(model)
        self._model = model
        self._linkageMatrix = self._createLinkageMatrix(model)
        self._dendroData = self._getSciPyDendrogramData(
            self._linkageMatrix,
            p=p,
            truncate_mode="level",
            show_contracted=True,
            **dendrogram_kwargs
        )
        self._UShapeDataFrame = self._createUShapeDataFrame(self._dendroData)
        self._lineAt = None

    def create(self) -> alt.Chart:
        return self._createAltairChart()
    
    def withLineAt(self, height: float) -> 'Dendrogram':
        self._lineAt = height
        return self
    
    def withLineAuto(self) -> 'Dendrogram':
        self._lineAt = self.findOptimalCutHeight()
        return self
    
    def height(self) -> int:
        return self._model.distances_.max()
    
    def countClustersAuto(self) -> int:
        return self.countClustersAt(self.findOptimalCutHeight())
    
    def countClustersAt(self, height: float) -> int:
        """Calculate number of clusters at given height (threshold)"""
        clusters = hr.fcluster(self._linkageMatrix, height, criterion='distance')
        return len(np.unique(clusters))
    
    def findOptimalCutHeight(self):
        # The optimal cut height can be chosen within this largest gap.
        # A common heuristic is to cut in the middle of this largest gap.
        # The merge before the largest gap is at merge_distances[largest_diff_index]
        # The merge after the largest gap is at merge_distances[largest_diff_index + 1]

        merge_distances = self._linkageMatrix[:, 2]
        distance_diffs = np.diff(merge_distances)
        largest_diff_index = np.argmax(distance_diffs)
        cut_threshold = (
            merge_distances[largest_diff_index] + merge_distances[largest_diff_index + 1]
        ) / 2.0
        return cut_threshold
    

    
    def _createModelFromData(self, 
        data: pl.DataFrame|pd.DataFrame|np.ndarray|list[dict]
    ) -> AgglomerativeClustering:
        
        model = AgglomerativeClustering(distance_threshold=0, n_clusters=None).fit(data)
        return model
    
    def _createLinkageMatrix(self, model: AgglomerativeClustering) -> np.ndarray:
        '''
        Create linkage matrix, a 2D array where each row is:
        [child1, child2, distance, sample_count]
        '''
        counts = np.zeros(model.children_.shape[0])
        n_samples = len(model.labels_)
        for i, merge in enumerate(model.children_):
            current_count = 0
            for child_idx in merge:
                if child_idx < n_samples:
                    current_count += 1
                else:
                    current_count += counts[child_idx - n_samples]
            counts[i] = current_count
        
        linkage_matrix = np.column_stack(
            [model.children_, model.distances_, counts]
        ).astype(float)

        return linkage_matrix

    def _getSciPyDendrogramData(self, 
        linkage_matrix: np.ndarray,
        p: int = 3,
        truncate_mode: Literal['lastp', 'level'] = 'level',
        show_contracted: bool =True,
        **dendrogram_kwargs: Any
    ) -> _DendrogramResult:
        
        ddata = hr.dendrogram(
            linkage_matrix,
            no_plot=True,
            p=p,
            truncate_mode=truncate_mode,
            show_contracted=show_contracted,
            **dendrogram_kwargs,
            count_sort=False,
            show_leaf_counts=True
        )
        return ddata

    def _createUShapeSegments(self, ddata: _DendrogramResult) -> list[dict[str, Any]]:
        if not ddata['leaves']:
            return []
        
        segments = []
        all_icoord = [x for sublist in ddata['icoord'] for x in sublist]
        icoord_min = min(all_icoord)
        icoord_max = max(all_icoord)
        n_leaves = len(ddata['leaves'])
        
        for idx, (xs, ys) in enumerate(zip(ddata['icoord'], ddata['dcoord'])):
            # Normalize x coordinates to [0, n_leaves-1]
            normalized_xs = [(x - icoord_min) / (icoord_max - icoord_min) * (n_leaves - 1)
                            for x in xs]
            color = ColorMap.codeToHex(ddata['color_list'][idx])
            
            # Create complete U-shaped segment
            segments.append({
                'x': normalized_xs,
                'y': ys,
                'color': color,
                'segment': idx,
                'order': [0, 1, 2, 3]  # Drawing order for U-shape
            })

        return segments

    def _createUShapeDataFrame(self, ddata: _DendrogramResult) -> pd.DataFrame:
        segments = self._createUShapeSegments(ddata)
        return pd.DataFrame(segments).explode(['x', 'y', 'order'])
    
    def _getXLabels(self) -> list[str]:
        return self._dendroData['ivl']
    
    def _createXAxis(self) -> alt.X:
        custom_labels = self._getXLabels()

        # Format the Vega expression to map tick index to label
        label_expr = f"{json.dumps(custom_labels)}[datum.value]"

        return alt.X(
            'x:Q',
            scale=alt.Scale(domain=[-0.5, len(custom_labels) - 0.5]),  # Add padding
            axis=alt.Axis(
                title=self.DEFAULT_TITLE_X,
                titlePadding=12,
                titleFontSize=16,
                values=list(range(len(custom_labels))),
                labelExpr=label_expr,
                # labelAngle=90,
                labelLimit=120,
                ticks=False,
                grid=False,
                domain=False
            )
        )

    def _createYAxis(self) -> alt.Y:
        return alt.Y(
            'y:Q', 
            axis=alt.Axis(
                title=self.DEFAULT_TITLE_Y,
                titlePadding=12,
                format='d',
                grid=False,
                domain=False
            )
        )
    
    def _createTitle(self, title_text: str) -> alt.TitleParams:
        return alt.TitleParams(
            title_text,
            anchor='middle',
            offset=4,
            fontSize=16,
            fontWeight=600
        )
    
    def _createAltairChart(self) -> alt.Chart:
        chart = alt.Chart(self._UShapeDataFrame).mark_line().encode(
            x=self._createXAxis(),
            y=self._createYAxis(),
            color=alt.Color('color:N', scale=None, legend=None),
            detail='segment:N',
            order='order:O'
        )
        
        title_text = self.DEFAULT_TITLE
        
        if self._lineAt:
            # Create threshold line
            rule = alt.Chart().mark_rule(color='red', strokeDash=[2, 2]).encode(
                y=alt.Y('threshold:Q')
            ).transform_calculate(threshold=f'{self._lineAt}')
            n_clusters = self.countClustersAt(self._lineAt)
            
            chart = chart + rule
            title_text += f"\n(Auto-detected clusters: {n_clusters})"
        
        title_cfg = self._createTitle(title_text)

        return chart.properties(
            width=self.DEFAULT_WIDTH,
            height=self.DEFAULT_HEIGHT,
            title=title_cfg,
            padding=self.DEFAULT_PADDING
        ).configure_view().configure_axis(
            labelFontSize=14,
            titleFontSize=16,
            labelPadding=8,
            labelLimit=120,
            labelOverlap=True
        )
    