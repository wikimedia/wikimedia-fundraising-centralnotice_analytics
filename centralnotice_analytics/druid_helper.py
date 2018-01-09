import json

from pydruid.utils.filters import Filter
from pydruid.client import QueryBuilder

import centralnotice_analytics.util.py_druid_util as py_d_util


class DruidHelper:

    def __init__( self, timeseries_args, group_by_cols = None ):
        self._query_args = timeseries_args

        if ( group_by_cols ):
            self._query_args[ 'dimensions' ] = group_by_cols
            self._group_by = True
        else:
            self._group_by = False


    def pandas_df( self ):
        # Get a configured client query object
        query = py_d_util.get_py_druid_query()

        if ( self._group_by ):
            query.groupby( **self._query_args )
        else:
            query.timeseries( **self._query_args )

        return query.export_pandas()


    def json_for_query( self ):
        # This query object constructs the query but does not actually send it, unlike the
        # client query object used above.
        if ( self._group_by ):
            query = QueryBuilder().groupby( self._query_args )
        else:
            query = QueryBuilder().timeseries( self._query_args )

        return json.dumps( query.query_dict, indent = 4 )


    @staticmethod
    def and_or_single_filter( filters ):
        if len( filters ) == 1:
            return filters[0]
        else:
            return Filter( type = 'and', fields = filters )


    @staticmethod
    def or_or_single_filter( filters ):
        if len( filters ) == 1:
            return filters[0]
        else:
            return Filter( type = 'or', fields = filters )


    @staticmethod
    def build_filter( config ):
        filter_params = config.copy()

        for name, val in filter_params.items():
            if ( isinstance( val, dict ) ):
                filter_params[ name ] = DruidHelper.build_filter( val )

            elif ( isinstance( val, list ) ):
                filter_params[ name ] = []
                for inner_config in val:
                    filter_params[ name ].append(
                        DruidHelper.build_filter( inner_config ) )

        return Filter( **filter_params )

