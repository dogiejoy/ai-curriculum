-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:8889
-- Generation Time: Jun 17, 2026 at 12:57 PM
-- Server version: 5.7.44
-- PHP Version: 8.3.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `depot_rtb`
--

-- --------------------------------------------------------

--
-- Table structure for table `alerts`
--

CREATE TABLE `alerts` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `alert_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `severity` enum('low','medium','high','critical') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'low' COMMENT 'ระดับความรุนแรง',
  `related_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'ประเภทข้อมูลที่เกี่ยวข้อง',
  `related_id` bigint(20) UNSIGNED DEFAULT NULL COMMENT 'ID ข้อมูลที่เกี่ยวข้อง',
  `branch_id` bigint(20) UNSIGNED DEFAULT NULL COMMENT 'สาขา (null = คลังกลาง)',
  `product_id` bigint(20) UNSIGNED DEFAULT NULL,
  `batch_id` bigint(20) UNSIGNED DEFAULT NULL,
  `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'หัวข้อแจ้งเตือน',
  `message` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'ข้อความ',
  `data` json DEFAULT NULL COMMENT 'ข้อมูลเพิ่มเติม (JSON)',
  `is_read` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'อ่านแล้ว',
  `is_resolved` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'แก้ไขแล้ว',
  `assigned_to` bigint(20) UNSIGNED DEFAULT NULL,
  `resolved_by` bigint(20) UNSIGNED DEFAULT NULL,
  `resolved_at` timestamp NULL DEFAULT NULL COMMENT 'วันที่แก้ไข',
  `resolution_notes` text COLLATE utf8mb4_unicode_ci COMMENT 'บันทึกการแก้ไข',
  `alert_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'วันที่แจ้งเตือน',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `branches`
--

CREATE TABLE `branches` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `branch_code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'รหัสสาขา',
  `branch_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'ชื่อสาขา',
  `branch_type` enum('clinic','hospital','retail','warehouse') COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'ประเภทสาขา: clinic=คลินิก, hospital=โรงพยาบาล, retail=ร้านค้า, warehouse=คลัง',
  `company_id` bigint(20) UNSIGNED DEFAULT NULL,
  `contact_person` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'ผู้ติดต่อ',
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'เบอร์โทรศัพท์',
  `email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'อีเมล',
  `address` text COLLATE utf8mb4_unicode_ci COMMENT 'ที่อยู่',
  `province` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'จังหวัด',
  `district` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'อำเภอ',
  `postal_code` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'รหัสไปรษณีย์',
  `is_active` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'สถานะการใช้งาน',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `branch_adjustments`
--

CREATE TABLE `branch_adjustments` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `branch_id` bigint(20) UNSIGNED NOT NULL,
  `adjustment_number` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `adjustment_type` enum('adjustment','damage','expire') COLLATE utf8mb4_unicode_ci NOT NULL,
  `reason` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `items_count` smallint(5) UNSIGNED NOT NULL DEFAULT '0',
  `total_increase` decimal(10,3) NOT NULL DEFAULT '0.000',
  `total_decrease` decimal(10,3) NOT NULL DEFAULT '0.000',
  `created_by` bigint(20) UNSIGNED NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `branch_inventory`
--

CREATE TABLE `branch_inventory` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `branch_id` bigint(20) UNSIGNED NOT NULL COMMENT 'สาขา',
  `product_id` bigint(20) UNSIGNED NOT NULL COMMENT 'สินค้า',
  `batch_id` bigint(20) UNSIGNED DEFAULT NULL COMMENT 'Batch/Lot (nullable สำหรับสินค้าที่ไม่มี batch)',
  `quantity` decimal(10,3) NOT NULL DEFAULT '0.000' COMMENT 'จำนวนคงเหลือ (หน่วยพื้นฐาน)',
  `reserved_quantity` decimal(10,3) NOT NULL DEFAULT '0.000' COMMENT 'จำนวนที่จอง',
  `available_quantity` decimal(10,3) GENERATED ALWAYS AS ((`quantity` - `reserved_quantity`)) STORED COMMENT 'จำนวนที่พร้อมขาย = คงเหลือ - จอง',
  `last_count_date` date DEFAULT NULL COMMENT 'วันที่นับสต็อกล่าสุด',
  `last_count_by` bigint(20) UNSIGNED DEFAULT NULL COMMENT 'ผู้นับสต็อกล่าสุด',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `branch_product_settings`
--

CREATE TABLE `branch_product_settings` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `branch_id` bigint(20) UNSIGNED NOT NULL COMMENT 'สาขา',
  `product_id` bigint(20) UNSIGNED NOT NULL COMMENT 'สินค้า',
  `min_stock_level` decimal(10,3) NOT NULL DEFAULT '0.000' COMMENT 'สต็อกขั้นต่ำ',
  `reorder_point` decimal(10,3) NOT NULL DEFAULT '0.000' COMMENT 'จุดสั่งสินค้า',
  `reorder_quantity` decimal(10,3) DEFAULT NULL COMMENT 'จำนวนที่สั่งแต่ละครั้ง',
  `max_stock_level` decimal(10,3) DEFAULT NULL COMMENT 'สต็อกสูงสุด',
  `is_active` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'ใช้งาน',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `branch_receiving`
--

CREATE TABLE `branch_receiving` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `receiving_number` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'เลขที่ใบรับสินค้า BR-YYYYMMDD-XXXX',
  `distribution_order_id` bigint(20) UNSIGNED NOT NULL,
  `branch_id` bigint(20) UNSIGNED NOT NULL,
  `status` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending' COMMENT 'pending, receiving, partially_received, received, rejected',
  `received_at` timestamp NULL DEFAULT NULL,
  `received_by` bigint(20) UNSIGNED DEFAULT NULL,
  `notes` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `branch_receiving_items`
--

CREATE TABLE `branch_receiving_items` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `branch_receiving_id` bigint(20) UNSIGNED NOT NULL,
  `distribution_order_item_id` bigint(20) UNSIGNED NOT NULL,
  `product_id` bigint(20) UNSIGNED NOT NULL,
  `product_batch_id` bigint(20) UNSIGNED DEFAULT NULL,
  `expected_quantity` decimal(10,3) NOT NULL COMMENT 'จำนวนที่ส่งมา',
  `received_quantity` decimal(10,3) NOT NULL DEFAULT '0.000' COMMENT 'จำนวนที่รับจริง',
  `rejected_quantity` decimal(10,3) NOT NULL DEFAULT '0.000' COMMENT 'จำนวนที่ปฏิเสธ',
  `status` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending' COMMENT 'pending, accepted, partially_accepted, rejected',
  `rejection_reason` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'damaged, expired, wrong_item, quality_issue, other',
  `rejection_notes` text COLLATE utf8mb4_unicode_ci,
  `scanned_barcode` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `scanned_sku` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `branch_requests`
--

CREATE TABLE `branch_requests` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `request_number` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'BRQ-{branch_code}-{YYYY}-{NNNN}',
  `branch_id` bigint(20) UNSIGNED NOT NULL,
  `parent_request_id` bigint(20) UNSIGNED DEFAULT NULL,
  `revision` int(11) NOT NULL DEFAULT '1' COMMENT 'รอบที่ (1, 2, 3...)',
  `request_date` date NOT NULL,
  `required_date` date DEFAULT NULL COMMENT 'วันที่ต้องการรับ',
  `status` enum('draft','submitted','approved','partial','rejected','fulfilling','completed','cancelled') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'draft',
  `priority` enum('low','normal','high','urgent') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'normal',
  `items_count` int(11) NOT NULL DEFAULT '0',
  `requested_items_total` decimal(12,3) NOT NULL DEFAULT '0.000' COMMENT 'ผลรวม requested_qty',
  `approved_items_total` decimal(12,3) NOT NULL DEFAULT '0.000' COMMENT 'ผลรวม approved_qty',
  `notes` text COLLATE utf8mb4_unicode_ci COMMENT 'หมายเหตุจากสาขา',
  `review_notes` text COLLATE utf8mb4_unicode_ci COMMENT 'หมายเหตุจากคลัง',
  `rejection_reason` text COLLATE utf8mb4_unicode_ci,
  `do_id` bigint(20) UNSIGNED DEFAULT NULL,
  `requested_by` bigint(20) UNSIGNED NOT NULL,
  `reviewed_by` bigint(20) UNSIGNED DEFAULT NULL,
  `submitted_at` timestamp NULL DEFAULT NULL,
  `reviewed_at` timestamp NULL DEFAULT NULL,
  `converted_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `branch_request_items`
--

CREATE TABLE `branch_request_items` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `request_id` bigint(20) UNSIGNED NOT NULL,
  `product_id` bigint(20) UNSIGNED NOT NULL,
  `unit_id` bigint(20) UNSIGNED NOT NULL,
  `requested_qty` decimal(10,3) NOT NULL COMMENT 'จำนวนที่สาขาขอ',
  `approved_qty` decimal(10,3) NOT NULL DEFAULT '0.000' COMMENT 'จำนวนที่คลังอนุมัติ',
  `branch_current_stock` decimal(10,3) DEFAULT NULL COMMENT 'สต็อกสาขาตอนสั่ง',
  `branch_reorder_point` decimal(10,3) DEFAULT NULL COMMENT 'Reorder point ตอนสั่ง',
  `warehouse_available_qty` decimal(10,3) DEFAULT NULL COMMENT 'สต็อกคลังตอนคลังตรวจ',
  `item_status` enum('pending','approved','partial','rejected') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending',
  `notes` text COLLATE utf8mb4_unicode_ci,
  `reject_reason` text COLLATE utf8mb4_unicode_ci COMMENT 'เหตุผล reject เฉพาะ item',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `branch_returns`
--

CREATE TABLE `branch_returns` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `return_number` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'เลขที่ใบคืนสินค้า RTN-YYYYMMDD-XXXX',
  `branch_receiving_item_id` bigint(20) UNSIGNED NOT NULL,
  `branch_id` bigint(20) UNSIGNED NOT NULL,
  `product_id` bigint(20) UNSIGNED NOT NULL,
  `product_batch_id` bigint(20) UNSIGNED DEFAULT NULL,
  `quantity` decimal(10,3) NOT NULL COMMENT 'จำนวนที่ปฏิเสธ/คืน',
  `display_quantity` decimal(10,3) DEFAULT NULL COMMENT 'จำนวนในหน่วย DO (สำหรับแสดง)',
  `unit_id` bigint(20) UNSIGNED DEFAULT NULL,
  `distribution_order_id` bigint(20) UNSIGNED DEFAULT NULL,
  `status` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending' COMMENT 'pending, returning, received, disposed, lost',
  `rejection_reason` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'damaged, expired, wrong_item, quality_issue, other',
  `rejection_notes` text COLLATE utf8mb4_unicode_ci,
  `warehouse_action` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'return_to_stock, damaged, expired_dispose, lost, other',
  `warehouse_notes` text COLLATE utf8mb4_unicode_ci,
  `processed_by` bigint(20) UNSIGNED DEFAULT NULL,
  `processed_at` timestamp NULL DEFAULT NULL,
  `returned_to_location_id` bigint(20) UNSIGNED DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `branch_stock_counts`
--

CREATE TABLE `branch_stock_counts` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `count_number` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'เลขที่การนับสต็อก',
  `branch_id` bigint(20) UNSIGNED NOT NULL COMMENT 'สาขา',
  `count_date` date NOT NULL COMMENT 'วันที่นับ',
  `count_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` enum('draft','in_progress','submitted','approved','rejected','cancelled') COLLATE utf8mb4_unicode_ci DEFAULT 'draft',
  `notes` text COLLATE utf8mb4_unicode_ci COMMENT 'หมายเหตุ',
  `created_by` bigint(20) UNSIGNED NOT NULL COMMENT 'ผู้สร้าง',
  `counted_by` bigint(20) UNSIGNED DEFAULT NULL,
  `submitted_by` bigint(20) UNSIGNED DEFAULT NULL COMMENT 'ผู้ส่งอนุมัติ',
  `submitted_at` timestamp NULL DEFAULT NULL COMMENT 'วันที่ส่งอนุมัติ',
  `approved_by` bigint(20) UNSIGNED DEFAULT NULL COMMENT 'ผู้อนุมัติ',
  `approved_at` timestamp NULL DEFAULT NULL COMMENT 'วันที่อนุมัติ',
  `approval_notes` text COLLATE utf8mb4_unicode_ci COMMENT 'หมายเหตุการอนุมัติ/ปฏิเสธ',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `branch_stock_count_items`
--

CREATE TABLE `branch_stock_count_items` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `stock_count_id` bigint(20) UNSIGNED NOT NULL COMMENT 'การนับสต็อก',
  `product_id` bigint(20) UNSIGNED NOT NULL COMMENT 'สินค้า',
  `batch_id` bigint(20) UNSIGNED DEFAULT NULL,
  `system_quantity` decimal(10,3) NOT NULL DEFAULT '0.000' COMMENT 'จำนวนตามระบบ',
  `actual_quantity` decimal(10,3) DEFAULT NULL,
  `difference_quantity` decimal(10,3) GENERATED ALWAYS AS ((case when isnull(`actual_quantity`) then NULL else (`actual_quantity` - `system_quantity`) end)) STORED,
  `notes` text COLLATE utf8mb4_unicode_ci COMMENT 'หมายเหตุ',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `branch_stock_movements`
--

CREATE TABLE `branch_stock_movements` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `branch_id` bigint(20) UNSIGNED NOT NULL COMMENT 'สาขา',
  `product_id` bigint(20) UNSIGNED NOT NULL COMMENT 'สินค้า',
  `batch_id` bigint(20) UNSIGNED DEFAULT NULL COMMENT 'Batch/Lot (nullable สำหรับสินค้าที่ไม่มี batch)',
  `movement_type` enum('receive_from_warehouse','sale','return_to_warehouse','adjustment','damage','expire','count','transfer_out','transfer_in','transfer_loss') COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'ประเภทการเคลื่อนไหว',
  `quantity` decimal(10,3) NOT NULL COMMENT 'จำนวน (+/-) หน่วยพื้นฐาน',
  `quantity_before` decimal(10,3) DEFAULT NULL COMMENT 'จำนวนก่อน',
  `quantity_after` decimal(10,3) DEFAULT NULL COMMENT 'จำนวนหลัง',
  `reference_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'ประเภทเอกสารอ้างอิง',
  `reference_id` bigint(20) UNSIGNED DEFAULT NULL COMMENT 'ID เอกสารอ้างอิง',
  `reference_number` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'เลขที่เอกสารอ้างอิง',
  `notes` text COLLATE utf8mb4_unicode_ci COMMENT 'หมายเหตุ',
  `created_by` bigint(20) UNSIGNED NOT NULL COMMENT 'ผู้บันทึก',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `branch_transfers`
--

CREATE TABLE `branch_transfers` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `transfer_number` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'เลขที่ใบโอน BT-YYYYMMDD-XXXX',
  `from_branch_id` bigint(20) UNSIGNED NOT NULL,
  `to_branch_id` bigint(20) UNSIGNED NOT NULL,
  `status` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'draft' COMMENT 'draft, confirmed, shipping, received, completed, cancelled',
  `requested_by` bigint(20) UNSIGNED NOT NULL,
  `confirmed_at` timestamp NULL DEFAULT NULL,
  `shipped_at` timestamp NULL DEFAULT NULL,
  `shipped_by` bigint(20) UNSIGNED DEFAULT NULL,
  `received_at` timestamp NULL DEFAULT NULL,
  `received_by` bigint(20) UNSIGNED DEFAULT NULL,
  `notes` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `branch_transfer_items`
--

CREATE TABLE `branch_transfer_items` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `branch_transfer_id` bigint(20) UNSIGNED NOT NULL,
  `product_id` bigint(20) UNSIGNED NOT NULL,
  `product_batch_id` bigint(20) UNSIGNED DEFAULT NULL,
  `quantity` decimal(10,3) NOT NULL COMMENT 'จำนวนที่โอน',
  `received_quantity` decimal(10,3) NOT NULL DEFAULT '0.000' COMMENT 'จำนวนที่รับจริง',
  `variance_action` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'return_stock or loss — sender decides on partial receive',
  `notes` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `cache`
--

CREATE TABLE `cache` (
  `key` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `value` mediumtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `expiration` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `cache_locks`
--

CREATE TABLE `cache_locks` (
  `key` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `owner` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `expiration` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `categories`
--

CREATE TABLE `categories` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `parent_id` bigint(20) UNSIGNED DEFAULT NULL,
  `code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'รหัสหมวดหมู่',
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'ชื่อหมวดหมู่',
  `description` text COLLATE utf8mb4_unicode_ci COMMENT 'คำอธิบาย',
  `sort_order` int(10) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'ลำดับการแสดง',
  `is_active` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'สถานะใช้งาน',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `companies`
--

CREATE TABLE `companies` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'รหัสบริษัท เช่น RCT, RPP',
  `name_th` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'ชื่อบริษัท (ไทย)',
  `name_en` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'ชื่อบริษัท (อังกฤษ)',
  `tax_id` varchar(13) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'เลขผู้เสียภาษี 13 หลัก',
  `branch_tax_no` varchar(5) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '00000' COMMENT 'เลขสาขา (00000=สำนักงานใหญ่)',
  `is_vat_registered` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'จด VAT มั้ย',
  `vat_rate` decimal(5,2) NOT NULL DEFAULT '7.00' COMMENT 'อัตรา VAT %',
  `address` text COLLATE utf8mb4_unicode_ci,
  `province` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `district` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `subdistrict` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `postal_code` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fax` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `website` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `bank_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `bank_account_no` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `bank_account_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `logo_path` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `signature_path` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `notes` text COLLATE utf8mb4_unicode_ci,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `distribution_orders`
--

CREATE TABLE `distribution_orders` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `do_number` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'เลขที่ใบกระจายสินค้า',
  `branch_id` bigint(20) UNSIGNED NOT NULL,
  `request_id` bigint(20) UNSIGNED DEFAULT NULL,
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
  `created_by` bigint(20) UNSIGNED NOT NULL,
  `picked_by` bigint(20) UNSIGNED DEFAULT NULL,
  `packed_by` bigint(20) UNSIGNED DEFAULT NULL,
  `shipped_by` bigint(20) UNSIGNED DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `distribution_order_items`
--

CREATE TABLE `distribution_order_items` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `do_id` bigint(20) UNSIGNED NOT NULL,
  `product_id` bigint(20) UNSIGNED NOT NULL,
  `batch_id` bigint(20) UNSIGNED DEFAULT NULL,
  `unit_id` bigint(20) UNSIGNED NOT NULL,
  `ordered_qty` decimal(10,3) NOT NULL COMMENT 'จำนวนที่สั่ง',
  `picked_qty` decimal(10,3) NOT NULL DEFAULT '0.000' COMMENT 'จำนวนที่หยิบแล้ว',
  `shipped_qty` decimal(10,3) NOT NULL DEFAULT '0.000' COMMENT 'จำนวนที่จัดส่งแล้ว',
  `unit_price` decimal(10,2) DEFAULT NULL COMMENT 'ราคาต่อหน่วย',
  `discount_percent` decimal(5,2) NOT NULL DEFAULT '0.00' COMMENT 'ส่วนลด (%)',
  `discount_amount` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT 'ส่วนลด (บาท)',
  `total_price` decimal(12,2) GENERATED ALWAYS AS (((`ordered_qty` * `unit_price`) - `discount_amount`)) STORED COMMENT 'ยอดรวม',
  `pick_location_id` bigint(20) UNSIGNED DEFAULT NULL,
  `picked_at` timestamp NULL DEFAULT NULL COMMENT 'เวลาที่หยิบ',
  `picked_by` bigint(20) UNSIGNED DEFAULT NULL,
  `notes` text COLLATE utf8mb4_unicode_ci COMMENT 'หมายเหตุ',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `distribution_order_picks`
--

CREATE TABLE `distribution_order_picks` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `do_item_id` bigint(20) UNSIGNED NOT NULL,
  `batch_id` bigint(20) UNSIGNED DEFAULT NULL,
  `location_id` bigint(20) UNSIGNED NOT NULL,
  `quantity` decimal(10,3) NOT NULL COMMENT 'จำนวนที่หยิบ',
  `picked_by` bigint(20) UNSIGNED NOT NULL,
  `picked_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'เวลาที่หยิบ',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `failed_jobs`
--

CREATE TABLE `failed_jobs` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `uuid` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `connection` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `queue` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `payload` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `exception` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `failed_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `goods_receipts`
--

CREATE TABLE `goods_receipts` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `gr_number` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'เลขที่ใบรับสินค้า',
  `po_id` bigint(20) UNSIGNED NOT NULL,
  `supplier_id` bigint(20) UNSIGNED DEFAULT NULL,
  `receipt_date` date NOT NULL COMMENT 'วันที่รับสินค้า',
  `received_by` bigint(20) UNSIGNED NOT NULL,
  `verified_by` bigint(20) UNSIGNED DEFAULT NULL,
  `verified_at` timestamp NULL DEFAULT NULL,
  `status` enum('draft','pending_verification','verified','completed','rejected','cancelled') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'draft',
  `notes` text COLLATE utf8mb4_unicode_ci COMMENT 'หมายเหตุ',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `goods_receipt_items`
--

CREATE TABLE `goods_receipt_items` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `gr_id` bigint(20) UNSIGNED NOT NULL,
  `po_item_id` bigint(20) UNSIGNED NOT NULL,
  `product_id` bigint(20) UNSIGNED NOT NULL,
  `batch_id` bigint(20) UNSIGNED NOT NULL,
  `unit_id` bigint(20) UNSIGNED NOT NULL,
  `received_qty` decimal(10,3) NOT NULL COMMENT 'จำนวนที่รับ',
  `location_id` bigint(20) UNSIGNED DEFAULT NULL,
  `quality_status` enum('pending','approved','quarantine','rejected') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending',
  `inspected_by` bigint(20) UNSIGNED DEFAULT NULL,
  `inspected_at` timestamp NULL DEFAULT NULL,
  `notes` text COLLATE utf8mb4_unicode_ci COMMENT 'หมายเหตุ',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `inventory`
--

CREATE TABLE `inventory` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `product_id` bigint(20) UNSIGNED NOT NULL,
  `batch_id` bigint(20) UNSIGNED DEFAULT NULL,
  `location_id` bigint(20) UNSIGNED NOT NULL,
  `quantity` decimal(10,3) NOT NULL DEFAULT '0.000' COMMENT 'จำนวนในหน่วยพื้นฐาน',
  `reserved_quantity` decimal(10,3) NOT NULL DEFAULT '0.000' COMMENT 'จำนวนที่จองไว้',
  `available_quantity` decimal(10,3) GENERATED ALWAYS AS ((`quantity` - `reserved_quantity`)) STORED COMMENT 'จำนวนที่พร้อมใช้',
  `last_count_date` date DEFAULT NULL COMMENT 'วันที่นับล่าสุด',
  `last_count_by` bigint(20) UNSIGNED DEFAULT NULL,
  `created_by` bigint(20) UNSIGNED DEFAULT NULL,
  `updated_by` bigint(20) UNSIGNED DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `jobs`
--

CREATE TABLE `jobs` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `queue` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `payload` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `attempts` tinyint(3) UNSIGNED NOT NULL,
  `reserved_at` int(10) UNSIGNED DEFAULT NULL,
  `available_at` int(10) UNSIGNED NOT NULL,
  `created_at` int(10) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `job_batches`
--

CREATE TABLE `job_batches` (
  `id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `total_jobs` int(11) NOT NULL,
  `pending_jobs` int(11) NOT NULL,
  `failed_jobs` int(11) NOT NULL,
  `failed_job_ids` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `options` mediumtext COLLATE utf8mb4_unicode_ci,
  `cancelled_at` int(11) DEFAULT NULL,
  `created_at` int(11) NOT NULL,
  `finished_at` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `migrations`
--

CREATE TABLE `migrations` (
  `id` int(10) UNSIGNED NOT NULL,
  `migration` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `batch` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `mst_vendor`
--

CREATE TABLE `mst_vendor` (
  `cmid` char(2) NOT NULL DEFAULT 'CM',
  `ccust` varchar(15) NOT NULL DEFAULT '0',
  `ref_code_zel` varchar(25) DEFAULT NULL COMMENT 'zuellig code',
  `cnme` varchar(70) DEFAULT NULL,
  `cname` varchar(70) DEFAULT NULL,
  `cadd1` varchar(100) DEFAULT NULL,
  `cadd2` varchar(100) DEFAULT NULL,
  `czip` varchar(9) DEFAULT NULL,
  `cphon` varchar(255) DEFAULT NULL,
  `cmfaxn` varchar(25) DEFAULT NULL,
  `ccon` varchar(255) DEFAULT NULL,
  `crdol` decimal(15,2) NOT NULL DEFAULT '0.00',
  `ctype` varchar(4) DEFAULT NULL,
  `cterm` varchar(5) NOT NULL,
  `cdisc` char(2) NOT NULL DEFAULT 'A3',
  `ctax` varchar(50) DEFAULT NULL,
  `cship` varchar(12) NOT NULL DEFAULT '0',
  `cpcd` int(11) DEFAULT '0' COMMENT 'Rule ID',
  `p_name` varchar(255) DEFAULT NULL COMMENT 'ข้อมูลการจ่าย Name',
  `p_bank` varchar(255) DEFAULT NULL COMMENT 'ข้อมูลการจ่าย ธนาคาร',
  `p_bank_branch` varchar(255) DEFAULT NULL COMMENT 'ข้อมูลการจ่าย สาขา',
  `p_bank_no` varchar(100) DEFAULT NULL COMMENT 'ข้อมูลการจ่าย Bank No.',
  `p_send` varchar(255) DEFAULT NULL COMMENT 'ข้อมูลการจ่าย ส่งหลักฐานการโอน',
  `mgroup` varchar(255) DEFAULT NULL COMMENT 'Group',
  `csal` int(6) NOT NULL DEFAULT '0',
  `csal1` int(6) NOT NULL DEFAULT '0',
  `csal2` int(6) NOT NULL DEFAULT '0',
  `csal3` int(6) NOT NULL DEFAULT '0',
  `csal4` int(6) NOT NULL DEFAULT '0',
  `csal5` int(6) NOT NULL DEFAULT '0',
  `csal6` int(6) NOT NULL DEFAULT '0',
  `csal7` int(6) NOT NULL DEFAULT '0',
  `csal8` int(6) NOT NULL DEFAULT '0',
  `csal9` int(6) NOT NULL DEFAULT '0' COMMENT 'First bill collector',
  `csal10` int(6) NOT NULL DEFAULT '0' COMMENT 'Second bill collector',
  `cwhse` char(2) NOT NULL DEFAULT 'K1',
  `cref01` varchar(5) DEFAULT NULL,
  `cref02` varchar(5) DEFAULT NULL,
  `cref03` varchar(5) DEFAULT NULL,
  `cref04` varchar(5) DEFAULT NULL,
  `cref05` varchar(5) DEFAULT NULL,
  `cmexcn` varchar(10) DEFAULT NULL,
  `clusr` char(1) DEFAULT NULL COMMENT 'Nature of Business',
  `cldte` int(8) NOT NULL DEFAULT '0',
  `cltme` int(6) NOT NULL DEFAULT '0',
  `cmenus` varchar(10) DEFAULT NULL,
  `cmendt` varchar(255) NOT NULL DEFAULT '0',
  `cmentm` int(6) NOT NULL DEFAULT '0',
  `camtd` double NOT NULL DEFAULT '0',
  `copen` double NOT NULL DEFAULT '0',
  `balcre` double NOT NULL DEFAULT '0',
  `cmhold` double NOT NULL DEFAULT '0',
  `cstatus` int(2) NOT NULL DEFAULT '0',
  `ccomment` text,
  `dc_type` enum('DB','DC','DT') NOT NULL DEFAULT 'DB',
  `diferen_head` enum('Y','N') NOT NULL DEFAULT 'Y',
  `status` enum('Y','N') DEFAULT 'Y',
  `created_at` timestamp NULL DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` int(11) DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- --------------------------------------------------------

--
-- Table structure for table `password_reset_tokens`
--

CREATE TABLE `password_reset_tokens` (
  `email` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `token` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `personal_access_tokens`
--

CREATE TABLE `personal_access_tokens` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `tokenable_type` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tokenable_id` bigint(20) UNSIGNED NOT NULL,
  `name` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `token` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `abilities` text COLLATE utf8mb4_unicode_ci,
  `last_used_at` timestamp NULL DEFAULT NULL,
  `expires_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `products`
--

CREATE TABLE `products` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `sku` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'รหัสสินค้า',
  `barcode` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'บาร์โค้ด',
  `code_org` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'ชื่อสินค้า',
  `name_en` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `name_th` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` text COLLATE utf8mb4_unicode_ci COMMENT 'คำอธิบาย',
  `category` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `sub_category` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'ประเภทย่อย',
  `category_id` bigint(20) UNSIGNED DEFAULT NULL,
  `supplier_id` bigint(20) UNSIGNED DEFAULT NULL,
  `base_unit_id` bigint(20) UNSIGNED NOT NULL,
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
  `created_by` bigint(20) UNSIGNED DEFAULT NULL,
  `updated_by` bigint(20) UNSIGNED DEFAULT NULL,
  `deleted_by` bigint(20) UNSIGNED DEFAULT NULL,
  `notes` text COLLATE utf8mb4_unicode_ci COMMENT 'หมายเหตุ',
  `image_path` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'พาธรูปภาพสินค้า',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `deleted_at` timestamp NULL DEFAULT NULL COMMENT 'วันที่ลบ (Soft Delete)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `products_bk`
--

CREATE TABLE `products_bk` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `sku` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'รหัสสินค้า',
  `barcode` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'บาร์โค้ด',
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'ชื่อสินค้า',
  `description` text COLLATE utf8mb4_unicode_ci COMMENT 'คำอธิบาย',
  `category` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `sub_category` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'ประเภทย่อย',
  `category_id` bigint(20) UNSIGNED DEFAULT NULL,
  `base_unit_id` bigint(20) UNSIGNED NOT NULL,
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
  `tax_type` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'V',
  `is_active` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'สถานะการใช้งาน',
  `created_by` bigint(20) UNSIGNED DEFAULT NULL,
  `updated_by` bigint(20) UNSIGNED DEFAULT NULL,
  `deleted_by` bigint(20) UNSIGNED DEFAULT NULL,
  `notes` text COLLATE utf8mb4_unicode_ci COMMENT 'หมายเหตุ',
  `image_path` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'พาธรูปภาพสินค้า',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `deleted_at` timestamp NULL DEFAULT NULL COMMENT 'วันที่ลบ (Soft Delete)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `product_batches`
--

CREATE TABLE `product_batches` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `product_id` bigint(20) UNSIGNED NOT NULL,
  `batch_number` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'เลขที่ Batch/Lot',
  `manufacture_date` date DEFAULT NULL COMMENT 'วันที่ผลิต',
  `expiry_date` date NOT NULL COMMENT 'วันหมดอายุ',
  `supplier_id` bigint(20) UNSIGNED DEFAULT NULL,
  `receive_date` date NOT NULL COMMENT 'วันที่รับ',
  `received_unit_id` bigint(20) UNSIGNED NOT NULL,
  `received_quantity` decimal(10,3) NOT NULL COMMENT 'จำนวนที่รับในหน่วยรับเข้า',
  `quantity_in_base_unit` int(11) NOT NULL COMMENT 'จำนวนในหน่วยพื้นฐาน',
  `is_quarantine` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'อยู่ระหว่างกักกัน',
  `quarantine_until` date DEFAULT NULL COMMENT 'กักกันถึงวันที่',
  `quarantine_reason` text COLLATE utf8mb4_unicode_ci COMMENT 'เหตุผลกักกัน',
  `approved_by` bigint(20) UNSIGNED DEFAULT NULL,
  `approved_at` timestamp NULL DEFAULT NULL COMMENT 'วันที่อนุมัติ',
  `status` enum('active','quarantine','expired','recalled','damaged','closed') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'active',
  `cost_per_unit` decimal(10,2) DEFAULT NULL COMMENT 'ต้นทุนต่อหน่วยรับเข้า',
  `notes` text COLLATE utf8mb4_unicode_ci COMMENT 'หมายเหตุ',
  `created_by` bigint(20) UNSIGNED DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `product_unit_conversions`
--

CREATE TABLE `product_unit_conversions` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `product_id` bigint(20) UNSIGNED NOT NULL,
  `base_unit_id` bigint(20) UNSIGNED NOT NULL,
  `purchase_unit_id` bigint(20) UNSIGNED NOT NULL,
  `purchase_to_base_qty` decimal(10,3) NOT NULL COMMENT '1 หน่วยซื้อ = กี่หน่วยพื้นฐาน',
  `purchase_price` decimal(10,2) DEFAULT NULL COMMENT 'ราคาต่อหน่วยซื้อ',
  `distribution_unit_id` bigint(20) UNSIGNED NOT NULL,
  `distribution_to_base_qty` decimal(10,3) NOT NULL COMMENT '1 หน่วยจ่าย = กี่หน่วยพื้นฐาน',
  `distribution_price` decimal(10,2) DEFAULT NULL COMMENT 'ราคาต่อหน่วยจ่าย',
  `sales_unit_id` bigint(20) UNSIGNED DEFAULT NULL,
  `sales_to_base_qty` decimal(10,3) DEFAULT NULL COMMENT '1 หน่วยขาย = กี่หน่วยพื้นฐาน',
  `sales_price` decimal(10,2) DEFAULT NULL COMMENT 'ราคาต่อหน่วยขาย',
  `is_active` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'สถานะการใช้งาน',
  `notes` text COLLATE utf8mb4_unicode_ci,
  `effective_from` date DEFAULT NULL COMMENT 'มีผลตั้งแต่',
  `effective_to` date DEFAULT NULL COMMENT 'มีผลถึง',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `product_unit_conversions_bk`
--

CREATE TABLE `product_unit_conversions_bk` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `product_id` bigint(20) UNSIGNED NOT NULL,
  `base_unit_id` bigint(20) UNSIGNED NOT NULL,
  `purchase_unit_id` bigint(20) UNSIGNED NOT NULL,
  `purchase_to_base_qty` decimal(10,3) NOT NULL COMMENT '1 หน่วยซื้อ = กี่หน่วยพื้นฐาน',
  `purchase_price` decimal(10,2) DEFAULT NULL COMMENT 'ราคาต่อหน่วยซื้อ',
  `distribution_unit_id` bigint(20) UNSIGNED NOT NULL,
  `distribution_to_base_qty` decimal(10,3) NOT NULL COMMENT '1 หน่วยจ่าย = กี่หน่วยพื้นฐาน',
  `distribution_price` decimal(10,2) DEFAULT NULL COMMENT 'ราคาต่อหน่วยจ่าย',
  `sales_unit_id` bigint(20) UNSIGNED DEFAULT NULL,
  `sales_to_base_qty` decimal(10,3) DEFAULT NULL COMMENT '1 หน่วยขาย = กี่หน่วยพื้นฐาน',
  `sales_price` decimal(10,2) DEFAULT NULL COMMENT 'ราคาต่อหน่วยขาย',
  `is_active` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'สถานะการใช้งาน',
  `effective_from` date DEFAULT NULL COMMENT 'มีผลตั้งแต่',
  `effective_to` date DEFAULT NULL COMMENT 'มีผลถึง',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `purchase_orders`
--

CREATE TABLE `purchase_orders` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `po_number` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'เลขที่ใบสั่งซื้อ',
  `supplier_id` bigint(20) UNSIGNED NOT NULL,
  `order_date` date NOT NULL COMMENT 'วันที่สั่งซื้อ',
  `expected_date` date DEFAULT NULL COMMENT 'วันที่คาดว่าจะได้รับ',
  `received_date` date DEFAULT NULL COMMENT 'วันที่ได้รับจริง',
  `status` enum('draft','submitted','approved','ordered','partial_received','received','cancelled') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'draft' COMMENT 'สถานะ',
  `subtotal` decimal(12,2) NOT NULL DEFAULT '0.00' COMMENT 'ยอดรวมก่อนหัก',
  `discount` decimal(12,2) NOT NULL DEFAULT '0.00' COMMENT 'ส่วนลด',
  `tax` decimal(12,2) NOT NULL DEFAULT '0.00' COMMENT 'ภาษี',
  `shipping_cost` decimal(12,2) NOT NULL DEFAULT '0.00' COMMENT 'ค่าจัดส่ง',
  `total_amount` decimal(12,2) NOT NULL DEFAULT '0.00' COMMENT 'ยอดรวมทั้งสิ้น',
  `payment_terms` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'เงื่อนไขการชำระเงิน',
  `payment_status` enum('pending','partial','paid') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending' COMMENT 'สถานะการชำระเงิน',
  `notes` text COLLATE utf8mb4_unicode_ci COMMENT 'หมายเหตุ',
  `created_by` bigint(20) UNSIGNED NOT NULL,
  `approved_by` bigint(20) UNSIGNED DEFAULT NULL,
  `approved_at` timestamp NULL DEFAULT NULL COMMENT 'วันที่อนุมัติ',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `purchase_order_items`
--

CREATE TABLE `purchase_order_items` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `po_id` bigint(20) UNSIGNED NOT NULL,
  `product_id` bigint(20) UNSIGNED NOT NULL,
  `unit_id` bigint(20) UNSIGNED NOT NULL,
  `ordered_qty` decimal(10,3) NOT NULL COMMENT 'จำนวนที่สั่ง',
  `received_qty` decimal(10,3) NOT NULL DEFAULT '0.000' COMMENT 'จำนวนที่รับแล้ว',
  `unit_price` decimal(10,2) NOT NULL COMMENT 'ราคาต่อหน่วย',
  `discount_percent` decimal(5,2) NOT NULL DEFAULT '0.00' COMMENT 'ส่วนลด (%)',
  `discount_amount` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT 'ส่วนลด (บาท)',
  `total_price` decimal(12,2) GENERATED ALWAYS AS (((`ordered_qty` * `unit_price`) - `discount_amount`)) STORED COMMENT 'ยอดรวม',
  `batch_number` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'เลขที่ Batch (เมื่อรับของ)',
  `expiry_date` date DEFAULT NULL COMMENT 'วันหมดอายุ (เมื่อรับของ)',
  `notes` text COLLATE utf8mb4_unicode_ci COMMENT 'หมายเหตุ',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `sessions`
--

CREATE TABLE `sessions` (
  `id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` bigint(20) UNSIGNED DEFAULT NULL,
  `ip_address` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_agent` text COLLATE utf8mb4_unicode_ci,
  `payload` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_activity` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `stock_adjustments`
--

CREATE TABLE `stock_adjustments` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `adjustment_number` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'เลขที่ใบปรับปรุงสต็อก',
  `adjustment_type` enum('count','damage','expire','lost','found','other') COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'ประเภทการปรับปรุง',
  `adjustment_date` date NOT NULL COMMENT 'วันที่ปรับปรุง',
  `reason` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'เหตุผล',
  `status` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'draft',
  `created_by` bigint(20) UNSIGNED NOT NULL,
  `approved_by` bigint(20) UNSIGNED DEFAULT NULL,
  `approved_at` timestamp NULL DEFAULT NULL COMMENT 'วันที่อนุมัติ',
  `cancelled_by` bigint(20) UNSIGNED DEFAULT NULL,
  `cancelled_at` timestamp NULL DEFAULT NULL,
  `rejection_reason` text COLLATE utf8mb4_unicode_ci,
  `cancellation_reason` text COLLATE utf8mb4_unicode_ci,
  `notes` text COLLATE utf8mb4_unicode_ci COMMENT 'หมายเหตุ',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `stock_adjustment_items`
--

CREATE TABLE `stock_adjustment_items` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `adjustment_id` bigint(20) UNSIGNED NOT NULL,
  `product_id` bigint(20) UNSIGNED NOT NULL,
  `batch_id` bigint(20) UNSIGNED DEFAULT NULL,
  `location_id` bigint(20) UNSIGNED NOT NULL,
  `system_qty` decimal(10,3) NOT NULL COMMENT 'จำนวนในระบบ (หน่วยพื้นฐาน)',
  `actual_qty` decimal(10,3) NOT NULL COMMENT 'จำนวนจริง (หน่วยพื้นฐาน)',
  `difference_qty` decimal(10,3) GENERATED ALWAYS AS ((`actual_qty` - `system_qty`)) STORED COMMENT 'ส่วนต่าง = จริง - ระบบ',
  `unit_id` bigint(20) UNSIGNED NOT NULL,
  `notes` text COLLATE utf8mb4_unicode_ci COMMENT 'หมายเหตุ',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `stock_movements`
--

CREATE TABLE `stock_movements` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `product_id` bigint(20) UNSIGNED NOT NULL,
  `batch_id` bigint(20) UNSIGNED DEFAULT NULL,
  `movement_type` enum('receive','put_away','return_in','adjustment_in','transfer_in','pick','ship','distribution','adjustment_out','transfer_out','damage','expire','dispose','transfer','count','adjust') COLLATE utf8mb4_unicode_ci NOT NULL,
  `from_location_id` bigint(20) UNSIGNED DEFAULT NULL,
  `to_location_id` bigint(20) UNSIGNED DEFAULT NULL,
  `quantity` decimal(10,3) NOT NULL COMMENT 'จำนวนในหน่วยพื้นฐาน',
  `unit_id` bigint(20) UNSIGNED DEFAULT NULL,
  `reference_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'ประเภทเอกสารอ้างอิง',
  `reference_id` bigint(20) UNSIGNED DEFAULT NULL COMMENT 'ID เอกสารอ้างอิง',
  `reference_number` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'เลขที่เอกสารอ้างอิง',
  `performed_by` bigint(20) UNSIGNED NOT NULL,
  `performed_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'วันเวลาที่ทำรายการ',
  `notes` text COLLATE utf8mb4_unicode_ci COMMENT 'หมายเหตุ'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `stock_transfers`
--

CREATE TABLE `stock_transfers` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `transfer_number` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `product_id` bigint(20) UNSIGNED NOT NULL,
  `batch_id` bigint(20) UNSIGNED DEFAULT NULL,
  `from_location_id` bigint(20) UNSIGNED NOT NULL,
  `to_location_id` bigint(20) UNSIGNED NOT NULL,
  `quantity` decimal(15,4) NOT NULL,
  `unit_id` bigint(20) UNSIGNED NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending',
  `priority` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'normal',
  `reason` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `notes` text COLLATE utf8mb4_unicode_ci,
  `rejection_reason` text COLLATE utf8mb4_unicode_ci,
  `cancellation_reason` text COLLATE utf8mb4_unicode_ci,
  `requested_by` bigint(20) UNSIGNED NOT NULL,
  `approved_by` bigint(20) UNSIGNED DEFAULT NULL,
  `executed_by` bigint(20) UNSIGNED DEFAULT NULL,
  `cancelled_by` bigint(20) UNSIGNED DEFAULT NULL,
  `approved_at` timestamp NULL DEFAULT NULL,
  `executed_at` timestamp NULL DEFAULT NULL,
  `cancelled_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `storage_locations`
--

CREATE TABLE `storage_locations` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `zone_id` bigint(20) UNSIGNED NOT NULL,
  `location_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'รหัสตำแหน่ง (เช่น A-01-05)',
  `rack` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'ชั้นวาง',
  `row_number` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'แถว',
  `shelf_number` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'ชั้น',
  `max_capacity` int(11) NOT NULL DEFAULT '1' COMMENT 'ความจุสูงสุด (SKU)',
  `current_capacity` int(11) NOT NULL DEFAULT '0' COMMENT 'จำนวน SKU ที่เก็บอยู่',
  `is_available` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'สถานะว่าง',
  `location_type` enum('shelf','floor','bin','pallet') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'shelf' COMMENT 'ประเภทตำแหน่ง: shelf=ชั้นวาง, floor=พื้น, bin=กล่อง, pallet=พาเลท',
  `notes` text COLLATE utf8mb4_unicode_ci COMMENT 'หมายเหตุ',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `suppliers`
--

CREATE TABLE `suppliers` (
  `id` bigint(20) UNSIGNED NOT NULL,
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
  `deleted_by` bigint(20) UNSIGNED DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `suppliers_bk`
--

CREATE TABLE `suppliers_bk` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `supplier_code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'รหัสซัพพลายเออร์',
  `supplier_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'ชื่อซัพพลายเออร์',
  `contact_person` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'ผู้ติดต่อ',
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'เบอร์โทรศัพท์',
  `email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'อีเมล',
  `address` text COLLATE utf8mb4_unicode_ci COMMENT 'ที่อยู่',
  `province` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'จังหวัด',
  `district` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'อำเภอ',
  `postal_code` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'รหัสไปรษณีย์',
  `tax_id` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'เลขประจำตัวผู้เสียภาษี',
  `payment_terms` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'เงื่อนไขการชำระเงิน',
  `is_active` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'สถานะการใช้งาน',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `deleted_at` timestamp NULL DEFAULT NULL,
  `deleted_by` bigint(20) UNSIGNED DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `units`
--

CREATE TABLE `units` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `unit_code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'รหัสหน่วย',
  `unit_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'ชื่อหน่วย',
  `unit_type` enum('base','packaging') COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'ประเภทหน่วย: base=พื้นฐาน, packaging=บรรจุภัณฑ์',
  `description` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'คำอธิบาย',
  `is_active` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'สถานะการใช้งาน',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `units_bk`
--

CREATE TABLE `units_bk` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `unit_code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'รหัสหน่วย',
  `unit_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'ชื่อหน่วย',
  `unit_type` enum('base','packaging') COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'ประเภทหน่วย: base=พื้นฐาน, packaging=บรรจุภัณฑ์',
  `description` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'คำอธิบาย',
  `is_active` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'สถานะการใช้งาน',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'ชื่อผู้ใช้',
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `first_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'ชื่อจริง',
  `last_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'นามสกุล',
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'เบอร์โทรศัพท์',
  `role` enum('admin','warehouse_manager','warehouse_staff','purchaser','viewer','branch_manager','branch_staff') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'viewer' COMMENT 'บทบาท',
  `branch_id` bigint(20) UNSIGNED DEFAULT NULL COMMENT 'สาขา (null = คลังกลาง)',
  `is_active` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'สถานะการใช้งาน',
  `email_verified_at` timestamp NULL DEFAULT NULL,
  `password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `remember_token` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `last_login_at` timestamp NULL DEFAULT NULL COMMENT 'เข้าสู่ระบบล่าสุด',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `warehouse_zones`
--

CREATE TABLE `warehouse_zones` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `zone_code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'รหัสโซน',
  `zone_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'ชื่อโซน',
  `zone_type` enum('normal','cold','refrigerated','controlled') COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'ประเภทโซน: normal=ปกติ, cold=เย็น, refrigerated=แช่เย็น, controlled=ควบคุมพิเศษ',
  `temperature_min` decimal(5,2) DEFAULT NULL COMMENT 'อุณหภูมิต่ำสุด (°C)',
  `temperature_max` decimal(5,2) DEFAULT NULL COMMENT 'อุณหภูมิสูงสุด (°C)',
  `current_temperature` decimal(5,2) DEFAULT NULL COMMENT 'อุณหภูมิปัจจุบัน (°C)',
  `capacity` int(11) DEFAULT NULL COMMENT 'ความจุสูงสุด (ตำแหน่ง)',
  `description` text COLLATE utf8mb4_unicode_ci COMMENT 'คำอธิบาย',
  `is_active` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'สถานะการใช้งาน',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `alerts`
--
ALTER TABLE `alerts`
  ADD PRIMARY KEY (`id`),
  ADD KEY `alerts_assigned_to_foreign` (`assigned_to`),
  ADD KEY `alerts_resolved_by_foreign` (`resolved_by`),
  ADD KEY `alerts_alert_type_index` (`alert_type`),
  ADD KEY `alerts_severity_index` (`severity`),
  ADD KEY `alerts_is_read_index` (`is_read`),
  ADD KEY `alerts_is_resolved_index` (`is_resolved`),
  ADD KEY `alerts_product_id_index` (`product_id`),
  ADD KEY `alerts_batch_id_index` (`batch_id`),
  ADD KEY `alerts_related_type_related_id_index` (`related_type`,`related_id`),
  ADD KEY `alerts_alert_type_is_resolved_index` (`alert_type`,`is_resolved`),
  ADD KEY `alerts_severity_is_read_index` (`severity`,`is_read`),
  ADD KEY `alerts_alert_date_index` (`alert_date`),
  ADD KEY `alerts_branch_id_index` (`branch_id`);

--
-- Indexes for table `branches`
--
ALTER TABLE `branches`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `branches_branch_code_unique` (`branch_code`),
  ADD KEY `branches_branch_code_index` (`branch_code`),
  ADD KEY `branches_branch_type_index` (`branch_type`),
  ADD KEY `branches_company_id_index` (`company_id`);

--
-- Indexes for table `branch_adjustments`
--
ALTER TABLE `branch_adjustments`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `branch_adjustments_adjustment_number_unique` (`adjustment_number`),
  ADD KEY `branch_adjustments_created_by_foreign` (`created_by`),
  ADD KEY `branch_adjustments_branch_id_index` (`branch_id`),
  ADD KEY `branch_adjustments_adjustment_type_index` (`adjustment_type`),
  ADD KEY `branch_adjustments_created_at_index` (`created_at`);

--
-- Indexes for table `branch_inventory`
--
ALTER TABLE `branch_inventory`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `branch_product_batch_unique` (`branch_id`,`product_id`,`batch_id`),
  ADD KEY `branch_inventory_last_count_by_foreign` (`last_count_by`),
  ADD KEY `branch_inventory_branch_id_index` (`branch_id`),
  ADD KEY `branch_inventory_product_id_index` (`product_id`),
  ADD KEY `branch_inventory_batch_id_index` (`batch_id`),
  ADD KEY `branch_inventory_last_count_date_index` (`last_count_date`);

--
-- Indexes for table `branch_product_settings`
--
ALTER TABLE `branch_product_settings`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `branch_product_settings_unique` (`branch_id`,`product_id`),
  ADD KEY `branch_product_settings_branch_id_index` (`branch_id`),
  ADD KEY `branch_product_settings_product_id_index` (`product_id`),
  ADD KEY `branch_product_settings_is_active_index` (`is_active`);

--
-- Indexes for table `branch_receiving`
--
ALTER TABLE `branch_receiving`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `branch_receiving_receiving_number_unique` (`receiving_number`),
  ADD KEY `branch_receiving_received_by_foreign` (`received_by`),
  ADD KEY `branch_receiving_distribution_order_id_index` (`distribution_order_id`),
  ADD KEY `branch_receiving_branch_id_index` (`branch_id`),
  ADD KEY `branch_receiving_status_index` (`status`);

--
-- Indexes for table `branch_receiving_items`
--
ALTER TABLE `branch_receiving_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `branch_receiving_items_distribution_order_item_id_foreign` (`distribution_order_item_id`),
  ADD KEY `branch_receiving_items_product_batch_id_foreign` (`product_batch_id`),
  ADD KEY `branch_receiving_items_branch_receiving_id_index` (`branch_receiving_id`),
  ADD KEY `branch_receiving_items_product_id_index` (`product_id`),
  ADD KEY `branch_receiving_items_status_index` (`status`);

--
-- Indexes for table `branch_requests`
--
ALTER TABLE `branch_requests`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `branch_requests_request_number_unique` (`request_number`),
  ADD KEY `branch_requests_requested_by_foreign` (`requested_by`),
  ADD KEY `branch_requests_reviewed_by_foreign` (`reviewed_by`),
  ADD KEY `branch_requests_request_number_index` (`request_number`),
  ADD KEY `branch_requests_branch_id_index` (`branch_id`),
  ADD KEY `branch_requests_status_index` (`status`),
  ADD KEY `branch_requests_branch_id_status_index` (`branch_id`,`status`),
  ADD KEY `branch_requests_status_submitted_at_index` (`status`,`submitted_at`),
  ADD KEY `branch_requests_do_id_index` (`do_id`),
  ADD KEY `branch_requests_parent_request_id_index` (`parent_request_id`);

--
-- Indexes for table `branch_request_items`
--
ALTER TABLE `branch_request_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `branch_request_items_unit_id_foreign` (`unit_id`),
  ADD KEY `branch_request_items_request_id_index` (`request_id`),
  ADD KEY `branch_request_items_product_id_index` (`product_id`),
  ADD KEY `branch_request_items_request_id_product_id_index` (`request_id`,`product_id`);

--
-- Indexes for table `branch_returns`
--
ALTER TABLE `branch_returns`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `branch_returns_return_number_unique` (`return_number`),
  ADD KEY `branch_returns_branch_receiving_item_id_foreign` (`branch_receiving_item_id`),
  ADD KEY `branch_returns_product_batch_id_foreign` (`product_batch_id`),
  ADD KEY `branch_returns_processed_by_foreign` (`processed_by`),
  ADD KEY `branch_returns_returned_to_location_id_foreign` (`returned_to_location_id`),
  ADD KEY `branch_returns_branch_id_index` (`branch_id`),
  ADD KEY `branch_returns_status_index` (`status`),
  ADD KEY `branch_returns_product_id_index` (`product_id`),
  ADD KEY `branch_returns_unit_id_foreign` (`unit_id`),
  ADD KEY `branch_returns_distribution_order_id_foreign` (`distribution_order_id`);

--
-- Indexes for table `branch_stock_counts`
--
ALTER TABLE `branch_stock_counts`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `branch_stock_counts_count_number_unique` (`count_number`),
  ADD KEY `branch_stock_counts_created_by_foreign` (`created_by`),
  ADD KEY `branch_stock_counts_submitted_by_foreign` (`submitted_by`),
  ADD KEY `branch_stock_counts_approved_by_foreign` (`approved_by`),
  ADD KEY `branch_stock_counts_branch_id_index` (`branch_id`),
  ADD KEY `branch_stock_counts_count_date_index` (`count_date`),
  ADD KEY `branch_stock_counts_status_index` (`status`),
  ADD KEY `branch_stock_counts_created_at_index` (`created_at`),
  ADD KEY `fk_bsc_counted_by` (`counted_by`);

--
-- Indexes for table `branch_stock_count_items`
--
ALTER TABLE `branch_stock_count_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `branch_stock_count_items_stock_count_id_index` (`stock_count_id`),
  ADD KEY `branch_stock_count_items_product_id_index` (`product_id`),
  ADD KEY `branch_stock_count_items_batch_id_index` (`batch_id`);

--
-- Indexes for table `branch_stock_movements`
--
ALTER TABLE `branch_stock_movements`
  ADD PRIMARY KEY (`id`),
  ADD KEY `branch_stock_movements_created_by_foreign` (`created_by`),
  ADD KEY `branch_stock_movements_branch_id_index` (`branch_id`),
  ADD KEY `branch_stock_movements_product_id_index` (`product_id`),
  ADD KEY `branch_stock_movements_batch_id_index` (`batch_id`),
  ADD KEY `branch_stock_movements_movement_type_index` (`movement_type`),
  ADD KEY `branch_stock_movements_created_at_index` (`created_at`),
  ADD KEY `branch_stock_movements_reference_type_reference_id_index` (`reference_type`,`reference_id`);

--
-- Indexes for table `branch_transfers`
--
ALTER TABLE `branch_transfers`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `branch_transfers_transfer_number_unique` (`transfer_number`),
  ADD KEY `branch_transfers_requested_by_foreign` (`requested_by`),
  ADD KEY `branch_transfers_shipped_by_foreign` (`shipped_by`),
  ADD KEY `branch_transfers_received_by_foreign` (`received_by`),
  ADD KEY `branch_transfers_from_branch_id_index` (`from_branch_id`),
  ADD KEY `branch_transfers_to_branch_id_index` (`to_branch_id`),
  ADD KEY `branch_transfers_status_index` (`status`);

--
-- Indexes for table `branch_transfer_items`
--
ALTER TABLE `branch_transfer_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `branch_transfer_items_product_batch_id_foreign` (`product_batch_id`),
  ADD KEY `branch_transfer_items_branch_transfer_id_index` (`branch_transfer_id`),
  ADD KEY `branch_transfer_items_product_id_index` (`product_id`);

--
-- Indexes for table `cache`
--
ALTER TABLE `cache`
  ADD PRIMARY KEY (`key`);

--
-- Indexes for table `cache_locks`
--
ALTER TABLE `cache_locks`
  ADD PRIMARY KEY (`key`);

--
-- Indexes for table `categories`
--
ALTER TABLE `categories`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `categories_code_unique` (`code`),
  ADD KEY `categories_parent_id_index` (`parent_id`),
  ADD KEY `categories_is_active_index` (`is_active`),
  ADD KEY `categories_sort_order_index` (`sort_order`);

--
-- Indexes for table `companies`
--
ALTER TABLE `companies`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `companies_tax_id_branch_tax_no_unique` (`tax_id`,`branch_tax_no`),
  ADD UNIQUE KEY `companies_code_unique` (`code`),
  ADD KEY `companies_code_index` (`code`),
  ADD KEY `companies_is_active_index` (`is_active`);

--
-- Indexes for table `distribution_orders`
--
ALTER TABLE `distribution_orders`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `distribution_orders_do_number_unique` (`do_number`),
  ADD KEY `distribution_orders_created_by_foreign` (`created_by`),
  ADD KEY `distribution_orders_picked_by_foreign` (`picked_by`),
  ADD KEY `distribution_orders_packed_by_foreign` (`packed_by`),
  ADD KEY `distribution_orders_shipped_by_foreign` (`shipped_by`),
  ADD KEY `distribution_orders_do_number_index` (`do_number`),
  ADD KEY `distribution_orders_branch_id_index` (`branch_id`),
  ADD KEY `distribution_orders_status_index` (`status`),
  ADD KEY `distribution_orders_order_date_index` (`order_date`),
  ADD KEY `distribution_orders_branch_id_status_index` (`branch_id`,`status`),
  ADD KEY `distribution_orders_status_required_date_index` (`status`,`required_date`),
  ADD KEY `distribution_orders_request_id_index` (`request_id`);

--
-- Indexes for table `distribution_order_items`
--
ALTER TABLE `distribution_order_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `distribution_order_items_unit_id_foreign` (`unit_id`),
  ADD KEY `distribution_order_items_picked_by_foreign` (`picked_by`),
  ADD KEY `distribution_order_items_do_id_index` (`do_id`),
  ADD KEY `distribution_order_items_product_id_index` (`product_id`),
  ADD KEY `distribution_order_items_batch_id_index` (`batch_id`),
  ADD KEY `distribution_order_items_do_id_product_id_index` (`do_id`,`product_id`),
  ADD KEY `distribution_order_items_pick_location_id_index` (`pick_location_id`);

--
-- Indexes for table `distribution_order_picks`
--
ALTER TABLE `distribution_order_picks`
  ADD PRIMARY KEY (`id`),
  ADD KEY `distribution_order_picks_picked_by_foreign` (`picked_by`),
  ADD KEY `distribution_order_picks_do_item_id_index` (`do_item_id`),
  ADD KEY `distribution_order_picks_batch_id_index` (`batch_id`),
  ADD KEY `distribution_order_picks_location_id_index` (`location_id`),
  ADD KEY `distribution_order_picks_do_item_id_batch_id_location_id_index` (`do_item_id`,`batch_id`,`location_id`);

--
-- Indexes for table `failed_jobs`
--
ALTER TABLE `failed_jobs`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `failed_jobs_uuid_unique` (`uuid`);

--
-- Indexes for table `goods_receipts`
--
ALTER TABLE `goods_receipts`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `goods_receipts_gr_number_unique` (`gr_number`),
  ADD KEY `goods_receipts_received_by_foreign` (`received_by`),
  ADD KEY `goods_receipts_gr_number_index` (`gr_number`),
  ADD KEY `goods_receipts_po_id_index` (`po_id`),
  ADD KEY `goods_receipts_receipt_date_index` (`receipt_date`),
  ADD KEY `goods_receipts_status_index` (`status`),
  ADD KEY `goods_receipts_verified_by_foreign` (`verified_by`),
  ADD KEY `goods_receipts_supplier_id_foreign` (`supplier_id`);

--
-- Indexes for table `goods_receipt_items`
--
ALTER TABLE `goods_receipt_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `goods_receipt_items_unit_id_foreign` (`unit_id`),
  ADD KEY `goods_receipt_items_location_id_foreign` (`location_id`),
  ADD KEY `goods_receipt_items_gr_id_index` (`gr_id`),
  ADD KEY `goods_receipt_items_po_item_id_index` (`po_item_id`),
  ADD KEY `goods_receipt_items_product_id_index` (`product_id`),
  ADD KEY `goods_receipt_items_batch_id_index` (`batch_id`),
  ADD KEY `goods_receipt_items_gr_id_product_id_index` (`gr_id`,`product_id`),
  ADD KEY `goods_receipt_items_inspected_by_foreign` (`inspected_by`);

--
-- Indexes for table `inventory`
--
ALTER TABLE `inventory`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_inventory` (`product_id`,`batch_id`,`location_id`),
  ADD KEY `inventory_last_count_by_foreign` (`last_count_by`),
  ADD KEY `inventory_product_id_index` (`product_id`),
  ADD KEY `inventory_batch_id_index` (`batch_id`),
  ADD KEY `inventory_location_id_index` (`location_id`),
  ADD KEY `inventory_product_id_batch_id_index` (`product_id`,`batch_id`),
  ADD KEY `inventory_created_by_foreign` (`created_by`),
  ADD KEY `inventory_updated_by_foreign` (`updated_by`);

--
-- Indexes for table `jobs`
--
ALTER TABLE `jobs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `jobs_queue_index` (`queue`);

--
-- Indexes for table `job_batches`
--
ALTER TABLE `job_batches`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `migrations`
--
ALTER TABLE `migrations`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `mst_vendor`
--
ALTER TABLE `mst_vendor`
  ADD PRIMARY KEY (`ccust`),
  ADD KEY `cdisc` (`cdisc`),
  ADD KEY `csal` (`csal`),
  ADD KEY `csal1` (`csal1`),
  ADD KEY `csal2` (`csal2`),
  ADD KEY `csal3` (`csal3`),
  ADD KEY `csal4` (`csal4`),
  ADD KEY `csal5` (`csal5`),
  ADD KEY `cref01` (`cref01`),
  ADD KEY `ccust` (`ccust`);

--
-- Indexes for table `password_reset_tokens`
--
ALTER TABLE `password_reset_tokens`
  ADD PRIMARY KEY (`email`);

--
-- Indexes for table `personal_access_tokens`
--
ALTER TABLE `personal_access_tokens`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `personal_access_tokens_token_unique` (`token`),
  ADD KEY `personal_access_tokens_tokenable_type_tokenable_id_index` (`tokenable_type`,`tokenable_id`),
  ADD KEY `personal_access_tokens_expires_at_index` (`expires_at`);

--
-- Indexes for table `products`
--
ALTER TABLE `products`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `products_sku_unique` (`sku`),
  ADD KEY `products_sku_index` (`sku`),
  ADD KEY `products_barcode_index` (`barcode`),
  ADD KEY `products_category_index` (`category`),
  ADD KEY `products_base_unit_id_index` (`base_unit_id`),
  ADD KEY `products_category_is_active_index` (`category`,`is_active`),
  ADD KEY `products_deleted_by_foreign` (`deleted_by`),
  ADD KEY `products_created_by_index` (`created_by`),
  ADD KEY `products_updated_by_index` (`updated_by`),
  ADD KEY `products_category_id_index` (`category_id`),
  ADD KEY `products_code_org_index` (`code_org`);

--
-- Indexes for table `products_bk`
--
ALTER TABLE `products_bk`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `products_sku_unique` (`sku`),
  ADD KEY `products_sku_index` (`sku`),
  ADD KEY `products_barcode_index` (`barcode`),
  ADD KEY `products_category_index` (`category`),
  ADD KEY `products_base_unit_id_index` (`base_unit_id`),
  ADD KEY `products_category_is_active_index` (`category`,`is_active`),
  ADD KEY `products_deleted_by_foreign` (`deleted_by`),
  ADD KEY `products_created_by_index` (`created_by`),
  ADD KEY `products_updated_by_index` (`updated_by`),
  ADD KEY `products_category_id_index` (`category_id`);

--
-- Indexes for table `product_batches`
--
ALTER TABLE `product_batches`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_product_batch` (`product_id`,`batch_number`),
  ADD KEY `product_batches_supplier_id_foreign` (`supplier_id`),
  ADD KEY `product_batches_received_unit_id_foreign` (`received_unit_id`),
  ADD KEY `product_batches_approved_by_foreign` (`approved_by`),
  ADD KEY `product_batches_product_id_index` (`product_id`),
  ADD KEY `product_batches_batch_number_index` (`batch_number`),
  ADD KEY `product_batches_expiry_date_index` (`expiry_date`),
  ADD KEY `product_batches_status_index` (`status`),
  ADD KEY `product_batches_product_id_status_expiry_date_index` (`product_id`,`status`,`expiry_date`),
  ADD KEY `product_batches_created_by_foreign` (`created_by`);

--
-- Indexes for table `product_unit_conversions`
--
ALTER TABLE `product_unit_conversions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `product_unit_conversions_product_id_unique` (`product_id`),
  ADD KEY `product_unit_conversions_base_unit_id_foreign` (`base_unit_id`),
  ADD KEY `product_unit_conversions_purchase_unit_id_foreign` (`purchase_unit_id`),
  ADD KEY `product_unit_conversions_distribution_unit_id_foreign` (`distribution_unit_id`),
  ADD KEY `product_unit_conversions_sales_unit_id_foreign` (`sales_unit_id`),
  ADD KEY `product_unit_conversions_product_id_is_active_index` (`product_id`,`is_active`);

--
-- Indexes for table `product_unit_conversions_bk`
--
ALTER TABLE `product_unit_conversions_bk`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `product_unit_conversions_product_id_unique` (`product_id`),
  ADD KEY `product_unit_conversions_base_unit_id_foreign` (`base_unit_id`),
  ADD KEY `product_unit_conversions_purchase_unit_id_foreign` (`purchase_unit_id`),
  ADD KEY `product_unit_conversions_distribution_unit_id_foreign` (`distribution_unit_id`),
  ADD KEY `product_unit_conversions_sales_unit_id_foreign` (`sales_unit_id`),
  ADD KEY `product_unit_conversions_product_id_is_active_index` (`product_id`,`is_active`);

--
-- Indexes for table `purchase_orders`
--
ALTER TABLE `purchase_orders`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `purchase_orders_po_number_unique` (`po_number`),
  ADD KEY `purchase_orders_created_by_foreign` (`created_by`),
  ADD KEY `purchase_orders_approved_by_foreign` (`approved_by`),
  ADD KEY `purchase_orders_po_number_index` (`po_number`),
  ADD KEY `purchase_orders_supplier_id_index` (`supplier_id`),
  ADD KEY `purchase_orders_status_index` (`status`),
  ADD KEY `purchase_orders_order_date_index` (`order_date`),
  ADD KEY `purchase_orders_supplier_id_status_index` (`supplier_id`,`status`);

--
-- Indexes for table `purchase_order_items`
--
ALTER TABLE `purchase_order_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `purchase_order_items_unit_id_foreign` (`unit_id`),
  ADD KEY `purchase_order_items_po_id_index` (`po_id`),
  ADD KEY `purchase_order_items_product_id_index` (`product_id`),
  ADD KEY `purchase_order_items_po_id_product_id_index` (`po_id`,`product_id`);

--
-- Indexes for table `sessions`
--
ALTER TABLE `sessions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `sessions_user_id_index` (`user_id`),
  ADD KEY `sessions_last_activity_index` (`last_activity`);

--
-- Indexes for table `stock_adjustments`
--
ALTER TABLE `stock_adjustments`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `stock_adjustments_adjustment_number_unique` (`adjustment_number`),
  ADD KEY `stock_adjustments_created_by_foreign` (`created_by`),
  ADD KEY `stock_adjustments_approved_by_foreign` (`approved_by`),
  ADD KEY `stock_adjustments_adjustment_number_index` (`adjustment_number`),
  ADD KEY `stock_adjustments_adjustment_type_index` (`adjustment_type`),
  ADD KEY `stock_adjustments_adjustment_date_index` (`adjustment_date`),
  ADD KEY `stock_adjustments_status_adjustment_date_index` (`adjustment_date`),
  ADD KEY `stock_adjustments_status_index` (`status`),
  ADD KEY `stock_adjustments_cancelled_by_foreign` (`cancelled_by`);

--
-- Indexes for table `stock_adjustment_items`
--
ALTER TABLE `stock_adjustment_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `stock_adjustment_items_unit_id_foreign` (`unit_id`),
  ADD KEY `stock_adjustment_items_adjustment_id_index` (`adjustment_id`),
  ADD KEY `stock_adjustment_items_product_id_index` (`product_id`),
  ADD KEY `stock_adjustment_items_batch_id_index` (`batch_id`),
  ADD KEY `stock_adjustment_items_location_id_index` (`location_id`),
  ADD KEY `stock_adjustment_items_adjustment_id_product_id_index` (`adjustment_id`,`product_id`);

--
-- Indexes for table `stock_movements`
--
ALTER TABLE `stock_movements`
  ADD PRIMARY KEY (`id`),
  ADD KEY `stock_movements_from_location_id_foreign` (`from_location_id`),
  ADD KEY `stock_movements_to_location_id_foreign` (`to_location_id`),
  ADD KEY `stock_movements_unit_id_foreign` (`unit_id`),
  ADD KEY `stock_movements_performed_by_foreign` (`performed_by`),
  ADD KEY `stock_movements_product_id_index` (`product_id`),
  ADD KEY `stock_movements_batch_id_index` (`batch_id`),
  ADD KEY `stock_movements_movement_type_index` (`movement_type`),
  ADD KEY `stock_movements_performed_at_index` (`performed_at`),
  ADD KEY `stock_movements_reference_type_reference_id_index` (`reference_type`,`reference_id`),
  ADD KEY `stock_movements_product_id_performed_at_index` (`product_id`,`performed_at`);

--
-- Indexes for table `stock_transfers`
--
ALTER TABLE `stock_transfers`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `stock_transfers_transfer_number_unique` (`transfer_number`),
  ADD KEY `stock_transfers_batch_id_foreign` (`batch_id`),
  ADD KEY `stock_transfers_unit_id_foreign` (`unit_id`),
  ADD KEY `stock_transfers_approved_by_foreign` (`approved_by`),
  ADD KEY `stock_transfers_executed_by_foreign` (`executed_by`),
  ADD KEY `stock_transfers_cancelled_by_foreign` (`cancelled_by`),
  ADD KEY `stock_transfers_status_index` (`status`),
  ADD KEY `stock_transfers_priority_index` (`priority`),
  ADD KEY `stock_transfers_from_location_id_index` (`from_location_id`),
  ADD KEY `stock_transfers_to_location_id_index` (`to_location_id`),
  ADD KEY `stock_transfers_product_id_index` (`product_id`),
  ADD KEY `stock_transfers_requested_by_index` (`requested_by`),
  ADD KEY `stock_transfers_created_at_index` (`created_at`);

--
-- Indexes for table `storage_locations`
--
ALTER TABLE `storage_locations`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `storage_locations_location_code_unique` (`location_code`),
  ADD KEY `storage_locations_zone_id_index` (`zone_id`),
  ADD KEY `storage_locations_location_code_index` (`location_code`),
  ADD KEY `storage_locations_is_available_zone_id_index` (`is_available`,`zone_id`);

--
-- Indexes for table `suppliers`
--
ALTER TABLE `suppliers`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `suppliers_supplier_code_unique` (`supplier_code`),
  ADD KEY `suppliers_supplier_code_index` (`supplier_code`),
  ADD KEY `suppliers_supplier_name_index` (`supplier_name`),
  ADD KEY `suppliers_deleted_by_foreign` (`deleted_by`);

--
-- Indexes for table `suppliers_bk`
--
ALTER TABLE `suppliers_bk`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `suppliers_supplier_code_unique` (`supplier_code`),
  ADD KEY `suppliers_supplier_code_index` (`supplier_code`),
  ADD KEY `suppliers_supplier_name_index` (`supplier_name`),
  ADD KEY `suppliers_deleted_by_foreign` (`deleted_by`);

--
-- Indexes for table `units`
--
ALTER TABLE `units`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `units_unit_code_unique` (`unit_code`),
  ADD KEY `units_unit_code_index` (`unit_code`),
  ADD KEY `units_unit_type_index` (`unit_type`);

--
-- Indexes for table `units_bk`
--
ALTER TABLE `units_bk`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `units_unit_code_unique` (`unit_code`),
  ADD KEY `units_unit_code_index` (`unit_code`),
  ADD KEY `units_unit_type_index` (`unit_type`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `users_email_unique` (`email`),
  ADD UNIQUE KEY `users_username_unique` (`username`),
  ADD KEY `users_username_index` (`username`),
  ADD KEY `users_role_index` (`role`),
  ADD KEY `users_is_active_index` (`is_active`),
  ADD KEY `users_branch_id_index` (`branch_id`);

--
-- Indexes for table `warehouse_zones`
--
ALTER TABLE `warehouse_zones`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `warehouse_zones_zone_code_unique` (`zone_code`),
  ADD KEY `warehouse_zones_zone_code_index` (`zone_code`),
  ADD KEY `warehouse_zones_zone_type_index` (`zone_type`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `alerts`
--
ALTER TABLE `alerts`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `branches`
--
ALTER TABLE `branches`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `branch_adjustments`
--
ALTER TABLE `branch_adjustments`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `branch_inventory`
--
ALTER TABLE `branch_inventory`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `branch_product_settings`
--
ALTER TABLE `branch_product_settings`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `branch_receiving`
--
ALTER TABLE `branch_receiving`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `branch_receiving_items`
--
ALTER TABLE `branch_receiving_items`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `branch_requests`
--
ALTER TABLE `branch_requests`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `branch_request_items`
--
ALTER TABLE `branch_request_items`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `branch_returns`
--
ALTER TABLE `branch_returns`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `branch_stock_counts`
--
ALTER TABLE `branch_stock_counts`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `branch_stock_count_items`
--
ALTER TABLE `branch_stock_count_items`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `branch_stock_movements`
--
ALTER TABLE `branch_stock_movements`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `branch_transfers`
--
ALTER TABLE `branch_transfers`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `branch_transfer_items`
--
ALTER TABLE `branch_transfer_items`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `categories`
--
ALTER TABLE `categories`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `companies`
--
ALTER TABLE `companies`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `distribution_orders`
--
ALTER TABLE `distribution_orders`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `distribution_order_items`
--
ALTER TABLE `distribution_order_items`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `distribution_order_picks`
--
ALTER TABLE `distribution_order_picks`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `failed_jobs`
--
ALTER TABLE `failed_jobs`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `goods_receipts`
--
ALTER TABLE `goods_receipts`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `goods_receipt_items`
--
ALTER TABLE `goods_receipt_items`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `inventory`
--
ALTER TABLE `inventory`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `jobs`
--
ALTER TABLE `jobs`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `migrations`
--
ALTER TABLE `migrations`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `personal_access_tokens`
--
ALTER TABLE `personal_access_tokens`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `products`
--
ALTER TABLE `products`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `products_bk`
--
ALTER TABLE `products_bk`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `product_batches`
--
ALTER TABLE `product_batches`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `product_unit_conversions`
--
ALTER TABLE `product_unit_conversions`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `product_unit_conversions_bk`
--
ALTER TABLE `product_unit_conversions_bk`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `purchase_orders`
--
ALTER TABLE `purchase_orders`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `purchase_order_items`
--
ALTER TABLE `purchase_order_items`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `stock_adjustments`
--
ALTER TABLE `stock_adjustments`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `stock_adjustment_items`
--
ALTER TABLE `stock_adjustment_items`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `stock_movements`
--
ALTER TABLE `stock_movements`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `stock_transfers`
--
ALTER TABLE `stock_transfers`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `storage_locations`
--
ALTER TABLE `storage_locations`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `suppliers`
--
ALTER TABLE `suppliers`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `suppliers_bk`
--
ALTER TABLE `suppliers_bk`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `units`
--
ALTER TABLE `units`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `units_bk`
--
ALTER TABLE `units_bk`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `warehouse_zones`
--
ALTER TABLE `warehouse_zones`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `alerts`
--
ALTER TABLE `alerts`
  ADD CONSTRAINT `alerts_assigned_to_foreign` FOREIGN KEY (`assigned_to`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `alerts_batch_id_foreign` FOREIGN KEY (`batch_id`) REFERENCES `product_batches` (`id`),
  ADD CONSTRAINT `alerts_branch_id_foreign` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `alerts_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  ADD CONSTRAINT `alerts_resolved_by_foreign` FOREIGN KEY (`resolved_by`) REFERENCES `users` (`id`);

--
-- Constraints for table `branches`
--
ALTER TABLE `branches`
  ADD CONSTRAINT `branches_company_id_foreign` FOREIGN KEY (`company_id`) REFERENCES `companies` (`id`);

--
-- Constraints for table `branch_adjustments`
--
ALTER TABLE `branch_adjustments`
  ADD CONSTRAINT `branch_adjustments_branch_id_foreign` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `branch_adjustments_created_by_foreign` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`);

--
-- Constraints for table `branch_inventory`
--
ALTER TABLE `branch_inventory`
  ADD CONSTRAINT `branch_inventory_batch_id_foreign` FOREIGN KEY (`batch_id`) REFERENCES `product_batches` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `branch_inventory_branch_id_foreign` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `branch_inventory_last_count_by_foreign` FOREIGN KEY (`last_count_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `branch_inventory_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `branch_product_settings`
--
ALTER TABLE `branch_product_settings`
  ADD CONSTRAINT `branch_product_settings_branch_id_foreign` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `branch_product_settings_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `branch_receiving`
--
ALTER TABLE `branch_receiving`
  ADD CONSTRAINT `branch_receiving_branch_id_foreign` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`id`),
  ADD CONSTRAINT `branch_receiving_distribution_order_id_foreign` FOREIGN KEY (`distribution_order_id`) REFERENCES `distribution_orders` (`id`),
  ADD CONSTRAINT `branch_receiving_received_by_foreign` FOREIGN KEY (`received_by`) REFERENCES `users` (`id`);

--
-- Constraints for table `branch_receiving_items`
--
ALTER TABLE `branch_receiving_items`
  ADD CONSTRAINT `branch_receiving_items_branch_receiving_id_foreign` FOREIGN KEY (`branch_receiving_id`) REFERENCES `branch_receiving` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `branch_receiving_items_distribution_order_item_id_foreign` FOREIGN KEY (`distribution_order_item_id`) REFERENCES `distribution_order_items` (`id`),
  ADD CONSTRAINT `branch_receiving_items_product_batch_id_foreign` FOREIGN KEY (`product_batch_id`) REFERENCES `product_batches` (`id`),
  ADD CONSTRAINT `branch_receiving_items_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`);

--
-- Constraints for table `branch_requests`
--
ALTER TABLE `branch_requests`
  ADD CONSTRAINT `branch_requests_branch_id_foreign` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`id`),
  ADD CONSTRAINT `branch_requests_do_id_foreign` FOREIGN KEY (`do_id`) REFERENCES `distribution_orders` (`id`),
  ADD CONSTRAINT `branch_requests_parent_request_id_foreign` FOREIGN KEY (`parent_request_id`) REFERENCES `branch_requests` (`id`),
  ADD CONSTRAINT `branch_requests_requested_by_foreign` FOREIGN KEY (`requested_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `branch_requests_reviewed_by_foreign` FOREIGN KEY (`reviewed_by`) REFERENCES `users` (`id`);

--
-- Constraints for table `branch_request_items`
--
ALTER TABLE `branch_request_items`
  ADD CONSTRAINT `branch_request_items_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  ADD CONSTRAINT `branch_request_items_request_id_foreign` FOREIGN KEY (`request_id`) REFERENCES `branch_requests` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `branch_request_items_unit_id_foreign` FOREIGN KEY (`unit_id`) REFERENCES `units` (`id`);

--
-- Constraints for table `branch_returns`
--
ALTER TABLE `branch_returns`
  ADD CONSTRAINT `branch_returns_branch_id_foreign` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`id`),
  ADD CONSTRAINT `branch_returns_branch_receiving_item_id_foreign` FOREIGN KEY (`branch_receiving_item_id`) REFERENCES `branch_receiving_items` (`id`),
  ADD CONSTRAINT `branch_returns_distribution_order_id_foreign` FOREIGN KEY (`distribution_order_id`) REFERENCES `distribution_orders` (`id`),
  ADD CONSTRAINT `branch_returns_processed_by_foreign` FOREIGN KEY (`processed_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `branch_returns_product_batch_id_foreign` FOREIGN KEY (`product_batch_id`) REFERENCES `product_batches` (`id`),
  ADD CONSTRAINT `branch_returns_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  ADD CONSTRAINT `branch_returns_returned_to_location_id_foreign` FOREIGN KEY (`returned_to_location_id`) REFERENCES `storage_locations` (`id`),
  ADD CONSTRAINT `branch_returns_unit_id_foreign` FOREIGN KEY (`unit_id`) REFERENCES `units` (`id`);

--
-- Constraints for table `branch_stock_counts`
--
ALTER TABLE `branch_stock_counts`
  ADD CONSTRAINT `branch_stock_counts_approved_by_foreign` FOREIGN KEY (`approved_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `branch_stock_counts_branch_id_foreign` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `branch_stock_counts_created_by_foreign` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `branch_stock_counts_submitted_by_foreign` FOREIGN KEY (`submitted_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `fk_bsc_counted_by` FOREIGN KEY (`counted_by`) REFERENCES `users` (`id`);

--
-- Constraints for table `branch_stock_count_items`
--
ALTER TABLE `branch_stock_count_items`
  ADD CONSTRAINT `branch_stock_count_items_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  ADD CONSTRAINT `branch_stock_count_items_stock_count_id_foreign` FOREIGN KEY (`stock_count_id`) REFERENCES `branch_stock_counts` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `branch_stock_movements`
--
ALTER TABLE `branch_stock_movements`
  ADD CONSTRAINT `branch_stock_movements_batch_id_foreign` FOREIGN KEY (`batch_id`) REFERENCES `product_batches` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `branch_stock_movements_branch_id_foreign` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `branch_stock_movements_created_by_foreign` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `branch_stock_movements_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `branch_transfers`
--
ALTER TABLE `branch_transfers`
  ADD CONSTRAINT `branch_transfers_from_branch_id_foreign` FOREIGN KEY (`from_branch_id`) REFERENCES `branches` (`id`),
  ADD CONSTRAINT `branch_transfers_received_by_foreign` FOREIGN KEY (`received_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `branch_transfers_requested_by_foreign` FOREIGN KEY (`requested_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `branch_transfers_shipped_by_foreign` FOREIGN KEY (`shipped_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `branch_transfers_to_branch_id_foreign` FOREIGN KEY (`to_branch_id`) REFERENCES `branches` (`id`);

--
-- Constraints for table `branch_transfer_items`
--
ALTER TABLE `branch_transfer_items`
  ADD CONSTRAINT `branch_transfer_items_branch_transfer_id_foreign` FOREIGN KEY (`branch_transfer_id`) REFERENCES `branch_transfers` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `branch_transfer_items_product_batch_id_foreign` FOREIGN KEY (`product_batch_id`) REFERENCES `product_batches` (`id`),
  ADD CONSTRAINT `branch_transfer_items_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`);

--
-- Constraints for table `categories`
--
ALTER TABLE `categories`
  ADD CONSTRAINT `categories_parent_id_foreign` FOREIGN KEY (`parent_id`) REFERENCES `categories` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `distribution_orders`
--
ALTER TABLE `distribution_orders`
  ADD CONSTRAINT `distribution_orders_branch_id_foreign` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`id`),
  ADD CONSTRAINT `distribution_orders_created_by_foreign` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `distribution_orders_packed_by_foreign` FOREIGN KEY (`packed_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `distribution_orders_picked_by_foreign` FOREIGN KEY (`picked_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `distribution_orders_request_id_foreign` FOREIGN KEY (`request_id`) REFERENCES `branch_requests` (`id`),
  ADD CONSTRAINT `distribution_orders_shipped_by_foreign` FOREIGN KEY (`shipped_by`) REFERENCES `users` (`id`);

--
-- Constraints for table `distribution_order_items`
--
ALTER TABLE `distribution_order_items`
  ADD CONSTRAINT `distribution_order_items_batch_id_foreign` FOREIGN KEY (`batch_id`) REFERENCES `product_batches` (`id`),
  ADD CONSTRAINT `distribution_order_items_do_id_foreign` FOREIGN KEY (`do_id`) REFERENCES `distribution_orders` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `distribution_order_items_pick_location_id_foreign` FOREIGN KEY (`pick_location_id`) REFERENCES `storage_locations` (`id`),
  ADD CONSTRAINT `distribution_order_items_picked_by_foreign` FOREIGN KEY (`picked_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `distribution_order_items_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  ADD CONSTRAINT `distribution_order_items_unit_id_foreign` FOREIGN KEY (`unit_id`) REFERENCES `units` (`id`);

--
-- Constraints for table `distribution_order_picks`
--
ALTER TABLE `distribution_order_picks`
  ADD CONSTRAINT `distribution_order_picks_batch_id_foreign` FOREIGN KEY (`batch_id`) REFERENCES `product_batches` (`id`),
  ADD CONSTRAINT `distribution_order_picks_do_item_id_foreign` FOREIGN KEY (`do_item_id`) REFERENCES `distribution_order_items` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `distribution_order_picks_location_id_foreign` FOREIGN KEY (`location_id`) REFERENCES `storage_locations` (`id`),
  ADD CONSTRAINT `distribution_order_picks_picked_by_foreign` FOREIGN KEY (`picked_by`) REFERENCES `users` (`id`);

--
-- Constraints for table `goods_receipts`
--
ALTER TABLE `goods_receipts`
  ADD CONSTRAINT `goods_receipts_po_id_foreign` FOREIGN KEY (`po_id`) REFERENCES `purchase_orders` (`id`),
  ADD CONSTRAINT `goods_receipts_received_by_foreign` FOREIGN KEY (`received_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `goods_receipts_supplier_id_foreign` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`id`),
  ADD CONSTRAINT `goods_receipts_verified_by_foreign` FOREIGN KEY (`verified_by`) REFERENCES `users` (`id`);

--
-- Constraints for table `goods_receipt_items`
--
ALTER TABLE `goods_receipt_items`
  ADD CONSTRAINT `goods_receipt_items_batch_id_foreign` FOREIGN KEY (`batch_id`) REFERENCES `product_batches` (`id`),
  ADD CONSTRAINT `goods_receipt_items_gr_id_foreign` FOREIGN KEY (`gr_id`) REFERENCES `goods_receipts` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `goods_receipt_items_inspected_by_foreign` FOREIGN KEY (`inspected_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `goods_receipt_items_location_id_foreign` FOREIGN KEY (`location_id`) REFERENCES `storage_locations` (`id`),
  ADD CONSTRAINT `goods_receipt_items_po_item_id_foreign` FOREIGN KEY (`po_item_id`) REFERENCES `purchase_order_items` (`id`),
  ADD CONSTRAINT `goods_receipt_items_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  ADD CONSTRAINT `goods_receipt_items_unit_id_foreign` FOREIGN KEY (`unit_id`) REFERENCES `units` (`id`);

--
-- Constraints for table `inventory`
--
ALTER TABLE `inventory`
  ADD CONSTRAINT `inventory_batch_id_foreign` FOREIGN KEY (`batch_id`) REFERENCES `product_batches` (`id`),
  ADD CONSTRAINT `inventory_created_by_foreign` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `inventory_last_count_by_foreign` FOREIGN KEY (`last_count_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `inventory_location_id_foreign` FOREIGN KEY (`location_id`) REFERENCES `storage_locations` (`id`),
  ADD CONSTRAINT `inventory_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  ADD CONSTRAINT `inventory_updated_by_foreign` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`);

--
-- Constraints for table `products`
--
ALTER TABLE `products`
  ADD CONSTRAINT `products_base_unit_id_foreign` FOREIGN KEY (`base_unit_id`) REFERENCES `units` (`id`),
  ADD CONSTRAINT `products_category_id_foreign` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `products_created_by_foreign` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `products_deleted_by_foreign` FOREIGN KEY (`deleted_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `products_updated_by_foreign` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `product_batches`
--
ALTER TABLE `product_batches`
  ADD CONSTRAINT `product_batches_approved_by_foreign` FOREIGN KEY (`approved_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `product_batches_created_by_foreign` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `product_batches_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  ADD CONSTRAINT `product_batches_received_unit_id_foreign` FOREIGN KEY (`received_unit_id`) REFERENCES `units` (`id`),
  ADD CONSTRAINT `product_batches_supplier_id_foreign` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`id`);

--
-- Constraints for table `product_unit_conversions`
--
ALTER TABLE `product_unit_conversions`
  ADD CONSTRAINT `product_unit_conversions_base_unit_id_foreign` FOREIGN KEY (`base_unit_id`) REFERENCES `units` (`id`),
  ADD CONSTRAINT `product_unit_conversions_distribution_unit_id_foreign` FOREIGN KEY (`distribution_unit_id`) REFERENCES `units` (`id`),
  ADD CONSTRAINT `product_unit_conversions_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `product_unit_conversions_purchase_unit_id_foreign` FOREIGN KEY (`purchase_unit_id`) REFERENCES `units` (`id`),
  ADD CONSTRAINT `product_unit_conversions_sales_unit_id_foreign` FOREIGN KEY (`sales_unit_id`) REFERENCES `units` (`id`);

--
-- Constraints for table `purchase_orders`
--
ALTER TABLE `purchase_orders`
  ADD CONSTRAINT `purchase_orders_approved_by_foreign` FOREIGN KEY (`approved_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `purchase_orders_created_by_foreign` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `purchase_orders_supplier_id_foreign` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`id`);

--
-- Constraints for table `purchase_order_items`
--
ALTER TABLE `purchase_order_items`
  ADD CONSTRAINT `purchase_order_items_po_id_foreign` FOREIGN KEY (`po_id`) REFERENCES `purchase_orders` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `purchase_order_items_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  ADD CONSTRAINT `purchase_order_items_unit_id_foreign` FOREIGN KEY (`unit_id`) REFERENCES `units` (`id`);

--
-- Constraints for table `stock_adjustments`
--
ALTER TABLE `stock_adjustments`
  ADD CONSTRAINT `stock_adjustments_approved_by_foreign` FOREIGN KEY (`approved_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `stock_adjustments_cancelled_by_foreign` FOREIGN KEY (`cancelled_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `stock_adjustments_created_by_foreign` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`);

--
-- Constraints for table `stock_adjustment_items`
--
ALTER TABLE `stock_adjustment_items`
  ADD CONSTRAINT `stock_adjustment_items_adjustment_id_foreign` FOREIGN KEY (`adjustment_id`) REFERENCES `stock_adjustments` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `stock_adjustment_items_batch_id_foreign` FOREIGN KEY (`batch_id`) REFERENCES `product_batches` (`id`),
  ADD CONSTRAINT `stock_adjustment_items_location_id_foreign` FOREIGN KEY (`location_id`) REFERENCES `storage_locations` (`id`),
  ADD CONSTRAINT `stock_adjustment_items_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  ADD CONSTRAINT `stock_adjustment_items_unit_id_foreign` FOREIGN KEY (`unit_id`) REFERENCES `units` (`id`);

--
-- Constraints for table `stock_movements`
--
ALTER TABLE `stock_movements`
  ADD CONSTRAINT `stock_movements_batch_id_foreign` FOREIGN KEY (`batch_id`) REFERENCES `product_batches` (`id`),
  ADD CONSTRAINT `stock_movements_from_location_id_foreign` FOREIGN KEY (`from_location_id`) REFERENCES `storage_locations` (`id`),
  ADD CONSTRAINT `stock_movements_performed_by_foreign` FOREIGN KEY (`performed_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `stock_movements_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  ADD CONSTRAINT `stock_movements_to_location_id_foreign` FOREIGN KEY (`to_location_id`) REFERENCES `storage_locations` (`id`),
  ADD CONSTRAINT `stock_movements_unit_id_foreign` FOREIGN KEY (`unit_id`) REFERENCES `units` (`id`);

--
-- Constraints for table `stock_transfers`
--
ALTER TABLE `stock_transfers`
  ADD CONSTRAINT `stock_transfers_approved_by_foreign` FOREIGN KEY (`approved_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `stock_transfers_batch_id_foreign` FOREIGN KEY (`batch_id`) REFERENCES `product_batches` (`id`),
  ADD CONSTRAINT `stock_transfers_cancelled_by_foreign` FOREIGN KEY (`cancelled_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `stock_transfers_executed_by_foreign` FOREIGN KEY (`executed_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `stock_transfers_from_location_id_foreign` FOREIGN KEY (`from_location_id`) REFERENCES `storage_locations` (`id`),
  ADD CONSTRAINT `stock_transfers_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  ADD CONSTRAINT `stock_transfers_requested_by_foreign` FOREIGN KEY (`requested_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `stock_transfers_to_location_id_foreign` FOREIGN KEY (`to_location_id`) REFERENCES `storage_locations` (`id`),
  ADD CONSTRAINT `stock_transfers_unit_id_foreign` FOREIGN KEY (`unit_id`) REFERENCES `units` (`id`);

--
-- Constraints for table `storage_locations`
--
ALTER TABLE `storage_locations`
  ADD CONSTRAINT `storage_locations_zone_id_foreign` FOREIGN KEY (`zone_id`) REFERENCES `warehouse_zones` (`id`);

--
-- Constraints for table `suppliers`
--
ALTER TABLE `suppliers`
  ADD CONSTRAINT `suppliers_deleted_by_foreign` FOREIGN KEY (`deleted_by`) REFERENCES `users` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `users`
--
ALTER TABLE `users`
  ADD CONSTRAINT `users_branch_id_foreign` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`id`) ON DELETE SET NULL;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
