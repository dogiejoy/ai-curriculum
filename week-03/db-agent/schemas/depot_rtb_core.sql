/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `products` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `sku` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'รหัสสินค้า',
  `barcode` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'บาร์โค้ด',
  `code_org` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'ชื่อสินค้า',
  `name_en` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `name_th` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` text COLLATE utf8mb4_unicode_ci COMMENT 'คำอธิบาย',
  `category` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `sub_category` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'ประเภทย่อย',
  `category_id` bigint(20) unsigned DEFAULT NULL,
  `supplier_id` bigint(20) unsigned DEFAULT NULL,
  `base_unit_id` bigint(20) unsigned NOT NULL,
  `registration_number` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'เลขทะเบียนยา',
  `is_controlled_drug` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'ยาควบคุมพิเศษ',
  `require_prescription` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'ต้องมีใบสั่งแพทย์',
  `active_ingredient` text COLLATE utf8mb4_unicode_ci COMMENT 'สารออกฤทธิ์',
  `storage_temp_min` decimal(5,2) DEFAULT NULL COMMENT 'อุณหภูมิต่ำสุด (°C)',
  `storage_temp_max` decimal(5,2) DEFAULT NULL COMMENT 'อุณหภูมิสูงสุด (°C)',
  `storage_condition` text COLLATE utf8mb4_unicode_ci COMMENT 'เงื่อนไขการเก็บ',
  `storage_zone_type` enum('normal','cold','refrigerated','controlled') COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'ประเภทโซนที่ต้องเก็บ',
  `min_stock_level` int(11) NOT NULL DEFAULT '0' COMMENT 'สต็อกขั้นต่ำ',
  `reorder_point` int(11) NOT NULL DEFAULT '0' COMMENT 'จุดสั่งซื้อใหม่',
  `reorder_quantity` int(11) NOT NULL DEFAULT '0' COMMENT 'จำนวนที่สั่งแต่ละครั้ง',
  `cost_price` decimal(10,2) DEFAULT NULL COMMENT 'ราคาทุน',
  `selling_price` decimal(10,2) DEFAULT NULL COMMENT 'ราคาขาย',
  `promotion` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `packing_info` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `tax_type` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'V',
  `is_active` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'สถานะการใช้งาน',
  `created_by` bigint(20) unsigned DEFAULT NULL,
  `updated_by` bigint(20) unsigned DEFAULT NULL,
  `deleted_by` bigint(20) unsigned DEFAULT NULL,
  `notes` text COLLATE utf8mb4_unicode_ci COMMENT 'หมายเหตุ',
  `image_path` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'พาธรูปภาพสินค้า',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `deleted_at` timestamp NULL DEFAULT NULL COMMENT 'วันที่ลบ (Soft Delete)',
  PRIMARY KEY (`id`),
  UNIQUE KEY `products_sku_unique` (`sku`),
  KEY `products_sku_index` (`sku`),
  KEY `products_barcode_index` (`barcode`),
  KEY `products_category_index` (`category`),
  KEY `products_base_unit_id_index` (`base_unit_id`),
  KEY `products_category_is_active_index` (`category`,`is_active`),
  KEY `products_deleted_by_foreign` (`deleted_by`),
  KEY `products_created_by_index` (`created_by`),
  KEY `products_updated_by_index` (`updated_by`),
  KEY `products_category_id_index` (`category_id`),
  KEY `products_code_org_index` (`code_org`),
  CONSTRAINT `products_base_unit_id_foreign` FOREIGN KEY (`base_unit_id`) REFERENCES `units` (`id`),
  CONSTRAINT `products_category_id_foreign` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE SET NULL,
  CONSTRAINT `products_created_by_foreign` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `products_deleted_by_foreign` FOREIGN KEY (`deleted_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `products_updated_by_foreign` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=1095 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `categories` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `parent_id` bigint(20) unsigned DEFAULT NULL,
  `code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'รหัสหมวดหมู่',
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'ชื่อหมวดหมู่',
  `description` text COLLATE utf8mb4_unicode_ci COMMENT 'คำอธิบาย',
  `sort_order` int(10) unsigned NOT NULL DEFAULT '0' COMMENT 'ลำดับการแสดง',
  `is_active` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'สถานะใช้งาน',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `categories_code_unique` (`code`),
  KEY `categories_parent_id_index` (`parent_id`),
  KEY `categories_is_active_index` (`is_active`),
  KEY `categories_sort_order_index` (`sort_order`),
  CONSTRAINT `categories_parent_id_foreign` FOREIGN KEY (`parent_id`) REFERENCES `categories` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `units`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `units` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `unit_code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'รหัสหน่วย',
  `unit_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'ชื่อหน่วย',
  `unit_type` enum('base','packaging') COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'ประเภทหน่วย: base=พื้นฐาน, packaging=บรรจุภัณฑ์',
  `description` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'คำอธิบาย',
  `is_active` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'สถานะการใช้งาน',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `units_unit_code_unique` (`unit_code`),
  KEY `units_unit_code_index` (`unit_code`),
  KEY `units_unit_type_index` (`unit_type`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `product_id` bigint(20) unsigned NOT NULL,
  `batch_id` bigint(20) unsigned DEFAULT NULL,
  `location_id` bigint(20) unsigned NOT NULL,
  `quantity` decimal(10,3) NOT NULL DEFAULT '0.000' COMMENT 'จำนวนในหน่วยพื้นฐาน',
  `reserved_quantity` decimal(10,3) NOT NULL DEFAULT '0.000' COMMENT 'จำนวนที่จองไว้',
  `available_quantity` decimal(10,3) GENERATED ALWAYS AS ((`quantity` - `reserved_quantity`)) STORED COMMENT 'จำนวนที่พร้อมใช้',
  `last_count_date` date DEFAULT NULL COMMENT 'วันที่นับล่าสุด',
  `last_count_by` bigint(20) unsigned DEFAULT NULL,
  `created_by` bigint(20) unsigned DEFAULT NULL,
  `updated_by` bigint(20) unsigned DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_inventory` (`product_id`,`batch_id`,`location_id`),
  KEY `inventory_last_count_by_foreign` (`last_count_by`),
  KEY `inventory_product_id_index` (`product_id`),
  KEY `inventory_batch_id_index` (`batch_id`),
  KEY `inventory_location_id_index` (`location_id`),
  KEY `inventory_product_id_batch_id_index` (`product_id`,`batch_id`),
  KEY `inventory_created_by_foreign` (`created_by`),
  KEY `inventory_updated_by_foreign` (`updated_by`),
  CONSTRAINT `inventory_batch_id_foreign` FOREIGN KEY (`batch_id`) REFERENCES `product_batches` (`id`),
  CONSTRAINT `inventory_created_by_foreign` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`),
  CONSTRAINT `inventory_last_count_by_foreign` FOREIGN KEY (`last_count_by`) REFERENCES `users` (`id`),
  CONSTRAINT `inventory_location_id_foreign` FOREIGN KEY (`location_id`) REFERENCES `storage_locations` (`id`),
  CONSTRAINT `inventory_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT `inventory_updated_by_foreign` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=59 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `branches`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `branches` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `branch_code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'รหัสสาขา',
  `branch_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'ชื่อสาขา',
  `branch_type` enum('clinic','hospital','retail','warehouse') COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'ประเภทสาขา: clinic=คลินิก, hospital=โรงพยาบาล, retail=ร้านค้า, warehouse=คลัง',
  `company_id` bigint(20) unsigned DEFAULT NULL,
  `contact_person` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'ผู้ติดต่อ',
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'เบอร์โทรศัพท์',
  `email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'อีเมล',
  `address` text COLLATE utf8mb4_unicode_ci COMMENT 'ที่อยู่',
  `province` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'จังหวัด',
  `district` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'อำเภอ',
  `postal_code` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'รหัสไปรษณีย์',
  `is_active` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'สถานะการใช้งาน',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `branches_branch_code_unique` (`branch_code`),
  KEY `branches_branch_code_index` (`branch_code`),
  KEY `branches_branch_type_index` (`branch_type`),
  KEY `branches_company_id_index` (`company_id`),
  CONSTRAINT `branches_company_id_foreign` FOREIGN KEY (`company_id`) REFERENCES `companies` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `branch_inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `branch_inventory` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `branch_id` bigint(20) unsigned NOT NULL COMMENT 'สาขา',
  `product_id` bigint(20) unsigned NOT NULL COMMENT 'สินค้า',
  `batch_id` bigint(20) unsigned DEFAULT NULL COMMENT 'Batch/Lot (nullable สำหรับสินค้าที่ไม่มี batch)',
  `quantity` decimal(10,3) NOT NULL DEFAULT '0.000' COMMENT 'จำนวนคงเหลือ (หน่วยพื้นฐาน)',
  `reserved_quantity` decimal(10,3) NOT NULL DEFAULT '0.000' COMMENT 'จำนวนที่จอง',
  `available_quantity` decimal(10,3) GENERATED ALWAYS AS ((`quantity` - `reserved_quantity`)) STORED COMMENT 'จำนวนที่พร้อมขาย = คงเหลือ - จอง',
  `last_count_date` date DEFAULT NULL COMMENT 'วันที่นับสต็อกล่าสุด',
  `last_count_by` bigint(20) unsigned DEFAULT NULL COMMENT 'ผู้นับสต็อกล่าสุด',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `branch_product_batch_unique` (`branch_id`,`product_id`,`batch_id`),
  KEY `branch_inventory_last_count_by_foreign` (`last_count_by`),
  KEY `branch_inventory_branch_id_index` (`branch_id`),
  KEY `branch_inventory_product_id_index` (`product_id`),
  KEY `branch_inventory_batch_id_index` (`batch_id`),
  KEY `branch_inventory_last_count_date_index` (`last_count_date`),
  CONSTRAINT `branch_inventory_batch_id_foreign` FOREIGN KEY (`batch_id`) REFERENCES `product_batches` (`id`) ON DELETE CASCADE,
  CONSTRAINT `branch_inventory_branch_id_foreign` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`id`) ON DELETE CASCADE,
  CONSTRAINT `branch_inventory_last_count_by_foreign` FOREIGN KEY (`last_count_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `branch_inventory_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `distribution_orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `distribution_orders` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `do_number` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'เลขที่ใบกระจายสินค้า',
  `branch_id` bigint(20) unsigned NOT NULL,
  `request_id` bigint(20) unsigned DEFAULT NULL,
  `order_date` date NOT NULL COMMENT 'วันที่สั่ง',
  `required_date` date DEFAULT NULL COMMENT 'วันที่ต้องการ',
  `ship_date` date DEFAULT NULL COMMENT 'วันที่จัดส่ง',
  `delivery_date` date DEFAULT NULL COMMENT 'วันที่ส่งถึง',
  `status` enum('draft','confirmed','picking','picked','packing','packed','shipped','delivered','cancelled') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'draft' COMMENT 'สถานะ',
  `priority` enum('low','normal','high','urgent') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'normal' COMMENT 'ความสำคัญ',
  `subtotal` decimal(12,2) NOT NULL DEFAULT '0.00' COMMENT 'ยอดรวมก่อนหัก',
  `discount` decimal(12,2) NOT NULL DEFAULT '0.00' COMMENT 'ส่วนลด',
  `tax` decimal(12,2) NOT NULL DEFAULT '0.00' COMMENT 'ภาษี',
  `shipping_cost` decimal(12,2) NOT NULL DEFAULT '0.00' COMMENT 'ค่าจัดส่ง',
  `total_amount` decimal(12,2) NOT NULL DEFAULT '0.00' COMMENT 'ยอดรวมทั้งสิ้น',
  `delivery_method` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'วิธีการจัดส่ง',
  `tracking_number` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'เลขติดตามพัสดุ',
  `notes` text COLLATE utf8mb4_unicode_ci COMMENT 'หมายเหตุ',
  `created_by` bigint(20) unsigned NOT NULL,
  `picked_by` bigint(20) unsigned DEFAULT NULL,
  `packed_by` bigint(20) unsigned DEFAULT NULL,
  `shipped_by` bigint(20) unsigned DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `distribution_orders_do_number_unique` (`do_number`),
  KEY `distribution_orders_created_by_foreign` (`created_by`),
  KEY `distribution_orders_picked_by_foreign` (`picked_by`),
  KEY `distribution_orders_packed_by_foreign` (`packed_by`),
  KEY `distribution_orders_shipped_by_foreign` (`shipped_by`),
  KEY `distribution_orders_do_number_index` (`do_number`),
  KEY `distribution_orders_branch_id_index` (`branch_id`),
  KEY `distribution_orders_status_index` (`status`),
  KEY `distribution_orders_order_date_index` (`order_date`),
  KEY `distribution_orders_branch_id_status_index` (`branch_id`,`status`),
  KEY `distribution_orders_status_required_date_index` (`status`,`required_date`),
  KEY `distribution_orders_request_id_index` (`request_id`),
  CONSTRAINT `distribution_orders_branch_id_foreign` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`id`),
  CONSTRAINT `distribution_orders_created_by_foreign` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`),
  CONSTRAINT `distribution_orders_packed_by_foreign` FOREIGN KEY (`packed_by`) REFERENCES `users` (`id`),
  CONSTRAINT `distribution_orders_picked_by_foreign` FOREIGN KEY (`picked_by`) REFERENCES `users` (`id`),
  CONSTRAINT `distribution_orders_request_id_foreign` FOREIGN KEY (`request_id`) REFERENCES `branch_requests` (`id`),
  CONSTRAINT `distribution_orders_shipped_by_foreign` FOREIGN KEY (`shipped_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `distribution_order_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `distribution_order_items` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `do_id` bigint(20) unsigned NOT NULL,
  `product_id` bigint(20) unsigned NOT NULL,
  `batch_id` bigint(20) unsigned DEFAULT NULL,
  `unit_id` bigint(20) unsigned NOT NULL,
  `ordered_qty` decimal(10,3) NOT NULL COMMENT 'จำนวนที่สั่ง',
  `picked_qty` decimal(10,3) NOT NULL DEFAULT '0.000' COMMENT 'จำนวนที่หยิบแล้ว',
  `shipped_qty` decimal(10,3) NOT NULL DEFAULT '0.000' COMMENT 'จำนวนที่จัดส่งแล้ว',
  `unit_price` decimal(10,2) DEFAULT NULL COMMENT 'ราคาต่อหน่วย',
  `discount_percent` decimal(5,2) NOT NULL DEFAULT '0.00' COMMENT 'ส่วนลด (%)',
  `discount_amount` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT 'ส่วนลด (บาท)',
  `total_price` decimal(12,2) GENERATED ALWAYS AS (((`ordered_qty` * `unit_price`) - `discount_amount`)) STORED COMMENT 'ยอดรวม',
  `pick_location_id` bigint(20) unsigned DEFAULT NULL,
  `picked_at` timestamp NULL DEFAULT NULL COMMENT 'เวลาที่หยิบ',
  `picked_by` bigint(20) unsigned DEFAULT NULL,
  `notes` text COLLATE utf8mb4_unicode_ci COMMENT 'หมายเหตุ',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `distribution_order_items_unit_id_foreign` (`unit_id`),
  KEY `distribution_order_items_picked_by_foreign` (`picked_by`),
  KEY `distribution_order_items_do_id_index` (`do_id`),
  KEY `distribution_order_items_product_id_index` (`product_id`),
  KEY `distribution_order_items_batch_id_index` (`batch_id`),
  KEY `distribution_order_items_do_id_product_id_index` (`do_id`,`product_id`),
  KEY `distribution_order_items_pick_location_id_index` (`pick_location_id`),
  CONSTRAINT `distribution_order_items_batch_id_foreign` FOREIGN KEY (`batch_id`) REFERENCES `product_batches` (`id`),
  CONSTRAINT `distribution_order_items_do_id_foreign` FOREIGN KEY (`do_id`) REFERENCES `distribution_orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `distribution_order_items_pick_location_id_foreign` FOREIGN KEY (`pick_location_id`) REFERENCES `storage_locations` (`id`),
  CONSTRAINT `distribution_order_items_picked_by_foreign` FOREIGN KEY (`picked_by`) REFERENCES `users` (`id`),
  CONSTRAINT `distribution_order_items_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT `distribution_order_items_unit_id_foreign` FOREIGN KEY (`unit_id`) REFERENCES `units` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `suppliers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `suppliers` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `supplier_code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'รหัสซัพพลายเออร์',
  `ref_code_rtb` varchar(25) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `supplier_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'ชื่อซัพพลายเออร์',
  `full_name` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `contact_person` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'ผู้ติดต่อ',
  `phone` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fax` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'อีเมล',
  `address` text COLLATE utf8mb4_unicode_ci COMMENT 'ที่อยู่',
  `province` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'จังหวัด',
  `district` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'อำเภอ',
  `postal_code` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'รหัสไปรษณีย์',
  `document_send_method` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `tax_id` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'เลขประจำตัวผู้เสียภาษี',
  `payment_terms` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'เงื่อนไขการชำระเงิน',
  `credit_limit` decimal(15,2) DEFAULT NULL,
  `bank_account_name` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `bank_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `bank_branch` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `bank_account_no` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `notes` text COLLATE utf8mb4_unicode_ci,
  `is_active` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'สถานะการใช้งาน',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `deleted_at` timestamp NULL DEFAULT NULL,
  `deleted_by` bigint(20) unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `suppliers_supplier_code_unique` (`supplier_code`),
  KEY `suppliers_supplier_code_index` (`supplier_code`),
  KEY `suppliers_supplier_name_index` (`supplier_name`),
  KEY `suppliers_deleted_by_foreign` (`deleted_by`),
  CONSTRAINT `suppliers_deleted_by_foreign` FOREIGN KEY (`deleted_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=163 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

