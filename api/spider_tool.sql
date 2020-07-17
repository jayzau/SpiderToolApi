/*
 Navicat Premium Data Transfer

 Source Server         : jayzau
 Source Server Type    : MySQL
 Source Server Version : 50731
 Source Host           : 
 Source Schema         : spider_tool

 Target Server Type    : MySQL
 Target Server Version : 50731
 File Encoding         : 65001

 Date: 17/07/2020 11:54:17
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for captcha
-- ----------------------------
DROP TABLE IF EXISTS `captcha`;
CREATE TABLE `captcha`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `path` varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '验证码地址',
  `md5` varchar(81) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'md5值',
  `timestamp` int(11) NULL DEFAULT NULL,
  `captcha_id` varchar(81) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '图片id',
  `source` varchar(24) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '来源',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_captcha_timestamp`(`timestamp`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 37 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
