drop database if exists ChinaTelecom;

create database if not exists ChinaTelecom CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

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
    role enum('normal', 'class_manager', 'center_manager', 'invoice_manager') not null,
    pwd varchar(120) not null,
    primary key(worker_id),
    foreign key(class_id) references class(class_id) on update cascade on delete cascade
) CHARACTER SET utf8 COLLATE utf8_unicode_ci;

create table service
(
	service_id varchar(60) not null,
	service_name varchar(60) not null,	-- 发票项目名称
    primary key(service_id)
) CHARACTER SET utf8 COLLATE utf8_unicode_ci;


create table service_record
(
	service_record_id int8 not null,	-- 发票号码
	service_id varchar(60) not null,	-- 项目名称id
    invoice_type enum('printed', 'electronic') not null,	-- 发票类型
    service_time datetime,	-- 开票时间
    upload_time datetime,	-- 上传时间
    buyer_company varchar(60),	-- 购买方信用代码
    seller_company varchar(60),	-- 销售方信用代码
    worker_id varchar(60) not null,	-- 开票人
    cost varchar(60) not null,	-- 金额
    total float4 not null,	-- 总额
    total_tax float4 not null,	-- 含税总额
    is_exception bool default false,	-- 是否认为识别结果异常
    primary key(service_record_id),
    foreign key(service_id) references service(service_id) on update restrict on delete restrict,    
    foreign key(worker_id) references worker(worker_id) on update restrict on delete restrict
) CHARACTER SET utf8 COLLATE utf8_unicode_ci;


INSERT INTO class (class_id, class_name) VALUES ('C001', '应用室');
INSERT INTO class (class_id, class_name) VALUES ('C002', '开发部');
INSERT INTO class (class_id, class_name) VALUES ('C003', '食堂');


INSERT INTO worker (worker_id, class_id, worker_name, role, pwd) VALUES ('W001', 'C001', '张洁铭', 'class_manager', '12345');
INSERT INTO worker (worker_id, class_id, worker_name, role, pwd) VALUES ('W002', 'C001', '付致宁', 'center_manager', '12345');
INSERT INTO worker (worker_id, class_id, worker_name, role, pwd) VALUES ('W003', 'C001', '黄奕', 'invoice_manager', '12345');
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


INSERT INTO service (service_id, service_name) VALUES ('S001', '餐饮');
INSERT INTO service (service_id, service_name) VALUES ('S002', '非餐饮');

INSERT INTO service_record (service_record_id, service_id, invoice_type, service_time, buyer_company, seller_company, worker_id, cost, total, total_tax) 
VALUES (1, 'S001', 'printed', '2024-07-01 10:00:00', 'ChinaTelcom', 'FoodCorp', 'W001', '100.0', '100.0', '116.0');

INSERT INTO service_record (service_record_id, service_id, invoice_type, service_time, buyer_company, seller_company, worker_id, cost, total, total_tax) 
VALUES (2, 'S001', 'printed', '2024-07-02 11:00:00', 'ChinaTelcom', 'FoodCorp', 'W002', '150.0', '150.0', '174.0');

INSERT INTO service_record (service_record_id, service_id, invoice_type, service_time, buyer_company, seller_company, worker_id, cost, total, total_tax) 
VALUES (3, 'S002', 'printed', '2024-07-03 09:00:00', 'ChinaTelcom', 'TechConsult', 'W005', '500.0', '500.0', '580.0');

INSERT INTO service_record (service_record_id, service_id, invoice_type, service_time, buyer_company, seller_company, worker_id, cost, total, total_tax) 
VALUES (4, 'S001', 'printed', '2024-07-04 14:00:00', 'ChinaTelcom', 'FoodCorp', 'W003', '80.0', '80.0', '92.8');

INSERT INTO service_record (service_record_id, service_id, invoice_type, service_time, buyer_company, seller_company, worker_id, cost, total, total_tax) 
VALUES (5, 'S002', 'printed', '2024-07-05 15:00:00', 'ChinaTelcom', 'TechConsult', 'W007', '1200.0', '1200.0', '1392.0');

INSERT INTO service_record (service_record_id, service_id, invoice_type, service_time, buyer_company, seller_company, worker_id, cost, total, total_tax) 
VALUES (6, 'S001', 'printed', '2024-07-06 13:00:00', 'ChinaTelcom', 'FoodCorp', 'W009', '200.0', '200.0', '232.0');

INSERT INTO service_record (service_record_id, service_id, invoice_type, service_time, buyer_company, seller_company, worker_id, cost, total, total_tax) 
VALUES (7, 'S002', 'printed', '2024-07-07 16:00:00', 'ChinaTelcom', 'TechConsult', 'W011', '700.0', '700.0', '812.0');

INSERT INTO service_record (service_record_id, service_id, invoice_type, service_time, buyer_company, seller_company, worker_id, cost, total, total_tax) 
VALUES (8, 'S001', 'printed', '2024-07-08 12:00:00', 'ChinaTelcom', 'FoodCorp', 'W013', '250.0', '250.0', '290.0');

INSERT INTO service_record (service_record_id, service_id, invoice_type, service_time, buyer_company, seller_company, worker_id, cost, total, total_tax) 
VALUES (9, 'S002', 'printed', '2024-07-09 11:30:00', 'ChinaTelcom', 'TechConsult', 'W014', '600.0', '600.0', '696.0');

INSERT INTO service_record (service_record_id, service_id, invoice_type, service_time, buyer_company, seller_company, worker_id, cost, total, total_tax) 
VALUES (10, 'S001', 'printed', '2024-07-10 10:30:00', 'ChinaTelcom', 'FoodCorp', 'W006', '180.0', '180.0', '208.8');


select * from service_record;
select * from worker;