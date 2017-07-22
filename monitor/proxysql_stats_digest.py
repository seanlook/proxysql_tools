#!/usr/local/bin/python2.7
"""
This script dump proxysql digest from `stats_mysql_query_digest` periodically but not too often.
In order to show the trends, difference is caculated to save to mysql table. Also print influxdb format.

`ProxySQL_Info` and `MySQL_Digest` should be given!
"""
import MySQLdb
import time
import sys
from socket import gethostname

if len(sys.argv) != 3:
    print "Please give arguments like base 6032"
    sys.exit(1)

try:
    if int(sys.argv[2]):
        pass
except:
   print "Please give the right db port" 
   sys.exit(1)
dbinstance = sys.argv[1]
dbport = int(sys.argv[2])

# source
ProxySQL_Info = {
    'host': 'your_proxysql_ip',
    'port': 6032,
    'user': 'stats_user',
    'passwd': 'stats_pass'
}

# dump to
MySQL_Digest = {
    'host': 'where_digest_is_dumped_to',
    'port': 3306,
    'user': 'your_user',
    'passwd': 'your_pass',
    'db': 'dbquery'
}


tablename_prefix = 'stats_mysql_query_digest'
tablename_stats_digest = tablename_prefix + '_' + dbinstance
tablename_stats_digest_hist = tablename_stats_digest + '_hist'
mins_11ago = str(int(time.time()) - 11 * 60)  # 10 minutes ago

"""
run script every 10 minutes
only collect queries that last seen in last 10 minutes, and limit 1000
"""
def get_query_digests():
    dbconn = MySQLdb.connect(**ProxySQL_Info)
    dbconn.autocommit(1)
    sql_digests = """
        select hostgroup,username,digest_text,count_star,first_seen,last_seen,sum_time/1000,min_time,max_time,schemaname,digest
        from stats_mysql_query_digest
        where last_seen > {0}
        order by count_star desc limit 1000
    """.format(mins_11ago)

    cur = dbconn.cursor()
    cur.execute(sql_digests)
    data_digests = cur.fetchall()
    cur.close()
    dbconn.close()

    return data_digests


def get_connection():
    dbconn = MySQLdb.connect(**MySQL_Digest)
    dbconn.autocommit(1)

    return dbconn


def save_query_digests_hist(data_digests):
    dbconn = get_connection()
    # delta must locate before
    sql_digests = "insert into " + tablename_stats_digest + \
                  "    (hostgroup,username,digest_text,count_star,first_seen,last_seen,sum_time,min_time,max_time,schemaname,digest, count_star_delta,sum_time_delta,first_seen_real) " \
                  "values(%s, %s, %s, %s ,%s, %s, %s, %s, %s, %s, %s,  %s,%s,%s) " \
                  "on duplicate key update " \
                  "count_star_delta = IF(VALUES(count_star)<=count_star, 0,VALUES(count_star)-count_star), sum_time_delta = IF(VALUES(sum_time)<=sum_time, 0, VALUES(sum_time)-sum_time),  " \
                  "count_star=%s, first_seen=%s, last_seen=%s, sum_time=%s, min_time=%s, max_time=%s"
    digest_params = [list(row) + [row[3],row[6],row[4]] + [row[3], row[4], row[5], row[6], row[7], row[8] ] for row in data_digests]

    cur = dbconn.cursor()
    cur.executemany(sql_digests, digest_params)

    sql_copyto_hist = "insert into " + tablename_stats_digest_hist + \
                      "    (digest, username, hostgroup, schemaname, count_star, sum_time, last_seen, first_seen,digest_id) " \
                      " select digest, username, hostgroup, schemaname, count_star_delta, sum_time_delta, last_seen, first_seen_real, id " \
                      " from " + tablename_stats_digest  #  + " where last_seen > " + mins_11ago
    cur.execute(sql_copyto_hist)

    dbconn.close()


def print_metrics_digest_influx(proxy_host):
    measurement = "proxysql_digest"
    # max 500, only 20 minutes ago
    sql_writeto_influx = """
        select username, digest, count_star_delta, sum_time_delta
        from {0}
        where last_seen > {1}
        order by count_star_delta desc limit 500
    """.format(tablename_stats_digest, mins_11ago)

    dbconn = get_connection()
    cur = dbconn.cursor()
    cur.execute(sql_writeto_influx)
    list_metrics = cur.fetchall()
    cur.close()
    dbconn.close()

    ret_metric = []
    for row in list_metrics:
        tag_fields = "{0},host={1},instance={2},username={3},digest={4}".format(
            measurement,
            proxy_host,
            dbinstance,
            row[0],
            row[1]
        )
        value_fields = "count_star={0},sum_time={1}".format(
            row[2],
            row[3]
        )
        ret_metric.append(tag_fields + " " + value_fields)

    print "\n".join(ret_metric)


if __name__ == '__main__':

    HOSTNAME = gethostname()
    if HOSTNAME == 'ecbak':  # only collect data from proxysql-1
        data = get_query_digests()
        save_query_digests_hist(data)
        print_metrics_digest_influx(HOSTNAME)
