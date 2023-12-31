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
-- Table structure for table `messages`
--

DROP TABLE IF EXISTS `messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `messages` (
  `ID_Message` int NOT NULL AUTO_INCREMENT,
  `ID_Utilisateur` int DEFAULT NULL,
  `ID_Salon` int DEFAULT NULL,
  `Contenu_Message` text,
  `Date_Heure_Envoi` datetime DEFAULT NULL,
  PRIMARY KEY (`ID_Message`),
  KEY `ID_Utilisateur` (`ID_Utilisateur`),
  KEY `ID_Salon` (`ID_Salon`),
  CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`ID_Utilisateur`) REFERENCES `utilisateurs` (`ID_Utilisateur`),
  CONSTRAINT `messages_ibfk_2` FOREIGN KEY (`ID_Salon`) REFERENCES `salons` (`ID_Salon`)
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `messages`
--

LOCK TABLES `messages` WRITE;
/*!40000 ALTER TABLE `messages` DISABLE KEYS */;
INSERT INTO `messages` VALUES (1,1,1,'gre','2023-12-31 12:46:27'),(2,1,1,'efrdzqs<ghb','2023-12-31 12:46:29'),(3,1,1,'ghedzqsgv','2023-12-31 12:46:30'),(4,1,1,'jyydgyj','2023-12-31 12:46:54'),(5,1,1,'rgrfg','2023-12-31 12:47:05'),(6,1,1,'QUIT','2023-12-31 12:47:50'),(7,1,1,'QUIT','2023-12-31 12:50:05'),(8,1,1,'CHANGE_ROOM|Général','2023-12-31 13:25:31'),(9,1,1,'dazdad','2023-12-31 13:25:36'),(10,1,1,'nkibvfnikbginkkijgbjfdnkbknfqnblkklnqbbknlnbklkslndfknlbknldsfqbknfdknbkndqfbklfsdqhbqfhbvjlqsbnvjqsfbvj','2023-12-31 13:25:43'),(11,1,1,'QUIT','2023-12-31 13:28:43'),(12,1,1,'jnej','2023-12-31 13:35:21'),(13,1,1,'QUIT','2023-12-31 13:35:29'),(14,1,1,'QUIT','2023-12-31 13:59:06'),(15,1,1,'QUIT','2023-12-31 13:59:25'),(16,1,1,'dzad','2023-12-31 14:01:51'),(17,1,1,'AUTHENTICATE|kiki|azerty','2023-12-31 14:06:26'),(18,1,1,'QUIT','2023-12-31 14:06:30'),(19,1,1,'QUIT','2023-12-31 14:07:24'),(20,1,1,'QUIT','2023-12-31 14:10:47'),(21,1,1,'QUIT','2023-12-31 14:28:16'),(22,1,1,'QUIT','2023-12-31 14:28:33'),(23,1,1,'QUIT','2023-12-31 14:31:10'),(24,1,1,'hvkj','2023-12-31 14:35:12'),(25,1,1,'QUIT','2023-12-31 14:35:16'),(26,1,1,'QUIT','2023-12-31 14:36:01'),(27,1,1,'QUIT','2023-12-31 14:36:43'),(28,1,1,'QUIT','2023-12-31 14:37:17'),(29,1,1,'QUIT','2023-12-31 14:54:11'),(30,1,1,'ffezf','2023-12-31 14:54:46'),(31,1,1,'QUIT','2023-12-31 14:55:08'),(32,1,1,'QUIT','2023-12-31 14:57:25'),(33,1,1,'AUTHENTICATE|kiki|azerty','2023-12-31 14:58:45'),(34,1,1,'CREATE_ACCOUNT_TRIGGER|SAEjaj|SAEjaj','2023-12-31 14:58:58'),(35,1,1,'bye','2023-12-31 15:06:29'),(36,1,1,'arret','2023-12-31 15:06:34'),(37,1,1,'jnej','2023-12-31 15:06:39'),(38,1,1,'QUIT','2023-12-31 15:06:56');
/*!40000 ALTER TABLE `messages` ENABLE KEYS */;
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
