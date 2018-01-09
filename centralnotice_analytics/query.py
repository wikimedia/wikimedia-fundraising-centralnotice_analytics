from abc import ABCMeta, abstractmethod

class Query:
    """Abstract superclass for queries of CentralNotice-related data."""
    __metaclass__ = ABCMeta


    def __init__( self, campaign_spec, interval, granularity = 'hour',
            custom_filter = None, group_by_cols = None ):
        """
        :param centralnotice_analytics.campaign_spec.CampaignSpec campaign_spec:
            CentralNotice campaign specification for query.
        :param str interval: ISO-8601 interval on which to run the query.
        :param str granularity: Time bucket to aggregate data (can be 'day' or 'hour').
        :paran dict custom_filter: Specification for a custom filter to add to query.
            Follows the same pattern as constructors for pydruid.utils.filters.Filter.
            See config_example.yaml for examples.
        :param list group_by_cols: A list of names of columns for grouping.

        Subclasses should add any warnings to self.warnings on instantiation.
        """

        self._campaign_spec = campaign_spec
        self._interval = interval
        self._granularity = granularity
        self._custom_filter = custom_filter
        self._group_by_cols = group_by_cols

        self._pandas_df = None
        """Pandas dataframe"""

        self.warnings = []
        """A list of strings with warnings about the query."""


    def print_warnings( self ):
        print ( '\n'.join( self.warnings ) )


    def pandas_df( self ):
        if ( self._pandas_df is None ):
            self._pandas_df = self._make_pandas_df()

        return self._pandas_df


    def plot( self, title = None ):
        plot = self.prepare_plot( title )
        plot.show()


    def dump_query( self ):
        print ( self.make_query_dump() )


    def _make_title( self ):
        return '{0} by {1}, {2}'.format(
            self._interval,
            self._granularity,
            self._campaign_spec.title()
        )


    @abstractmethod
    def prepare_plot( self, title = None ): pass


    @abstractmethod
    def make_query_dump( self ): pass


    @abstractmethod
    def _make_pandas_df( self ): pass