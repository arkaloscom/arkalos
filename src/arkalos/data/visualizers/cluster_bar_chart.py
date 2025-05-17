
import polars as pl
import pandas as pd
import altair as alt
from sklearn.ensemble import RandomForestClassifier # type: ignore



class ClusterBarChart:
    '''Determine and plot which features matter most for distinguishing ALL clusters'''

    DEFAULT_CHARTS_PER_ROW: int = 5

    _df: pl.DataFrame
    _clusterColName: str
    _importantFeatures: list
    _importances: pl.Series

    def __init__(self, data: pl.DataFrame, cluster_col_name: str = '_cluster'):
        if not isinstance(data, pl.DataFrame):
            data = pl.DataFrame(data)
        self._df = data
        self._clusterColName = cluster_col_name
        self._trainPredictOverallImportances()

    def _trainPredictOverallImportances(self) -> None:
        X = self._df.drop([self._clusterColName])
        y = self._df[self._clusterColName]

        model = RandomForestClassifier(n_estimators=100)
        model.fit(X, y)

        self._importances = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)
        self._importantFeatures = self._importances.index.tolist() # type: ignore

    def create(self) -> alt.VConcatChart:
        charts = []
        for feature in self._importantFeatures:
            chart = alt.Chart(self._df).mark_bar().encode(
                x=alt.X(f'mean({feature}):Q', title='Avg'),
                y=alt.Y(f'{self._clusterColName}:N', title='Cluster'),
                tooltip=[f'mean({feature}):Q'],
                color=f'{self._clusterColName}:N'
            ).properties(
                width=150,
                height=100,
                title=alt.TitleParams(
                    text=f"{feature}",
                    subtitle=f"(Importance: {self._importances[feature]:.3f})"
                ),
            )
            charts.append(chart)

        per_row = self.DEFAULT_CHARTS_PER_ROW
        # Split charts into rows of DEFAULT_CHARTS_PER_ROW
        rows = [alt.hconcat(*charts[i:i+per_row]) for i in range(0, len(charts), per_row)]

        # Stack rows vertically
        # Combine rows into a single chart
        final_chart = alt.vconcat(*rows)  
        return final_chart
