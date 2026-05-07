create database online_store;
use online_store;
SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE `users` (
   `name` varchar(255) NOT NULL,
   `email` varchar(255) NOT NULL,
   `username` varchar(255) NOT NULL,
   `password` varchar(255) NOT NULL,
   `userid` int NOT NULL AUTO_INCREMENT,
   `role` enum('admin','vendor','customer') DEFAULT NULL,
   PRIMARY KEY (`userid`),
   UNIQUE KEY `unique_email` (`email`),
   UNIQUE KEY `unique_username` (`username`)
);

CREATE TABLE `warranty` (
   `expire_date` date NOT NULL,
   `warrantyid` int NOT NULL AUTO_INCREMENT,
   PRIMARY KEY (`warrantyid`)
);

CREATE TABLE `chat` (
   `chatid` int NOT NULL AUTO_INCREMENT,
   `reason` varchar(255) NOT NULL,
   `userid` int DEFAULT NULL,
   PRIMARY KEY (`chatid`),
   KEY `userid` (`userid`),
   CONSTRAINT `chat_ibfk_1` FOREIGN KEY (`userid`) REFERENCES `users` (`userid`)
);

CREATE TABLE `cart` (
   `cartid` int NOT NULL AUTO_INCREMENT,
   `total` decimal(10,2) NOT NULL DEFAULT '0.00',
   `userid` int NOT NULL,
   PRIMARY KEY (`cartid`),
   KEY `userid` (`userid`),
   CONSTRAINT `cart_ibfk_1` FOREIGN KEY (`userid`) REFERENCES `users` (`userid`)
);


CREATE TABLE `orders` (
   `date` date NOT NULL,
   `total` decimal(10,2) NOT NULL,
   `orderstatus` varchar(50) DEFAULT NULL,
   `cartid` int NOT NULL,
   `orderid` int NOT NULL AUTO_INCREMENT,
   PRIMARY KEY (`orderid`),
   KEY `cartid` (`cartid`),
   CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`cartid`) REFERENCES `cart` (`cartid`)
);



CREATE TABLE `products` (
   `title` varchar(255) NOT NULL,
   `description` varchar(255) NOT NULL,
   `productid` int NOT NULL AUTO_INCREMENT,
   `price` decimal(10,2) NOT NULL,
   `instock` int NOT NULL,
   `image` varchar(500) DEFAULT NULL,
   `warrantyid` int DEFAULT NULL,
   `vendorid` int NOT NULL,
   `colorid` int DEFAULT NULL,
   `sizeid` int DEFAULT NULL,
   PRIMARY KEY (`productid`),
   KEY `warrantyid` (`warrantyid`),
   KEY `vendorid` (`vendorid`),
   KEY `fk_products_color` (`colorid`),
   KEY `fk_products_size` (`sizeid`),
   CONSTRAINT `fk_products_color` FOREIGN KEY (`colorid`) REFERENCES `color` (`colorid`),
   CONSTRAINT `fk_products_size` FOREIGN KEY (`sizeid`) REFERENCES `size` (`sizeid`),
   CONSTRAINT `products_ibfk_1` FOREIGN KEY (`warrantyid`) REFERENCES `warranty` (`warrantyid`),
   CONSTRAINT `products_ibfk_2` FOREIGN KEY (`vendorid`) REFERENCES `users` (`userid`)
);


CREATE TABLE `returns` (
   `complaint` varchar(255) NOT NULL,
   `returnid` int NOT NULL AUTO_INCREMENT,
   `date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
   `title` varchar(255) NOT NULL,
   `orderid` int NOT NULL,
   `image` varchar(500) DEFAULT NULL,
   `type` enum('refund','return','warranty') DEFAULT NULL,
   `status` varchar(50) DEFAULT NULL,
   `warrantyid` int DEFAULT NULL,
   PRIMARY KEY (`returnid`),
   KEY `orderid` (`orderid`),
   CONSTRAINT `returns_ibfk_1` FOREIGN KEY (`orderid`) REFERENCES `orders` (`orderid`)
);


CREATE TABLE `discount` (
   `discountid` int NOT NULL AUTO_INCREMENT,
   `length` date DEFAULT NULL,
   `discountprice` decimal(10,2) NOT NULL,
   `price` decimal(10,2) NOT NULL,
   PRIMARY KEY (`discountid`)
);


CREATE TABLE `discount_products` (
   `discountid` int NOT NULL,
   `productid` int NOT NULL,
   PRIMARY KEY (`discountid`,`productid`),
   KEY `productid` (`productid`),
   CONSTRAINT `discount_products_ibfk_1` FOREIGN KEY (`discountid`) REFERENCES `discount` (`discountid`),
   CONSTRAINT `discount_products_ibfk_2` FOREIGN KEY (`productid`) REFERENCES `products` (`productid`)
);


CREATE TABLE `color` (
   `colorid` int NOT NULL AUTO_INCREMENT,
   `colorname` varchar(255) NOT NULL,
   PRIMARY KEY (`colorid`)
);


CREATE TABLE `cartitem` (
   `cartitemid` int NOT NULL AUTO_INCREMENT,
   `cartid` int NOT NULL,
   `productid` int NOT NULL,
   `quantity` int NOT NULL,
   PRIMARY KEY (`cartitemid`),
   KEY `cartid` (`cartid`),
   KEY `productid` (`productid`),
   CONSTRAINT `cartitem_ibfk_1` FOREIGN KEY (`cartid`) REFERENCES `cart` (`cartid`),
   CONSTRAINT `cartitem_ibfk_2` FOREIGN KEY (`productid`) REFERENCES `products` (`productid`)
);


CREATE TABLE `orderitems` (
   `orderitemid` int NOT NULL AUTO_INCREMENT,
   `orderid` int NOT NULL,
   `productid` int NOT NULL,
   `quantity` int NOT NULL,
   `price` decimal(10,2) NOT NULL,
   PRIMARY KEY (`orderitemid`),
   KEY `orderid` (`orderid`),
   KEY `productid` (`productid`),
   CONSTRAINT `orderitems_ibfk_1` FOREIGN KEY (`orderid`) REFERENCES `orders` (`orderid`),
   CONSTRAINT `orderitems_ibfk_2` FOREIGN KEY (`productid`) REFERENCES `products` (`productid`)
);

CREATE TABLE `review` (
   `reviewid` int NOT NULL AUTO_INCREMENT,
   `userid` int NOT NULL,
   `productid` int NOT NULL,
   `rating` enum('1','2','3','4','5') NOT NULL,
   `reviewtext` varchar(255) NOT NULL,
   `name` varchar(255) DEFAULT NULL,
   `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
   PRIMARY KEY (`reviewid`),
   KEY `userid` (`userid`),
   KEY `productid` (`productid`),
   CONSTRAINT `review_ibfk_1` FOREIGN KEY (`userid`) REFERENCES `users` (`userid`),
   CONSTRAINT `review_ibfk_2` FOREIGN KEY (`productid`) REFERENCES `products` (`productid`)
);


CREATE TABLE `wishlist` (
   `userid` int NOT NULL,
   `productid` int NOT NULL,
   PRIMARY KEY (`userid`,`productid`),
   KEY `productid` (`productid`),
   CONSTRAINT `wishlist_ibfk_1` FOREIGN KEY (`userid`) REFERENCES `users` (`userid`),
   CONSTRAINT `wishlist_ibfk_2` FOREIGN KEY (`productid`) REFERENCES `products` (`productid`)
);


CREATE TABLE `complaint` (
   `complaintid` int NOT NULL AUTO_INCREMENT,
   `complaint_date` datetime DEFAULT CURRENT_TIMESTAMP,
   `description` varchar(255) DEFAULT NULL,
   `productid` int NOT NULL,
   `userid` int NOT NULL,
   `demand` enum('return','refund','warraty claim') DEFAULT NULL,
   `status` enum('pending','rejected','confrimed') DEFAULT NULL,
   `warrantyid` int DEFAULT NULL,
   PRIMARY KEY (`complaintid`),
   KEY `userid` (`userid`),
   KEY `productid` (`productid`),
   KEY `fk_warranty` (`warrantyid`),
   CONSTRAINT `complaint_ibfk_1` FOREIGN KEY (`userid`) REFERENCES `users` (`userid`),
   CONSTRAINT `complaint_ibfk_2` FOREIGN KEY (`productid`) REFERENCES `products` (`productid`),
   CONSTRAINT `fk_warranty` FOREIGN KEY (`warrantyid`) REFERENCES `warranty` (`warrantyid`)
);


CREATE TABLE `conversation` (
   `conversationid` int NOT NULL AUTO_INCREMENT,
   `customerid` int NOT NULL,
   `adminid` int DEFAULT NULL,
   `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
   `vendorid` int DEFAULT NULL,
   PRIMARY KEY (`conversationid`),
   KEY `customerid` (`customerid`),
   KEY `adminid` (`adminid`),
   KEY `vendorid` (`vendorid`),
   CONSTRAINT `conversation_ibfk_1` FOREIGN KEY (`customerid`) REFERENCES `users` (`userid`),
   CONSTRAINT `conversation_ibfk_2` FOREIGN KEY (`adminid`) REFERENCES `users` (`userid`),
   CONSTRAINT `conversation_ibfk_3` FOREIGN KEY (`vendorid`) REFERENCES `users` (`userid`)
);

CREATE TABLE `size` (
   `sizeid` int NOT NULL AUTO_INCREMENT,
   `sizename` varchar(50) NOT NULL,
   PRIMARY KEY (`sizeid`)
);

CREATE TABLE `message` (
   `messageid` int NOT NULL AUTO_INCREMENT,
   `conversationid` int NOT NULL,
   `senderid` int NOT NULL,
   `content` text NOT NULL,
   `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
   PRIMARY KEY (`messageid`),
   KEY `conversationid` (`conversationid`),
   KEY `senderid` (`senderid`),
   CONSTRAINT `message_ibfk_1` FOREIGN KEY (`conversationid`) REFERENCES `conversation` (`conversationid`),
   CONSTRAINT `message_ibfk_2` FOREIGN KEY (`senderid`) REFERENCES `users` (`userid`)
);


-- =========================================
-- USERS INSERTS
-- =========================================

-- ADMINS
INSERT INTO users(name,email,username,password,role)
VALUES
('jackson','jackson12@gmail.com','bigjack','jackjack','admin'),
('joshua','joshua12@gmail.com','littlejoshua','joshua','admin');

-- CUSTOMERS
INSERT INTO users(name,email,username,password,role)
VALUES
('manuel','manuel12@gmail.com','bigmanuel','manuel1','customer'),
('collin','collin12@gmail.com','littlecollin','collin1','customer'),
('steve','steve12@gmail.com','bigsteve','steve1','customer'),
('mike','mike12@gmail.com','bigmike','mike1','customer'),
('caleb','caleb12@gmail.com','bigcaleb','caleb1','customer');

-- 3 VENDORS
INSERT INTO users(name,email,username,password,role)
VALUES
('owen','owen12@gmail.com','bigowen','owen1','vendor'),
('jim','jim12@gmail.com','bigjim','jim1','vendor'),
('claire','claire12@gmail.com','bigclaire','claire1','vendor');

-- =========================================
-- WARRANTY INSERTS
-- =========================================

INSERT INTO warranty(expire_date)
VALUES
('2027-01-01'),
('2027-06-01'),
('2028-01-01'),
('2028-06-01');

-- =========================================
-- COLORS
-- =========================================

INSERT INTO color(colorname)
VALUES
('red'),
('blue'),
('green'),
('black'),
('white');

-- =========================================
-- SIZES
-- =========================================

INSERT INTO size(sizename)
VALUES
('extra small'),
('small'),
('medium'),
('large'),
('extra large');

-- =========================================
-- 10 PRODUCTS
-- =========================================

INSERT INTO products(
    title,
    description,
    price,
    instock,
    image,
    warrantyid,
    vendorid,
    colorid,
    sizeid
)

VALUES
('Crew Socks','A pair of crew socks',10.00,100,'/static/images/crew-sock.png',1,8,1,2),
('Ankle Socks','A pair of ankle socks',20.00,50,'/static/images/ankle-sock.png',2,9,2,3),
('No-Show Socks','A pair of no-show socks',30.00,25,'/static/images/no-show-sock.png',3,10,3,4),
('Knee-High Socks','A pair of knee-high socks',15.00,75,'/static/images/knee-high-sock.png',4,8,4,2),
('Over-the-Calf Socks','A pair of over-the-calf socks',15.00,75,'/static/images/calf-sock.png',1,9,5,5),
('Compression Socks','A pair of compression socks',12.00,80,'/static/images/compression-sock.png',2,10,1,3),
('Dress Socks','A pair of dress socks',18.00,60,'/static/images/dress-sock.png',3,8,2,4),
('Athletic Socks','A pair of athletic socks',14.00,90,'/static/images/athletic-sock.png',4,9,3,3),
('Hiking Socks','A pair of hiking socks',22.00,40,'/static/images/hiking-sock.png',1,10,4,5),
('Wool Socks','A pair of wool socks',25.00,30,'/static/images/wool-sock.png',2,8,5,4);
('Octopus socks','8 socks in different colors',100.00,8,'/static/images/octopus_sock.png',2,8,5,4);


-- =========================================
-- DISCOUNTS
-- =========================================

INSERT INTO discount(length,discountprice,price)
VALUES
(NULL,8.00,10.00),
(NULL,15.00,18.00),
('2026-12-31',16.00,20.00),
('2026-12-31',25.00,30.00);

-- =========================================
-- CARTS
-- =========================================

INSERT INTO cart(total, userid)
VALUES
(44.00,4),
(38.00,3),
(80.00,5);

-- =========================================
-- CART ITEMS
-- =========================================

INSERT INTO cartitem(cartid,productid,quantity)
VALUES
(1,5,2),
(1,9,1),
(2,1,2),
(2,7,1),
(3,3,1),
(3,10,2);

-- =========================================
-- ORDERS
-- =========================================

INSERT INTO orders(date,total,orderstatus,cartid)
VALUES
('2026-04-09',44.00,'pending',1),
('2026-04-09',38.00,'confirmed',2),
('2026-04-09',80.00,'handed to partner',3),
('2026-04-09',20.00,'shipped',1),
('2026-04-09',12.00,'shipped',2),
('2026-04-09',14.00,'shipped',3);

-- =========================================
-- ORDER ITEMS
-- =========================================

INSERT INTO orderitems(orderid,productid,quantity,price)
VALUES
(1,5,2,15.00),
(1,9,1,22.00),
(2,1,2,10.00),
(2,7,1,18.00),
(3,3,1,30.00),
(3,10,2,25.00),
(4,2,1,20.00),
(5,6,1,12.00),
(6,8,1,14.00);

-- =========================================
-- REVIEWS
-- =========================================

INSERT INTO review(userid,productid,rating,reviewtext,name)
VALUES
(3,1,'5','Great quality and very comfortable.','manuel'),
(4,5,'4','Good socks, fit well.','collin'),
(5,3,'5','Perfect no-show socks.','steve'),
(6,7,'3','Decent but thinner than expected.','mike'),
(7,10,'5','Warm and soft, great for winter.','caleb');

-- =========================================
-- WISHLIST
-- =========================================

INSERT INTO wishlist(userid,productid)
VALUES
(3,1),
(4,5),
(5,10);

-- =========================================
-- CHAT
-- =========================================

INSERT INTO chat(reason,userid)
VALUES
('Question about Crew Socks thickness',3),
('Shipping inquiry for Over-the-Calf Socks',4),
('Sizing question for No-Show Socks',5),
('Material question about Athletic Socks',6),
('Care instructions for Wool Socks',7);





-- =========================================
-- USERS RUD
-- =========================================

-- READ
SELECT * FROM users;

SELECT * FROM users
WHERE userid = 1;

SELECT * FROM users
WHERE role = 'customer';

-- UPDATE
UPDATE users
SET username = 'littlejack'
WHERE userid = 1;

UPDATE users
SET role = 'admin'
WHERE userid = 3;

-- DELETE
DELETE FROM users
WHERE userid = 4;



-- =========================================
-- WARRANTY RUD
-- =========================================

-- READ
SELECT * FROM warranty;

SELECT * FROM warranty
WHERE warrantyid = 1;

-- UPDATE
UPDATE warranty
SET expire_date = '2028-01-01'
WHERE warrantyid = 1;

-- DELETE
DELETE FROM warranty
WHERE warrantyid = 4;



-- =========================================
-- PRODUCTS RUD
-- =========================================

-- READ
SELECT * FROM products;

SELECT * FROM products
WHERE productid = 1;

SELECT p.*, c.colorname, s.sizename
FROM products p
LEFT JOIN color c
ON p.colorid = c.colorid
LEFT JOIN size s
ON p.sizeid = s.sizeid;

-- SEARCH
SELECT * FROM products
WHERE title LIKE '%sock%';

-- FILTER
SELECT * FROM products
WHERE instock > 0;

SELECT * FROM products
WHERE price < 20.00;

-- UPDATE
UPDATE products
SET price = 15.00
WHERE productid = 1;

UPDATE products
SET instock = 50
WHERE productid = 2;

-- DELETE
DELETE FROM products
WHERE productid = 10;



-- =========================================
-- CART RUD
-- =========================================

-- READ
SELECT * FROM cart;

SELECT * FROM cart
WHERE userid = 3;

-- UPDATE
UPDATE cart
SET total = 100.00
WHERE cartid = 1;

-- DELETE
DELETE FROM cart
WHERE cartid = 3;



-- =========================================
-- CARTITEM RUD
-- =========================================

-- READ
SELECT * FROM cartitem;

SELECT ci.*, p.title, p.price
FROM cartitem ci
JOIN products p
ON ci.productid = p.productid;

-- UPDATE
UPDATE cartitem
SET quantity = 5
WHERE cartitemid = 1;

-- DELETE
DELETE FROM cartitem
WHERE cartitemid = 1;



-- =========================================
-- ORDERS RUD
-- =========================================

-- READ
SELECT * FROM orders;

SELECT * FROM orders
WHERE orderstatus = 'pending';

SELECT o.*, u.username
FROM orders o
JOIN cart c
ON o.cartid = c.cartid
JOIN users u
ON c.userid = u.userid;

-- UPDATE
UPDATE orders
SET orderstatus = 'confirmed'
WHERE orderid = 1;

UPDATE orders
SET orderstatus = 'shipped'
WHERE orderid = 2;

-- DELETE
DELETE FROM orders
WHERE orderid = 6;



-- =========================================
-- ORDERITEMS RUD
-- =========================================

-- READ
SELECT * FROM orderitems;

SELECT oi.*, p.title
FROM orderitems oi
JOIN products p
ON oi.productid = p.productid;

-- UPDATE
UPDATE orderitems
SET quantity = 4
WHERE orderitemid = 1;

-- DELETE
DELETE FROM orderitems
WHERE orderitemid = 5;



-- =========================================
-- REVIEW RUD
-- =========================================

-- READ
SELECT * FROM review;

SELECT r.*, p.title
FROM review r
JOIN products p
ON r.productid = p.productid;

SELECT * FROM review
WHERE rating = '5';

-- UPDATE
UPDATE review
SET reviewtext = 'Amazing socks'
WHERE reviewid = 1;

UPDATE review
SET rating = '4'
WHERE reviewid = 2;

-- DELETE
DELETE FROM review
WHERE reviewid = 5;



-- =========================================
-- WISHLIST RUD
-- =========================================

-- READ
SELECT * FROM wishlist;

SELECT w.*, p.title
FROM wishlist w
JOIN products p
ON w.productid = p.productid;

-- UPDATE
UPDATE wishlist
SET productid = 4
WHERE userid = 3
AND productid = 1;

-- DELETE
DELETE FROM wishlist
WHERE userid = 4
AND productid = 5;



-- =========================================
-- DISCOUNT RUD
-- =========================================

-- READ
SELECT * FROM discount;

SELECT * FROM discount
WHERE discountprice < 20.00;

-- UPDATE
UPDATE discount
SET discountprice = 5.00
WHERE discountid = 1;

UPDATE discount
SET length = '2026-12-31'
WHERE discountid = 2;

-- DELETE
DELETE FROM discount
WHERE discountid = 4;



-- =========================================
-- DISCOUNT_PRODUCTS RUD
-- =========================================

-- READ
SELECT * FROM discount_products;

SELECT dp.*, p.title
FROM discount_products dp
JOIN products p
ON dp.productid = p.productid;

-- UPDATE
UPDATE discount_products
SET productid = 2
WHERE discountid = 1
AND productid = 1;

-- DELETE
DELETE FROM discount_products
WHERE discountid = 1
AND productid = 2;



-- =========================================
-- COLOR RUD
-- =========================================

-- READ
SELECT * FROM color;

SELECT * FROM color
WHERE colorid = 1;

-- UPDATE
UPDATE color
SET colorname = 'purple'
WHERE colorid = 1;

-- DELETE
DELETE FROM color
WHERE colorid = 5;



-- =========================================
-- SIZE RUD
-- =========================================

-- READ
SELECT * FROM size;

SELECT * FROM size
WHERE sizename = 'medium';

-- UPDATE
UPDATE size
SET sizename = 'XXL'
WHERE sizeid = 1;

-- DELETE
DELETE FROM size
WHERE sizeid = 5;



-- =========================================
-- COMPLAINT RUD
-- =========================================

-- READ
SELECT * FROM complaint;

SELECT c.*, p.title, u.username
FROM complaint c
JOIN products p
ON c.productid = p.productid
JOIN users u
ON c.userid = u.userid;

-- UPDATE
UPDATE complaint
SET status = 'confrimed'
WHERE complaintid = 1;

UPDATE complaint
SET demand = 'refund'
WHERE complaintid = 2;

-- DELETE
DELETE FROM complaint
WHERE complaintid = 4;



-- =========================================
-- RETURNS RUD
-- =========================================

-- READ
SELECT * FROM returns;

SELECT r.*, o.orderstatus
FROM returns r
JOIN orders o
ON r.orderid = o.orderid;

-- UPDATE
UPDATE returns
SET status = 'approved'
WHERE returnid = 1;

UPDATE returns
SET complaint = 'Wrong item received'
WHERE returnid = 2;

-- DELETE
DELETE FROM returns
WHERE returnid = 3;



-- =========================================
-- CONVERSATION RUD
-- =========================================

-- READ
SELECT * FROM conversation;

SELECT c.*, u.username
FROM conversation c
JOIN users u
ON c.customerid = u.userid;

-- UPDATE
UPDATE conversation
SET adminid = 2
WHERE conversationid = 1;

-- DELETE
DELETE FROM conversation
WHERE conversationid = 3;



-- =========================================
-- MESSAGE RUD
-- =========================================

-- READ
SELECT * FROM message;

SELECT m.*, u.username
FROM message m
JOIN users u
ON m.senderid = u.userid;

-- UPDATE
UPDATE message
SET content = 'Updated message text'
WHERE messageid = 1;

-- DELETE
DELETE FROM message
WHERE messageid = 4;



-- =========================================
-- CHAT RUD
-- =========================================

-- READ
SELECT * FROM chat;

SELECT * FROM chat
WHERE userid = 3;

-- UPDATE
UPDATE chat
SET reason = 'Updated support message'
WHERE chatid = 1;

-- DELETE
DELETE FROM chat
WHERE chatid = 5;