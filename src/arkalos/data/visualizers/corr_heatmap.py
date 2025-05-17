
import polars as pl
import pandas as pd
import numpy as np
import altair as alt

class CorrHeatmap:

    SCHEME = 'redblue'

    _meltedCorrDf: pl.DataFrame

    def __init__(self, data: pl.DataFrame):
        df_corr = data.corr()
        # Polars' corr() does not store row names (column names) explicitly
        # Add original column names as a new column  
        df_corr = df_corr.with_columns(pl.Series(name="variable1", values=data.columns))  

        # Melt the correlation matrix (Polars)  
        self._meltedCorrDf = df_corr.unpivot(  
            index="variable1",  # Row labels (original column names)  
            variable_name="variable2",  # Column labels  
            value_name="correlation"  # Correlation values  
        ).filter(  
            pl.col("variable1") >= pl.col("variable2")  # Keep only lower triangle  
        )
        self._meltedCorrDf

    def create(self) -> alt.Chart:

        # Base chart  
        base = alt.Chart(self._meltedCorrDf).encode(  
            x=alt.X("variable2:N", title=None),  # Column names  
            y=alt.Y("variable1:N", title=None),  # Row names  
            color=alt.Color(  
                "correlation:Q",  
                scale=alt.Scale(domain=(-1, 1), scheme=self.SCHEME)  # Diverging color scale  
            ),  
            tooltip=[ 
                alt.Tooltip("variable1:N", title="Variable 1"),  
                alt.Tooltip("variable2:N", title="Variable 2"),  
                alt.Tooltip("correlation:Q", title="Correlation", format=".2f")
            ]  
        )  

        # Heatmap cells  
        heatmap = base.mark_rect()  

        # Text labels (black for readability)  
        text = base.mark_text(baseline="middle").encode(  
            text=alt.Text("correlation:Q", format=".2f"),  
            color=alt.value("black")  # Ensure text is visible on all backgrounds  
        )  

        # Combine and configure  
        return (heatmap + text).properties(width=700, height=700).configure_axis(labelFontSize=10) 