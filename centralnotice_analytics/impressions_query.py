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

        self._druid_helper = DruidHelper(
            self.druid_timeseries_query_args(),
            group_by_cols
        )


    def _make_pandas_df( self ):
        return self._druid_helper.pandas_df()


    def prepare_plot( self, title = None  ):

        if ( title is None ):
            title = 'Impressions, ' + self._make_title()

        return TimeSeriesPlot(
            self.pandas_df(),
            'Impressions',
            [ 'impressions' ],
            title = title
        )


    def make_query_dump(self):
        return self._druid_helper.json_for_query()


    def druid_filter( self ):
        # the following filters are always present
        filters = [
            self.campaign_druid_filter(),
            self.project_druid_filter(),
            self.language_druid_filter()
        ]

        # campaign spec may not include geolocation or device
        if ( self._campaign_spec.devices ):
            filters.append( self.device_druid_filter() )

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

        # if no campaign names were provided in the spec, name_regex be there
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
