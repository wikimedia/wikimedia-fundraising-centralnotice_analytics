from pydruid.utils.aggregators import doublesum
from pydruid.utils.filters import Filter

import centralnotice_analytics as cna
from centralnotice_analytics.query import Query
from centralnotice_analytics.druid_helper import DruidHelper
from centralnotice_analytics import TimeSeriesPlot

class PageviewsQuery( Query ):
    """A query of pageviews for a segment of users defined by CampaignSpec.

    Note: Query objects are not re-usable. To run a different query, create a new object.
    """

    def __init__( self,  campaign_spec, interval, granularity = 'hour',
            custom_filter = None, group_by_cols = None ):

        super().__init__( campaign_spec, interval, granularity, custom_filter,
            group_by_cols )

        self.columns_for_avg = [ 'pageviews' ]
        self.columns_for_totals = [ 'pageviews' ]

        self._proj_lang_url_strs = self._make_proj_lang_url_strs()

        self.warnings.append( 'Filtering for logged-in status currently unavailable.' )

        if ( self._campaign_spec.countries ):
            self.warnings.append( 'CN and server log geolocation can differ.' )

        if ( self._campaign_spec.devices ):
            self.warnings.append( 'Device filtering can be inaccurate, since device ' +
                'detection in CN and in server log processing may differ.' )

        self._druid_helper = DruidHelper(
            self.druid_timeseries_query_args(),
            group_by_cols
        )


    def _make_pandas_df( self ):
        return self._druid_helper.pandas_df()


    def prepare_plot( self, title = None, max_group_by_values = 5 ):

        if ( title is None ):
            title = self.make_title( 'Pageviews' )

        if ( self._group_by_cols ):
            flattened_df, group_columns = self.flatten_df_with_top_values(
                'pageviews', max_group_by_values )

            return TimeSeriesPlot(
                flattened_df,
                'Pageviews',
                group_columns,
                title = title
            )

        return TimeSeriesPlot(
            self.pandas_df(),
            'Pageviews',
            [ 'pageviews' ],
            title = title
        )


    def make_query_dump( self ):
        return self._druid_helper.json_for_query()


    def druid_filter( self ):
        # the following filters are always present
        filters = [
            self.proj_lang_druid_filter(),
            self.device_druid_filter(),
            self.agent_type_druid_filter()
        ]

        # campaign spec may not include geolocation
        if ( self._campaign_spec.countries ):
            filters.append( self.country_druid_filter() )

        if ( self._custom_filter ):
            filters.append( DruidHelper.build_filter( self._custom_filter ) )

        return Filter( type = 'and', fields = filters )


    def agent_type_druid_filter( self ):
        return Filter( dimension = 'agent_type', value = 'user' )


    def country_druid_filter( self ):
        return Filter(
            type = 'in',
            dimension = 'country_code',
            values = self._campaign_spec.countries
        )


    def proj_lang_druid_filter( self ):
        filters = []

        # Escape '.' in URL patterns used in Druid regex filters
        for url_str in map( lambda p: p.replace( '.', '\.' ), self._proj_lang_url_strs ):
            druid_filter = Filter(
                type = 'regex',
                dimension = 'project',
                pattern = url_str
            )
            filters.append( druid_filter )

        # Include pageviews from all the projects/languages requested, so join with 'or'
        return DruidHelper.or_or_single_filter( filters )


    def device_druid_filter( self ):

        # If no devices were specified, we still filter for access methods that run CN.
        if ( self._campaign_spec.devices is None ):
            return DruidHelper.build_filter( cna.config[ 'any_device_filter' ] )

        # Each outer filter represents a device selection.
        device_filters = []
        filter_configs = cna.config[ 'device_filters' ]

        for device in self._campaign_spec.devices:
            device_filters.append(
                DruidHelper.build_filter( filter_configs[ device ] ) )

        # Include pageviews from all devices selected, so join with 'or'
        return DruidHelper.or_or_single_filter( device_filters )


    def druid_timeseries_query_args( self ):
        return {
            'datasource': 'pageviews-hourly',
            'granularity': self._granularity,
            'intervals': self._interval,
            'aggregations': { 'pageviews': doublesum( 'view_count' ) },
            'filter': self.druid_filter()
        }


    def _make_proj_lang_url_strs( self ):

        # From a WMF cluster (not CN) standpoint, projects are wikis, so the project
        # column in pageview data contains language and (CN-ish) project in a single
        # string.
        url_strs = []

        # For projects that don't include a language code in the URL, we can't even
        # filter pageviews by language for not-logged-in users. We'll warn about those.
        cluster_projects_without_lang = []

        # Even if no projects were included in the spec, we need to filter projects, since
        # cn does not run on all WMF wikis. Also, language filtering varies by WMF wiki.
        projects = self._campaign_spec.projects or self._campaign_spec.default_projects()

        for project in projects:
            project_configs = cna.config[ 'project_lang_url_selection' ][ project ] 
            for project_config in project_configs:

                url_str = project_config[ 'url_str' ]

                # Create a language-less filter if no language filtering was requested,
                # or if this project's URL doesn't include a language code.
                if (
                    ( self._campaign_spec.languages is None ) or
                    ( not project_config[ 'lang_prefix' ] )
                ): 

                    url_strs.append( url_str )

                    if ( self._campaign_spec.languages ):
                        cluster_projects_without_lang.append( url_str )

                else:
                    # Otherwise, create a separate filter for each language requested
                    for lang in self._campaign_spec.languages:
                        url_strs.append( '{0}.{1}'.format( lang, url_str ) )

        if ( self._campaign_spec.languages ):
            self.warnings.append(
                'Language filtering may be incorrect for some logged-in users.' )

            if ( len( cluster_projects_without_lang ) > 0 ):
                self.warnings.append(
                    'Language filtering not available for wikis with URLs containing ' +
                    'the following strings: ' +
                    '|'.join( cluster_projects_without_lang ) +
                    '.'
                )

        return url_strs
