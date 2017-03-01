
DROP TABLE IF EXISTS `assigned_ip`;

CREATE TABLE `assigned_ip` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `mac` varchar(17) DEFAULT NULL,
  `percent` varchar(3) DEFAULT NULL,
  `msg` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `mac` (`mac`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `participants`;

CREATE TABLE `participants` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `hour` int(11) DEFAULT NULL,
  `minute` int(11) DEFAULT NULL,
  `radial` varchar(11) DEFAULT NULL,
  `quad` varchar(17) DEFAULT NULL,
  `mac` varchar(17) DEFAULT NULL,
  `camp` varchar(1024) DEFAULT NULL,
  `contact` varchar(1024) DEFAULT NULL,
  `email` varchar(1024) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `mac` (`mac`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `status`;

CREATE TABLE `status` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `p_id` int(11) DEFAULT NULL,
  `state` varchar(24) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `vlans`;

# participant wifi vlans are between 1001 and 1999, so auto_inc starts at 1001
CREATE TABLE `vlans` (
  `vlan_id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `assigned_to` int(11) DEFAULT NULL,
  PRIMARY KEY (`vlan_id`),
  UNIQUE KEY `assigned_to` (`assigned_to`)
) ENGINE=InnoDB AUTO_INCREMENT=1001 DEFAULT CHARSET=utf8;

