-- MySQL dump 10.13  Distrib 8.0.33, for Win64 (x86_64)
--
-- Host: localhost    Database: discussion
-- ------------------------------------------------------
-- Server version	8.0.33

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `utilisateurs`
--

DROP TABLE IF EXISTS `utilisateurs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `utilisateurs` (
  `ID_Utilisateur` int NOT NULL AUTO_INCREMENT,
  `Nom_Utilisateur` varchar(25) DEFAULT NULL,
  `Mot_de_Passe` varchar(50) DEFAULT NULL,
  `Alias` varchar(50) DEFAULT NULL,
  `Statut` varchar(50) DEFAULT NULL,
  `Banni` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`ID_Utilisateur`),
  UNIQUE KEY `Alias` (`Alias`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `utilisateurs`
--

LOCK TABLES `utilisateurs` WRITE;
/*!40000 ALTER TABLE `utilisateurs` DISABLE KEYS */;
INSERT INTO `utilisateurs` VALUES (1,'kiki','azerty',NULL,NULL,0),(2,'Jnej','azerty',NULL,NULL,0),(3,'Nathan','jaj',NULL,NULL,0),(4,'CREATE_ACCOUNT','CREATE_ACCOUNT',NULL,NULL,0),(5,'test','azerty',NULL,NULL,1),(6,'test1','azerty',NULL,NULL,1),(7,'AUTHENTICATE|test2|azerty','f',NULL,NULL,0),(8,'zda','azd',NULL,NULL,0),(9,'test6','azerty',NULL,NULL,0),(10,'zafaz','azfza',NULL,NULL,0),(11,'CREATE_ACCOUNT_TRIGGER','zdaz',NULL,NULL,0),(12,'afazf','zafazf',NULL,NULL,0),(13,'test10','azerty',NULL,NULL,1),(14,'test9','azerty',NULL,NULL,1),(15,'test8','azerty',NULL,NULL,0),(16,'azdazd','zadazd',NULL,NULL,0),(17,'ezae','aezaze',NULL,NULL,0),(18,'dhregdfg','gfdgfdg',NULL,NULL,0),(19,'fezh','fds',NULL,NULL,0),(20,'test67832','azerty',NULL,NULL,0);
/*!40000 ALTER TABLE `utilisateurs` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-12-31 16:34:15
