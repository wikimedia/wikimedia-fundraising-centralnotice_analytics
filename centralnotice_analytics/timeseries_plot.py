import matplotlib
import matplotlib.pyplot as plt
import numpy as np

class TimeSeriesPlot:

    # TODO Does the timeseries column from Druid ever omit rows if there were no values?

    def __init__( self, pandas_df, left_scale_label,
        left_scale_columns, right_scale_label = None, right_scale_columns = None,
        title = None, figsize = ( 20, 8 ) ):

        plt.figure( figsize = figsize )
        matplotlib.rcParams.update( { 'font.size': 14 } )

        # Figure out how to space out ticks on the x axis
        # At this font size and dpi, we can fit about 1.5 ticks per inch
        max_x_ticks = int( figsize[0] * 1.5 )
        bucket_count = len( pandas_df )
        bucket_step = 1
        while ( bucket_count / bucket_step > max_x_ticks ):
            bucket_step += 1

        plt.xticks(
            np.arange( 0, bucket_count, bucket_step) ,
            pandas_df.timestamp.tolist()[::bucket_step],
            rotation = 'vertical'
        )

        plt.xlabel( 'Time' )
        plt.ylabel( left_scale_label )

        subplots = []
        legend_labels = []
        bucket_count_range = range( bucket_count )

        for column in left_scale_columns:
            subplots.append( plt.plot( bucket_count_range, pandas_df[ column ] ) )
            legend_labels.append( column )

        if ( ( right_scale_columns ) and ( right_scale_label ) ):
            ax2 = plt.twinx()
            ax2.set_ylabel( right_scale_label )

            for column in right_scale_columns:
                subplots.append( ax2.plot( bucket_count_range, pandas_df[ column ] ) )
                legend_labels.append( column )

        plt.legend( map( lambda p: p[0], subplots ), legend_labels )

        if ( title ):
            plt.title( title )


    def show( self ):
        plt.show()


    def pyplot_obj( self ):
        return plt