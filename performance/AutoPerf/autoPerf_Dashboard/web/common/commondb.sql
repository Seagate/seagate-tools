CREATE DATABASE
IF NOT EXISTS `commondb` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `commondb`;
-- MySQL dump 10.13  Distrib 5.7.29, for Linux (x86_64)
--
-- Host: localhost    Database: commondb
-- ------------------------------------------------------
-- Server version	5.7.29-0ubuntu0.18.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `common_user`
--

DROP TABLE IF EXISTS `common_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `common_user`
(
  `id` int
(10) unsigned NOT NULL AUTO_INCREMENT,
  `gid` varchar
(200) CHARACTER
SET utf8 DEFAULT
NULL,
  `email` varchar
(255) COLLATE utf8_unicode_ci NOT NULL,
  `component` varchar
(15) COLLATE utf8_unicode_ci NOT NULL,
  `password` varchar
(255) COLLATE utf8_unicode_ci NOT NULL,
  `isActive` int
(2) DEFAULT '1',
  `profileURL` varchar
(45) COLLATE utf8_unicode_ci DEFAULT NULL,
  `isEmailVerified` int
(2) unsigned DEFAULT '0',
  `isDeleted` int
(2) DEFAULT '0',
  `createdAt` datetime DEFAULT CURRENT_TIMESTAMP,
  `modifiedAt` datetime DEFAULT CURRENT_TIMESTAMP ON
UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY
(`id`),
  UNIQUE KEY `id_UNIQUE`
(`id`),
  UNIQUE KEY `emailAddress_UNIQUE`
(`email`),
  UNIQUE KEY `mobileNumber_UNIQUE`
(`component`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping routines for database 'commondb'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-04-13 17:14:22
