#!/usr/local/bin/python2.7
"""
This script monitor proxysql stats: Connections, Memory, Queries etc.
Set your own proxysql ip address and user/pass bellow (`ProxySQL_Admin`, `ProxySQL_Auth`)
Print out influxdb metric format
"""
from socket import gethostname
try:
    import MySQLdb
    from MySQLdb import MySQLError
except ImportError:
    MySQLdb = None
    MySQLError = ValueError

ProxySQL_Admin = {
    'db0': ('127.0.0.1', 6032),
    'db1': ('127.0.0.1', 7032),
    'db2': ('127.0.0.1', 7132),
    'db3': ('127.0.0.1', 7232),
}

ProxySQL_Auth = ('stats_user', 'stats_pass')


HOSTNAME = gethostname()

STATUS_CODE = {
    'ONLINE': 0,  # nagios think 0 as ok
    'SHUNNED': 1,
    'OFFLINE_SOFT': 2,
    'OFFLINE_HARD': 3,
}

METRIC_KEYS = [
    'Active_Transactions',
    'Client_Connections_connected',
    'Server_Connections_connected',
    'Server_Connections_aborted',

    'MySQL_Monitor_Workers',
    'MySQL_Thread_Workers',

    'Query_Cache_Entries',
    'Query_Cache_Memory_bytes',
    'SQLite3_memory_bytes',
    'ConnPool_memory_bytes',

    'mysql_backend_buffers_bytes',
    'mysql_frontend_buffers_bytes',
    'mysql_session_internal_bytes',
    'Questions',
]

STATS_SQL = """SELECT * FROM stats_mysql_global WHERE Variable_Name IN
('{0}')
""".format("','".join(METRIC_KEYS))

STATS_SERVER_SQL = """SELECT hostgroup,srv_host,srv_port, status,Queries,ConnUsed,Latency_us 
                      FROM stats_mysql_connection_pool"""


def get_connection(db_host, db_port):
    conn = MySQLdb.Connect(
        host=db_host,
        port=db_port,
        user=ProxySQL_Auth[0],
        passwd=ProxySQL_Auth[1],
        connect_timeout=2
    )
    return conn

def get_db_stats(proxy_instance):
    db_host, db_port = ProxySQL_Admin[proxy_instance]
    conn = get_connection(db_host, db_port)

    cur = conn.cursor()
    cur.execute(STATS_SQL)
    ret_proxy = cur.fetchall()
    cur.close()

    cur = conn.cursor()
    cur.execute(STATS_SERVER_SQL)
    ret_hosts = cur.fetchall()
    cur.close

    conn.close()

    print_metrics_proxy_influx(proxy_instance, ret_proxy)
    print_metrics_hosts_influx(proxy_instance, ret_hosts)


def print_metrics_proxy_influx(dbinstance, list_cols):
    measurement = "proxysql"
    ret_metric = []
    tag_fields = "{0},host={1},instance={2}".format(
        measurement,
        HOSTNAME,
        dbinstance,
    )

    for row in list_cols:
        ret_metric.append("{0}={1}".format(
            row[0],
            row[1]
        ))

    value_fields = ",".join(ret_metric)

    print tag_fields + " " + value_fields

def print_metrics_hosts_influx(dbinstance, list_cols):
    measurement = "proxysql_hosts"
    ret_metric = []
    for row in list_cols:
        tag_fields = "{0},host={1},instance={2},srv_hostgroup={3},srv_port={4}".format(
            measurement,
            HOSTNAME,
            dbinstance,
            row[0] + ':' + row[1],
            row[2],
        )
        value_fields = "status={0},Queries={1},ConnUsed={2},Latency_us={3}".format(
            STATUS_CODE[row[3]], #row[3],  # status
            row[4],  # Queries
            row[5],  # ConnUsed
            row[6],  # Latency_us
        )
        
        ret_metric.append(tag_fields + " " + value_fields)

    print "\n".join(ret_metric)


if __name__ == '__main__':
    for proxy_instance in ProxySQL_Admin:
        get_db_stats(proxy_instance)
