from pydruid.utils.aggregators import longsum
from pydruid.utils.filters import Filter

from centralnotice_analytics.query import Query
from centralnotice_analytics.druid_helper import DruidHelper
from centralnotice_analytics import TimeSeriesPlot

class ImpressionsQuery( Query ):
    """A query of CentralNotice impressions for a segment of users defined by CampaignSpec.

    Note: Query objects are not re-usable. To run a different query, create a new object.
    """

    def __init__( self, campaign_spec, interval, granularity = 'hour',
            custom_filter = None, group_by_cols = None  ):

        super().__init__( campaign_spec, interval, granularity, custom_filter,
            group_by_cols )

        self.columns_for_avg = [ 'impressions' ]
        self.columns_for_totals = [ 'impressions' ]

        self._druid_helper = DruidHelper(
            self.druid_timeseries_query_args(),
            group_by_cols
        )


    def _make_pandas_df( self ):
        return self._druid_helper.pandas_df()


    def prepare_plot( self, title = None, max_group_by_values = 5 ):

        if ( title is None ):
            title = self.make_title( 'Impressions' )

        if ( self._group_by_cols ):
            flattened_df, group_columns = self.flatten_df_with_top_values(
                'impressions', max_group_by_values )

            return TimeSeriesPlot(
                flattened_df,
                'Impressions',
                group_columns,
                title = title
            )

        return TimeSeriesPlot(
            self.pandas_df(),
            'Impressions',
            [ 'impressions' ],
            title = title
        )


    def make_query_dump(self):
        return self._druid_helper.json_for_query()


    def druid_filter( self ):
        filters = []

        # campaign spec may or may not include several criteria
        if ( self._campaign_spec.names or self._campaign_spec.name_regex ):
            filters.append( self.campaign_druid_filter() )

        if ( self._campaign_spec.projects ):
            filters.append( self.project_druid_filter() )

        if ( self._campaign_spec.devices ):
            filters.append( self.device_druid_filter() )

        if ( self._campaign_spec.languages ):
            filters.append( self.self.language_druid_filter() )

        if ( self._campaign_spec.countries ):
            filters.append( self.country_druid_filter() )

        if ( self._custom_filter ):
            filters.append( DruidHelper.build_filter( self._custom_filter ) )

        return Filter( type = 'and', fields = filters )


    def campaign_druid_filter( self ):
        if ( self._campaign_spec.names ):
            return Filter(
                type = 'in',
                dimension = 'campaign',
                values = self._campaign_spec.names
            )

        if ( self._campaign_spec.name_regex ):
            return Filter(
                type = 'regex',
                dimension = 'campaign',
                pattern = self._campaign_spec.name_regex
            )


    def country_druid_filter( self ):
        return Filter(
            type = 'in',
            dimension = 'country',
            values = self._campaign_spec.countries
        )


    def project_druid_filter( self ):
        return Filter(
            type = 'in',
            dimension = 'project',
            values = self._campaign_spec.projects
        )


    def language_druid_filter( self ):
        return Filter(
            type = 'in',
            dimension = 'uselang',
            values = self._campaign_spec.languages
        )


    def device_druid_filter( self ):
        return Filter(
            type = 'in',
            dimension = 'device',
            values = self._campaign_spec.devices
        )


    def druid_timeseries_query_args( self ):
        return {
            'datasource': 'banner_activity_minutely',
            'granularity': self._granularity,
            'intervals': self._interval,
            'aggregations':  { 'impressions': longsum( 'normalized_request_count' ) },
            'filter': self.druid_filter()
        }
