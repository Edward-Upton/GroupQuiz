-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema charities_day
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema charities_day
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `charities_day` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `charities_day` ;

-- -----------------------------------------------------
-- Table `charities_day`.`votes`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `charities_day`.`votes` (
  `id` INT(11) NOT NULL,
  `a` INT(11) NOT NULL DEFAULT '0',
  `b` INT(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
