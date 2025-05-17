
import polars as pl
import altair as alt

class BarChart:

    DEFAULT_PADDING: dict[str, int] = {
        "left": 12, "top": 12, "right": 12, "bottom": 12
    }
    DEFAULT_WIDTH: int = 600
    DEFAULT_HEIGHT: int = 400

    _df: pl.DataFrame
    _colNameX: str
    _colNameY: str|None

    def __init__(self, df: pl.DataFrame, col_name_x: str, col_name_y: str|None = None):
        if col_name_y is None:
            self._df = df.get_column(col_name_x).value_counts()
        else:
            self._df = df
        self._colNameX = col_name_x
        self._colNameY = col_name_y

    def _createXAxis(self):
        return alt.X(f'{self._colNameX}:N', sort='-y')

    def _createYAxis(self):
        if self._colNameY is None:
            return 'count:Q'
        return f'mean({self._colNameY}):Q'

    def _createTooltip(self):
        if self._colNameY is None:
            return [self._colNameX, 'count']
        return [f'mean({self._colNameY})']

    def create(self):
        chart = alt.Chart(self._df).mark_bar().encode(
            x=self._createXAxis(),
            y=self._createYAxis(),
            tooltip=self._createTooltip()
        ).properties(
            width=self.DEFAULT_WIDTH,
            height=self.DEFAULT_HEIGHT,
            padding=self.DEFAULT_PADDING
        )
        return chart
