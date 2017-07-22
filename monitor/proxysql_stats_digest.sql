-- CREATE DATABASE dbquery; use dbquery;

CREATE TABLE `stats_mysql_query_digest_YourDbId` (
  `hostgroup` int(10) unsigned NOT NULL DEFAULT '0',
  `username` varchar(30) NOT NULL,
  `digest_text` varchar(2048) NOT NULL,
  `count_star` int(10) unsigned NOT NULL,
  `first_seen` int(10) unsigned NOT NULL,
  `last_seen` int(10) unsigned NOT NULL,
  `sum_time` int(10) unsigned NOT NULL,
  `min_time` int(10) unsigned NOT NULL,
  `max_time` int(10) unsigned NOT NULL,
  `schemaname` varchar(30) NOT NULL,
  `digest` varchar(30) NOT NULL,
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `count_star_delta` int(11) unsigned DEFAULT '0',
  `sum_time_delta` int(11) unsigned DEFAULT '0',
  `first_seen_real` int(11) unsigned DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq` (`digest`,`username`,`hostgroup`,`schemaname`) USING BTREE,
  KEY `idx_lastseen` (`last_seen`),
  KEY `idx_firstseen` (`first_seen`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `stats_mysql_query_digest_YourDbId_hist` (
  `digest` varchar(30) NOT NULL,
  `username` varchar(30) NOT NULL,
  `hostgroup` int(10) unsigned NOT NULL DEFAULT '0',
  `schemaname` varchar(30) NOT NULL,
  `count_star` int(10) unsigned NOT NULL,
  `sum_time` int(10) unsigned NOT NULL,
  `last_seen` int(10) unsigned NOT NULL,
  `first_seen` int(11) unsigned DEFAULT NULL,
  `digest_id` bigint(20) unsigned NOT NULL,
  `series_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`series_time`,`digest_id`)
) ENGINE=TokuDB DEFAULT CHARSET=utf8mb4 COMMENT='Delete old partition at your time, and remember to create new partition.\r\nuse event scheduler instead'
PARTITION BY RANGE (UNIX_TIMESTAMP(series_time))
(PARTITION p201707 VALUES LESS THAN (UNIX_TIMESTAMP('2017-08-01')) ENGINE = TokuDB,
 PARTITION p201708 VALUES LESS THAN (UNIX_TIMESTAMP('2017-09-01')) ENGINE = TokuDB,
 PARTITION p201709 VALUES LESS THAN (UNIX_TIMESTAMP('2017-10-01')) ENGINE = TokuDB,
 PARTITION p201710 VALUES LESS THAN (UNIX_TIMESTAMP('2017-11-01')) ENGINE = TokuDB,
 PARTITION p201711 VALUES LESS THAN (UNIX_TIMESTAMP('2017-12-01')) ENGINE = TokuDB,
 PARTITION p201712 VALUES LESS THAN (UNIX_TIMESTAMP('2018-01-01')) ENGINE = TokuDB,
 PARTITION p201801 VALUES LESS THAN (UNIX_TIMESTAMP('2018-02-01')) ENGINE = TokuDB,
 PARTITION p201802 VALUES LESS THAN (UNIX_TIMESTAMP('2018-03-01')) ENGINE = TokuDB,
 PARTITION p201803 VALUES LESS THAN (UNIX_TIMESTAMP('2018-04-01')) ENGINE = TokuDB,
 PARTITION p201804 VALUES LESS THAN (UNIX_TIMESTAMP('2018-05-01')) ENGINE = TokuDB,
 PARTITION p201805 VALUES LESS THAN (UNIX_TIMESTAMP('2018-06-01')) ENGINE = TokuDB,
 PARTITION p201806 VALUES LESS THAN (UNIX_TIMESTAMP('2018-07-01')) ENGINE = TokuDB,
 PARTITION p201807 VALUES LESS THAN (UNIX_TIMESTAMP('2018-08-01')) ENGINE = TokuDB,
 PARTITION p201808 VALUES LESS THAN (UNIX_TIMESTAMP('2018-09-01')) ENGINE = TokuDB,
 PARTITION p201809 VALUES LESS THAN (UNIX_TIMESTAMP('2018-10-01')) ENGINE = TokuDB,
 PARTITION p201810 VALUES LESS THAN (UNIX_TIMESTAMP('2018-11-01')) ENGINE = TokuDB,
 PARTITION p201811 VALUES LESS THAN (UNIX_TIMESTAMP('2018-12-01')) ENGINE = TokuDB,
 PARTITION p201812 VALUES LESS THAN (UNIX_TIMESTAMP('2019-01-01')) ENGINE = TokuDB);

