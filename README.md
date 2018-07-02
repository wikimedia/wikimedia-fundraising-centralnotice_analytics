CentralNotice Analytics
=======================

This library provides a high-level API for querying and plotting statistics about
CentralNotice using the Wikimedia Foundation's analytics data stores. It lets you
define queries in terms of CentralNotice's targeting criteria, so you don't have
to worry about the details of how to translate those criteria into specific
queries of data stores.

Usage
-----
```python

	import centralnotice_analytics as cna
	
	# Create a CampaignSpec to specify the campaign(s) and CentralNotice
	# targeting criteria to use for queries. You can specify one or more
	# campaign names, or a regular expression to select all matching campaigns.
	# Project, languages, countries and devices use the same terms as those used
	# by CN for campaign configuration.
	
	c = cna.CampaignSpec(
	    name_regex='C1718_en6C',
	    projects=[ 'wikipedia' ],
	    languages = [ 'en' ],
	    countries = [ 'CA', 'US' ],
	    devices = [ 'iphone', 'ipad', 'android' ]
	)
	
	# Use the specification to create queries. Three query classes are
	# available: PageviewsQuery, ImpressionsQuery and RatesQuery.
	# (Intervals are specified in ISO 8601 format.)
	r = cna.RatesQuery( c, '2017-12-30T00:00Z/P3D', 'hour')
	
	# Get a pandas dataframe with the results
	r.pandas_df()
	
	# Plot the results
	r.plot()
	
	# Aggregate the results (sums or averages per time bucket)
	r.averages()
	
	# Print warnings about the query (caveats about the limitations of the
	# results).
	r.print_warnings()
	
	# Review the actual query or queries sent to the data stores.
	r.dump_query()
	
	# For PageviewsQuery and ImpressionsQuery, grouping is supported
	pv = cna.PageviewsQuery( c, '2017-12-30T00:00Z/P3D', 'hour',
	    group_by_cols = [ 'ua_browser_family', 'ua_browser_major'] )
	pv.plot()
	
	# PageviewsQuery and ImpressionsQuery also support custom filters.
	imp = cna.ImpressionsQuery( c, '2017-12-30T00:00Z/P3D', 'hour',
		custom_filter = { 'dimension': 'status_code', 'value': '2.1' } )
	imp.plot()
```

Installation and setup
----------------------

Access to WMF data stores is required. For Jupyter notebook setup, see
[SWAP instructions](https://wikitech.wikimedia.org/wiki/SWAP#Usage) on Wikitech.

Copy `config_example.yaml` as `config.yaml`, and set the Druid URL there.

For development, copy the repository to the notebook server. The following rsync
command may be useful:

`rsync -vr --delete -e ssh --exclude ".*project" --exclude "*__pycache__*" /local/path/to/centralnotice_analytics/ jupyter.notebook.server:~/path/on/server/centralnotice_analytics`

Then in the Jupyter notebook, try:

`!pip install -e /home/your_dir/path/on/server/centralnotice_analytics[plots]`

This should make the package accessible to python using a link, so that you can continue
to update the source code. Restart the Jupyter kernel after any changes.

It should also install all dependencies, including optional ones needed for plot functionality.

Limitations and future features
-------------------------------

For now, queries are only sent to Druid. This makes filtering pageviews for logged-in
status impossible. It might be possible to remedy this with changes to Druid stores.

Hive queries could be implemented. At least, a mechanism to output the text of an
 equivalent HiveQL query should be added. This would facilitate use of the library
 for more detailed and varied queries.