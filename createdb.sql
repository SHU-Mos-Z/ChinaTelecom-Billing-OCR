drop database if exists ChinaTelecom;

create database if not exists ChinaTelecom CHARACTER SET utf8 COLLATE utf8_unicode_ci;

use ChinaTelecom;

create table class
(
	class_id varchar(60) not null,
    class_name varchar(60) not null,
    primary key(class_id)
) CHARACTER SET utf8 COLLATE utf8_unicode_ci;

create table worker
(
	worker_id varchar(60) not null,
	class_id varchar(60) not null,
    worker_name varchar(60) not null,
    role enum('normal', 'class_manager', 'center_manager', 'system_manager') not null,
    pwd varchar(120) not null,
    primary key(worker_id),
    foreign key(class_id) references class(class_id) on update cascade on delete cascade
) CHARACTER SET utf8 COLLATE utf8_unicode_ci;

create table worker_quota_monthly
(
    worker_id varchar(60) not null,
    year_ year not null,
    quota_01 float(16, 2) not null default 0,
    quota_02 float(16, 2) not null default 0,
    quota_03 float(16, 2) not null default 0,
    quota_04 float(16, 2) not null default 0,
    quota_05 float(16, 2) not null default 0,
    quota_06 float(16, 2) not null default 0,
    quota_07 float(16, 2) not null default 0,
    quota_08 float(16, 2) not null default 0,
    quota_09 float(16, 2) not null default 0,
    quota_10 float(16, 2) not null default 0,
    quota_11 float(16, 2) not null default 0,
    quota_12 float(16, 2) not null default 0,
    primary key(worker_id, year_),
    foreign key(worker_id) references worker(worker_id) on update cascade on delete cascade
) CHARACTER SET utf8 COLLATE utf8_unicode_ci;


create table class_quota_monthly
(
    class_id varchar(60) not null,
    year_ year not null,
    quota_01 float(16, 2) not null default 0,
    quota_02 float(16, 2) not null default 0,
    quota_03 float(16, 2) not null default 0,
    quota_04 float(16, 2) not null default 0,
    quota_05 float(16, 2) not null default 0,
    quota_06 float(16, 2) not null default 0,
    quota_07 float(16, 2) not null default 0,
    quota_08 float(16, 2) not null default 0,
    quota_09 float(16, 2) not null default 0,
    quota_10 float(16, 2) not null default 0,
    quota_11 float(16, 2) not null default 0,
    quota_12 float(16, 2) not null default 0,
    primary key(class_id, year_),
    foreign key(class_id) references class(class_id) on update cascade on delete cascade
) CHARACTER SET utf8 COLLATE utf8_unicode_ci;

create table service_record
(
	service_record_id varchar(60) not null,	-- 发票号码
	service_name varchar(60) not null,	-- 项目名称
    invoice_type enum('pdf', 'ofd', 'image') not null,	-- 发票类型
    service_time datetime,	-- 开票时间
    upload_time datetime,	-- 上传时间
    buyer_company_id varchar(60),	-- 购买方信用代码
    seller_company_id varchar(60),	-- 销售方信用代码
	buyer_company_name varchar(60),	-- 购买方信用名称
    seller_company_name varchar(60),	-- 销售方信用名称
    worker_id varchar(60) not null,	-- 开票人
    cost varchar(60) not null,	-- 金额
    total float4 not null,	-- 总额
    total_tax float4 not null,	-- 含税总额
    is_exception bool default false not null,	-- 是否认为识别结果异常
    primary key(service_record_id),
    foreign key(worker_id) references worker(worker_id) on update restrict on delete restrict
) CHARACTER SET utf8 COLLATE utf8_unicode_ci;


INSERT INTO class (class_id, class_name) VALUES ('C001', '应用室');
INSERT INTO class (class_id, class_name) VALUES ('C002', '开发部');
INSERT INTO class (class_id, class_name) VALUES ('C003', '食堂');


INSERT INTO worker (worker_id, class_id, worker_name, role, pwd) VALUES ('W001', 'C001', '张洁铭', 'class_manager', '12345');
INSERT INTO worker (worker_id, class_id, worker_name, role, pwd) VALUES ('W002', 'C001', '付致宁', 'center_manager', '12345');
INSERT INTO worker (worker_id, class_id, worker_name, role, pwd) VALUES ('W003', 'C001', '黄奕', 'system_manager', '12345');
INSERT INTO worker (worker_id, class_id, worker_name, role, pwd) VALUES ('W004', 'C001', '赵红燕', 'normal', '12345');
INSERT INTO worker (worker_id, class_id, worker_name, role, pwd) VALUES ('W005', 'C001', '唐文琪', 'normal', '12345');
INSERT INTO worker (worker_id, class_id, worker_name, role, pwd) VALUES ('W006', 'C001', '陈峙良', 'normal', '12345');
INSERT INTO worker (worker_id, class_id, worker_name, role, pwd) VALUES ('W007', 'C001', '朱瀛', 'normal', '12345');
INSERT INTO worker (worker_id, class_id, worker_name, role, pwd) VALUES ('W008', 'C002', '吴怡晨', 'class_manager', '12345');
INSERT INTO worker (worker_id, class_id, worker_name, role, pwd) VALUES ('W009', 'C002', '丁浩', 'normal', '12345');
INSERT INTO worker (worker_id, class_id, worker_name, role, pwd) VALUES ('W010', 'C002', '曹青宇', 'normal', '12345');
INSERT INTO worker (worker_id, class_id, worker_name, role, pwd) VALUES ('W011', 'C003', '蔡奇', 'normal', '12345');
INSERT INTO worker (worker_id, class_id, worker_name, role, pwd) VALUES ('W012', 'C003', '刘絮', 'class_manager', '12345');
INSERT INTO worker (worker_id, class_id, worker_name, role, pwd) VALUES ('W013', 'C003', '蒋春平', 'normal', '12345');
INSERT INTO worker (worker_id, class_id, worker_name, role, pwd) VALUES ('W014', 'C003', '周晓君', 'normal', '12345');

SET @start_year = 2020;
SET @end_year = 2024;

INSERT INTO worker_quota_monthly (worker_id, year_, quota_01, quota_02, quota_03, quota_04, quota_05, quota_06, quota_07, quota_08, quota_09, quota_10, quota_11, quota_12)
SELECT worker_id, years.year_, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500
FROM worker
CROSS JOIN (
    SELECT @start_year AS year_
    UNION ALL SELECT @start_year + 1
    UNION ALL SELECT @start_year + 2
    UNION ALL SELECT @start_year + 3
    UNION ALL SELECT @start_year + 4
) AS years;


INSERT INTO class_quota_monthly (class_id, year_, quota_01, quota_02, quota_03, quota_04, quota_05, quota_06, quota_07, quota_08, quota_09, quota_10, quota_11, quota_12)
SELECT class_id, years.year_, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500
FROM class
CROSS JOIN (
    SELECT @start_year AS year_
    UNION ALL SELECT @start_year + 1
    UNION ALL SELECT @start_year + 2
    UNION ALL SELECT @start_year + 3
    UNION ALL SELECT @start_year + 4
) AS years;

INSERT INTO service_record (service_record_id, service_name, invoice_type, service_time, upload_time, buyer_company_name, seller_company_name, worker_id, cost, total, total_tax) 
VALUES ('1', '餐饮', 'pdf', '2024-07-01 10:00:00', '2024-07-01 12:00:00', 'ChinaTelcom', 'FoodCorp', 'W001', '100.0', '100.0', '116.0');

INSERT INTO service_record (service_record_id, service_name, invoice_type, service_time, upload_time, buyer_company_name, seller_company_name, worker_id, cost, total, total_tax) 
VALUES ('2', '餐饮', 'pdf', '2024-07-02 11:00:00', '2024-07-02 13:00:00', 'ChinaTelcom', 'FoodCorp', 'W002', '150.0', '150.0', '174.0');

INSERT INTO service_record (service_record_id, service_name, invoice_type, service_time, upload_time, buyer_company_name, seller_company_name, worker_id, cost, total, total_tax) 
VALUES ('3', '餐饮', 'pdf', '2024-07-03 09:00:00', '2024-07-03 11:00:00', 'ChinaTelcom', 'TechConsult', 'W005', '500.0', '500.0', '580.0');

INSERT INTO service_record (service_record_id, service_name, invoice_type, service_time, upload_time, buyer_company_name, seller_company_name, worker_id, cost, total, total_tax) 
VALUES ('4', '餐饮', 'pdf', '2024-07-04 14:00:00', '2024-07-04 16:00:00', 'ChinaTelcom', 'FoodCorp', 'W003', '80.0', '80.0', '92.8');

INSERT INTO service_record (service_record_id, service_name, invoice_type, service_time, upload_time, buyer_company_name, seller_company_name, worker_id, cost, total, total_tax) 
VALUES ('5', '餐饮', 'pdf', '2024-07-05 15:00:00', '2024-07-05 17:00:00', 'ChinaTelcom', 'TechConsult', 'W007', '1200.0', '1200.0', '1392.0');

INSERT INTO service_record (service_record_id, service_name, invoice_type, service_time, upload_time, buyer_company_name, seller_company_name, worker_id, cost, total, total_tax) 
VALUES ('6', '餐饮', 'pdf', '2024-07-06 13:00:00', '2024-07-06 15:00:00', 'ChinaTelcom', 'FoodCorp', 'W009', '200.0', '200.0', '232.0');

INSERT INTO service_record (service_record_id, service_name, invoice_type, service_time, upload_time, buyer_company_name, seller_company_name, worker_id, cost, total, total_tax) 
VALUES ('7', '餐饮', 'pdf', '2024-07-07 16:00:00', '2024-07-07 18:00:00', 'ChinaTelcom', 'TechConsult', 'W011', '700.0', '700.0', '812.0');

INSERT INTO service_record (service_record_id, service_name, invoice_type, service_time, upload_time, buyer_company_name, seller_company_name, worker_id, cost, total, total_tax) 
VALUES ('8', '餐饮', 'pdf', '2024-07-08 12:00:00', '2024-07-08 14:00:00', 'ChinaTelcom', 'FoodCorp', 'W013', '250.0', '250.0', '290.0');

INSERT INTO service_record (service_record_id, service_name, invoice_type, service_time, upload_time, buyer_company_name, seller_company_name, worker_id, cost, total, total_tax) 
VALUES ('9', '餐饮', 'pdf', '2024-07-09 11:30:00', '2024-07-09 13:30:00', 'ChinaTelcom', 'TechConsult', 'W014', '600.0', '600.0', '696.0');

INSERT INTO service_record (service_record_id, service_name, invoice_type, service_time, upload_time, buyer_company_name, seller_company_name, worker_id, cost, total, total_tax) 
VALUES ('10', '餐饮', 'pdf', '2024-07-10 10:30:00', '2024-07-10 12:30:00', 'ChinaTelcom', 'FoodCorp', 'W006', '180.0', '180.0', '208.8');

INSERT INTO service_record (service_record_id, service_name, invoice_type, service_time, upload_time, buyer_company_name, seller_company_name, worker_id, cost, total, total_tax) 
VALUES ('11', '餐饮', 'pdf', '2024-01-11 10:00:00', '2024-01-11 12:00:00', 'ChinaTelecom', 'FoodCorp', 'W001', '90.0', '90.0', '104.4');

INSERT INTO service_record (service_record_id, service_name, invoice_type, service_time, upload_time, buyer_company_name, seller_company_name, worker_id, cost, total, total_tax) 
VALUES ('12', '办公用品', 'pdf', '2024-08-12 11:00:00', '2024-08-12 13:00:00', 'ChinaTelecom', 'OfficeSupplyCo', 'W001', '200.0', '200.0', '232.0');

INSERT INTO service_record (service_record_id, service_name, invoice_type, service_time, upload_time, buyer_company_name, seller_company_name, worker_id, cost, total, total_tax) 
VALUES ('13', 'IT服务', 'pdf', '2024-09-13 09:00:00', '2024-09-13 11:00:00', 'ChinaTelecom', 'TechConsult', 'W001', '300.0', '300.0', '348.0');

INSERT INTO service_record (service_record_id, service_name, invoice_type, service_time, upload_time, buyer_company_name, seller_company_name, worker_id, cost, total, total_tax) 
VALUES ('14', '餐饮', 'pdf', '2024-01-14 14:00:00', '2024-01-14 16:00:00', 'ChinaTelecom', 'FoodCorp', 'W001', '50.0', '50.0', '58.0');

INSERT INTO service_record (service_record_id, service_name, invoice_type, service_time, upload_time, buyer_company_name, seller_company_name, worker_id, cost, total, total_tax) 
VALUES ('15', '办公用品', 'pdf', '2024-07-15 15:00:00', '2024-07-15 17:00:00', 'ChinaTelecom', 'OfficeSupplyCo', 'W001', '150.0', '150.0', '174.0');

INSERT INTO service_record (service_record_id, service_name, invoice_type, service_time, upload_time, buyer_company_name, seller_company_name, worker_id, cost, total, total_tax) 
VALUES ('16', '餐饮', 'pdf', '2024-04-16 13:00:00', '2024-04-16 15:00:00', 'ChinaTelecom', 'FoodCorp', 'W001', '120.0', '120.0', '139.2');

INSERT INTO service_record (service_record_id, service_name, invoice_type, service_time, upload_time, buyer_company_name, seller_company_name, worker_id, cost, total, total_tax) 
VALUES ('17', 'IT服务', 'pdf', '2024-03-17 16:00:00', '2024-03-17 18:00:00', 'ChinaTelecom', 'TechConsult', 'W001', '400.0', '400.0', '464.0');

INSERT INTO service_record (service_record_id, service_name, invoice_type, service_time, upload_time, buyer_company_name, seller_company_name, worker_id, cost, total, total_tax) 
VALUES ('18', '餐饮', 'pdf', '2024-07-18 12:00:00', '2024-07-18 14:00:00', 'ChinaTelecom', 'FoodCorp', 'W001', '300.0', '300.0', '348.0');

INSERT INTO service_record (service_record_id, service_name, invoice_type, service_time, upload_time, buyer_company_name, seller_company_name, worker_id, cost, total, total_tax) 
VALUES ('19', '餐饮', 'pdf', '2024-02-19 11:30:00', '2024-02-19 13:30:00', 'ChinaTelecom', 'TechConsult', 'W001', '600.0', '600.0', '696.0');

INSERT INTO service_record (service_record_id, service_name, invoice_type, service_time, upload_time, buyer_company_name, seller_company_name, worker_id, cost, total, total_tax) 
VALUES ('20', '餐饮', 'pdf', '2024-07-20 10:30:00', '2024-07-20 12:30:00', 'ChinaTelecom', 'FoodCorp', 'W001', '80.0', '80.0', '92.8');

INSERT INTO service_record (service_record_id, service_name, invoice_type, service_time, upload_time, buyer_company_name, seller_company_name, worker_id, cost, total, total_tax) 
VALUES ('21', 'IT服务', 'pdf', '2024-07-21 14:30:00', '2024-07-21 16:30:00', 'ChinaTelecom', 'TechConsult', 'W001', '250.0', '250.0', '290.0');

INSERT INTO service_record (service_record_id, service_name, invoice_type, service_time, upload_time, buyer_company_name, seller_company_name, worker_id, cost, total, total_tax) 
VALUES ('22', '餐饮', 'pdf', '2024-07-22 15:30:00', '2024-07-22 17:30:00', 'ChinaTelecom', 'FoodCorp', 'W001', '70.0', '70.0', '81.2');

INSERT INTO service_record (service_record_id, service_name, invoice_type, service_time, upload_time, buyer_company_name, seller_company_name, worker_id, cost, total, total_tax) 
VALUES ('23', '办公用品', 'pdf', '2024-07-23 12:00:00', '2024-07-23 14:00:00', 'ChinaTelecom', 'OfficeSupplyCo', 'W001', '90.0', '90.0', '104.4');

INSERT INTO service_record (service_record_id, service_name, invoice_type, service_time, upload_time, buyer_company_name, seller_company_name, worker_id, cost, total, total_tax) 
VALUES ('24', '餐饮', 'pdf', '2024-07-24 11:00:00', '2024-07-24 13:00:00', 'ChinaTelecom', 'FoodCorp', 'W001', '130.0', '130.0', '150.8');

INSERT INTO service_record (service_record_id, service_name, invoice_type, service_time, upload_time, buyer_company_name, seller_company_name, worker_id, cost, total, total_tax) 
VALUES ('25', 'IT服务', 'pdf', '2024-07-25 16:00:00', '2024-07-25 18:00:00', 'ChinaTelecom', 'TechConsult', 'W001', '500.0', '500.0', '580.0');




select * from service_record;
select * from worker;
select * from worker_quota_monthly;
select * from class_quota_monthly;