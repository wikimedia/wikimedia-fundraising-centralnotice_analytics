import pandas

from centralnotice_analytics.query import Query
from centralnotice_analytics import PageviewsQuery, ImpressionsQuery, TimeSeriesPlot

class RatesQuery( Query ):
    """A query of CentralNotice impression rates for user segment defined by a CampaignSpec.

    Note: Query objects are not re-usable. To run a different query, create a new object.
    """

    def __init__( self, campaign_spec, interval, granularity = 'hour',
            custom_filter = None, custom_pageviews_filter = None,
            custom_impressions_filter = None, group_by = None ):

        if ( custom_filter ):
            raise ValueError( 'Custom filter not available for rates query.' )

        if ( group_by ):
            raise ValueError( 'Grouping not yet implemented for rates query.')

        super().__init__( campaign_spec, interval, granularity )

        self._pageviews = PageviewsQuery(
            self._campaign_spec,
            self._interval,
            self._granularity,
            custom_pageviews_filter
        )

        self._impressions = ImpressionsQuery(
            self._campaign_spec,
            self._interval,
            self._granularity,
            custom_impressions_filter
        )

        self.columns_for_avg = [ 'pageviews', 'impressions', 'difference', 'rate' ]
        self.columns_for_totals = [ 'pageviews', 'impressions', 'difference' ]

        self.warnings += (
            list( map( lambda w: 'impressions: ' + w, self._impressions.warnings ) ) +
            list( map( lambda w: 'pageviews: ' + w, self._pageviews.warnings ) )
        )


    def _make_pandas_df( self ):
        pv_df = self._pageviews.pandas_df()
        imp_df = self._impressions.pandas_df()

        rates_df = pandas.merge(pv_df, imp_df, how = 'left', on = [ 'timestamp' ] )

        rates_df[ 'rate' ] = rates_df.apply(
            lambda row: row.impressions/row.pageviews,
            axis = 1
        )

        rates_df[ 'difference' ] = rates_df.apply(
            lambda row: row.pageviews - row.impressions,
            axis = 1
        )

        return rates_df


    def prepare_plot( self, title = None, max_group_by_values = 5 ):

        if ( title is None ):
            title = self.make_title( 'Impression rates' )

        return TimeSeriesPlot(
            self.pandas_df(),
            'Impressions and pageviews',
            [ 'impressions', 'pageviews', 'difference' ],
            right_scale_label = 'Impression rate',
            right_scale_columns = [ 'rate' ],
            title = title
        )


    def make_query_dump(self):
        return """
Pageviews:
    {0}

Impressions:
    {1}
""".format( self._pageviews.make_query_dump(), self._impressions.make_query_dump() )
