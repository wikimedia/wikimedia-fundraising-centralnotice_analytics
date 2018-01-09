import yaml, os
import pandas

from .campaign_spec import CampaignSpec
from .timeseries_plot import TimeSeriesPlot
from .pageviews_query import PageviewsQuery
from .impressions_query import ImpressionsQuery
from .rates_query import RatesQuery

path = os.path.dirname( __file__ )
config_filename = os.path.join( path, '../config.yaml' )
with open( config_filename, 'r' ) as stream:
    config = yaml.load( stream )

# Friendlier number displays for aggregates
pandas.set_option( 'display.float_format', lambda x: '{:,.4f}'.format( x) )