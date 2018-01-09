# Temporay hack to get around Jupyter proxy settings

from pydruid.client import *
import centralnotice_analytics as cna

py_druid_query = None
"""pydruid query object, set up as per config.yaml"""

class PyDruidIgnoreProxy(PyDruid):
    def _post(self, query):
        try:
            headers, querystr, url = self._prepare_url_headers_and_body(query)
            req = urllib.request.Request(url, querystr, headers)
            proxy_handler = urllib.request.ProxyHandler({})
            opener = urllib.request.build_opener(proxy_handler) 
            res = opener.open(req)
            data = res.read().decode("utf-8")
            res.close()
        except urllib.error.HTTPError:
            _, e, _ = sys.exc_info()
            err = None
            if e.code == 500:
                # has Druid returned an error?
                try:
                    err = json.loads(e.read().decode("utf-8"))
                except (ValueError, AttributeError, KeyError):
                    pass
                else:
                    err = err.get('error', None)

            raise IOError('{0} \n Druid Error: {1} \n Query is: {2}'.format(
                    e, err, json.dumps(query.query_dict, indent=4)))
        else:
            query.parse(data)
            return query

def get_py_druid_query():
    global py_druid_query

    if ( py_druid_query is not None ):
        return py_druid_query

    if ( cna.config[ 'druid' ][ 'bypass_proxy' ] ):
        py_druid_query = PyDruidIgnoreProxy(
            cna.config[ 'druid' ][ 'url' ],
            cna.config[ 'druid' ][ 'endpoint' ]
        )

    else:
        py_druid_query = PyDruid(
            cna.config[ 'druid' ][ 'url' ],
            cna.config[ 'druid' ][ 'endpoint' ]
        )

    return py_druid_query