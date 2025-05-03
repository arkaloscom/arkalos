from typing import Literal
import polars as pl
import altair as alt
from vega_datasets import data # type: ignore



class Example:

    def getDataset(self, 
        name: Literal['cars']|Literal['stocks']|Literal['pie']|Literal['bar']
    ) -> pl.DataFrame:

        if name == 'cars':
            cars = data.cars()
            return pl.from_pandas(cars)
        elif name == 'stocks':
            stocks = data.stocks()
            return pl.from_pandas(stocks)
        elif name == 'pie':
            return pl.DataFrame({
                "category": ["Category A", "Category B", "Category C", "Category D", "Category E"],
                "value": [25, 40, 12, 18, 5]
            })
        elif name == 'bar':
            return pl.DataFrame({
                "month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                "sales": [120, 150, 130, 190, 220, 170]
            })
        raise Exception(f'Dataset with name "{name} not found.')

    def barChart(self) -> alt.Chart:
        df = self.getDataset('bar')
        return alt.Chart(df).mark_bar().encode(
            x='month',
            y='sales',
            color='month',
            tooltip=['month', 'sales']
        ).properties(
            width=400,
            height=300,
            # title='Monthly Sales'
        ).interactive()

    def lineChart(self) -> alt.Chart:
        df = self.getDataset('stocks')
        df = df.filter(pl.col("symbol").is_in(["AAPL", "GOOG", "MSFT"]))
        return alt.Chart(df).mark_line(strokeWidth=3).encode(
            x='date',
            y='price',
            color='symbol',
            tooltip=['date', 'price', 'symbol']
        ).properties(
            width=500,
            height=300,
            # title='Stock Prices'
        ).interactive()

    def pieChart(self) -> alt.Chart:
        df = self.getDataset('pie')
        return alt.Chart(df).mark_arc().encode(
            theta=alt.Theta(field="value", type="quantitative"),
            color=alt.Color(field="category", type="nominal"),
            tooltip=['category', 'value']
        ).properties(
            width=400,
            height=400,
            # title='Distribution by Category'
        ).interactive()

    def scatterPlot(self) -> alt.Chart:
        df = self.getDataset('cars')
        return alt.Chart(df).mark_circle().encode(
            x='Horsepower',
            y='Miles_per_Gallon',
            color='Origin',
            size='Weight_in_lbs',
            tooltip=['Name', 'Horsepower', 'Miles_per_Gallon', 'Origin']
        ).properties(
            width=500,
            height=400,
            # title='Car Performance'
        ).interactive()

    def areaChart(self) -> alt.Chart:
        df = self.getDataset('stocks')
        df = df.filter(pl.col("symbol") == "AAPL")
        return alt.Chart(df).mark_area(
            opacity=0.7,
            interpolate='monotone'
        ).encode(
            x='date',
            y='price',
            tooltip=['date', 'price']
        ).properties(
            width=500,
            height=300,
            # title='AAPL Stock Price Trend'
        ).interactive()

    def chartSpec(self, 
        name=Literal['bar']|Literal['pie']|Literal['line']|Literal['scatter']|Literal['area']
    ) -> dict:
        if name == 'bar':
            return self.barChart().to_dict()
        elif name == 'pie':
            return self.pieChart().to_dict()
        elif name == 'line':
            return self.lineChart().to_dict()
        elif name == 'scatter':
            return self.scatterPlot().to_dict()
        elif name == 'area':
            return self.areaChart().to_dict()
        raise Exception(f'Chart with name "{name} not found.')
