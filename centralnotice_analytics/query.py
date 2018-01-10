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

        self.columns_for_avg = None
        """Columns to include in averages of results. Should be set by subclass."""

        self.columns_for_totals = None
        """Columns to include in totals of results. Should be set by subclass."""


    def print_warnings( self ):
        print ( '\n'.join( self.warnings ) )


    def pandas_df( self ):
        if ( self._pandas_df is None ):
            self._pandas_df = self._make_pandas_df()

        return self._pandas_df


    def totals( self ):
        return self.pandas_df()[ self.columns_for_totals ].sum()


    def averages( self ):
        return self.pandas_df()[ self.columns_for_avg ].mean()


    def flatten_df_with_top_values( self, aggregate_col, max_values ):
        df = self.pandas_df()

        # Get the top max_values groups for aggregte_col values
        top_values = (
            df
            .groupby( self._group_by_cols )[ [ aggregate_col ] ]
            .sum()
            .sort_values( by = [ aggregate_col ], ascending = False )
            .head( max_values )
            .reset_index()
        )

        # TODO Maybe find a faster way to do this?
        # Create a list two-column dataframes, one for each top value
        group_dfs = []
        for i in range( 0, len( top_values ) ):
            group_df = df.copy()
            group_label_parts = []

            for col in self._group_by_cols:
                val = top_values[ col ][ i ]
                group_df = group_df[ group_df[ col ] == val ]
                group_label_parts.append( val )

            # remove unwanted columns
            for col in group_df.columns.tolist():
                if ( ( col == aggregate_col ) or ( col == 'timestamp' ) ):
                    continue

                group_df.drop( col, axis=1, inplace = True )

            # rename the aggregate to identify the value(s) it represents
            group_df.rename(
                columns = { aggregate_col: ', '.join( group_label_parts ) },
                inplace = True
            )

            group_df.set_index( 'timestamp', inplace = True )
            group_dfs.append( group_df )

        # Join using an index of all timestamps in the original dataframe
        timestamps = df[['timestamp']].drop_duplicates().copy().set_index( 'timestamp' )

        flattened_df = (
            timestamps
            .join( group_dfs )
            .reset_index()
            .rename( columns = { 'index': 'timestamp' } )
            .fillna( 0 )
        )

        group_columns = flattened_df.columns.tolist()
        group_columns.remove( 'timestamp' )

        return ( flattened_df, group_columns )


    def plot( self, title = None, max_group_by_values = 5 ):
        plot = self.prepare_plot( title, max_group_by_values )
        plot.show()


    def dump_query( self ):
        print ( self.make_query_dump() )


    def make_title( self, prefix ):
        if ( self._group_by_cols ):
            prefix += ' grouped by ' + '/'.join( self._group_by_cols )

        return '{0}, {1} by {2}, {3}'.format(
            prefix,
            self._interval,
            self._granularity,
            self._campaign_spec.title()
        )


    @abstractmethod
    def prepare_plot( self, title = None, max_group_by_values = 5 ): pass


    @abstractmethod
    def make_query_dump( self ): pass


    @abstractmethod
    def _make_pandas_df( self ): pass