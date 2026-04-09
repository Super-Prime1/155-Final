create database online_store;
use online_store;
SET FOREIGN_KEY_CHECKS = 0;

create table pendingusers(
name varchar(255)not null,
email varchar(255) not null unique,
username varchar(255) not null unique,
password varchar(255) not null,
userid int primary key auto_increment,
role enum ("admin","vendor","customer")
);

create table users(
name varchar(255)not null,
email varchar(255) not null unique,
username varchar(255) not null unique,
password varchar(255) not null,
userid int primary key auto_increment,
role enum ("admin","vendor","customer")
);

create table warranty(
expire_date date not null,
warrantyid int primary key auto_increment
);

create table chat(
chatid int not null primary key auto_increment,
reason varchar(255) not null,
userid int,
FOREIGN KEY (userid) REFERENCES users(userid)
);

create table cart(
cartid int primary key auto_increment,
total decimal(10,2) not null,
userid int not null,
FOREIGN KEY (userid) REFERENCES users(userid)
);


create table orders(
date date not null,
total decimal (10,2) not null,
orderstatus enum("pending","confirmed","handed to partner","shipped"),
cartid int not null,
FOREIGN KEY (cartid) REFERENCES cart(cartid),
orderid int primary key auto_increment 
);

create table products(
title varchar(255) not null,
description varchar(255) not null,
productid int not null primary key auto_increment,
price decimal(10,2) not null,
instock int not null,
image varchar(500),
warrantyid int,
FOREIGN KEY (warrantyid) REFERENCES warranty(warrantyid),
vendorid INT NOT NULL,
FOREIGN KEY (vendorid) REFERENCES users(userid)
);


create table returns(
complaint varchar(255) not null,
returnid int primary key auto_increment,
date date not null,
title varchar(255)not null,
orderid int not null,
FOREIGN KEY (orderid) REFERENCES orders(orderid),
description varchar(255) not null,
image varchar(500),
type enum("refund","return","warranty")
);

create table discount(
discountid int not null primary key auto_increment,
length date null,
discountprice decimal(10,2) not null,
price decimal(10,2) not null,
productid int not null,
FOREIGN KEY (productid) REFERENCES products(productid)
);

create table color(
colorid int primary key auto_increment,
productid int not null,
FOREIGN KEY (productid) REFERENCES products(productid),
colorname varchar(255) not null
);

create table cartitem(
cartitemid int primary key auto_increment,
cartid int not null,
FOREIGN KEY (cartid) REFERENCES cart(cartid),
productid int not null,
FOREIGN KEY (productid) REFERENCES products(productid),
quantity int not null
);

 create table orderitems(
 orderitemid int primary key auto_increment,
 orderid int not null,
 FOREIGN KEY (orderid) REFERENCES orders(orderid),
 productid int not null,
 FOREIGN KEY (productid) REFERENCES products(productid),
 quantity int not null,
 price decimal(10,2) not null
 );


create table review (
    reviewid INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    userid INT NOT NULL,
    productid INT NOT NULL,
    rating ENUM('1','2','3','4','5') NOT NULL,
    reviewtext VARCHAR(255) NOT NULL,
    FOREIGN KEY (userid) REFERENCES users(userid),
    FOREIGN KEY (productid) REFERENCES products(productid)
);


--admin
insert into users (name, email, username,password, role)
values ('jackson', 'jackson12@gmail.com', 'bigjack', 'jackjack', 'admin');

insert into users (name, email, username,password, role)
values ('joshua', 'joshua12@gmail.com', 'littlejoshua', 'joshua', 'admin');

--customers
insert into users (name, email, username,password, role)
values ('manuel', 'manuel12@gmail.com', 'bigmanuel', 'manuel1', 'customer');

insert into users (name, email, username,password, role)
values ('collin', 'collin12@gmail.com', 'littlecollin', 'collin1', 'customer');

insert into users (name, email, username,password, role)
values ('steve', 'steve12@gmail.com', 'bigsteve', 'steve1', 'customer');

insert into users (name, email, username,password, role)
values ('mike', 'mike12@gmail.com', 'bigmike', 'mike1', 'customer');

insert into users (name, email, username,password, role)
values ('caleb', 'caleb12@gmail.com', 'bigcaleb', 'caleb1', 'customer');

--vendors
insert into users (name, email, username,password, role)
values ('owen', 'owen12@gmail.com', 'bigowen', 'owen1', 'vendor');

insert into users (name, email, username,password, role)
values ('jim', 'jim12@gmail.com', 'bigjim', 'jim1', 'vendor');

insert into users (name, email, username,password, role)
values ('clairel', 'claire12@gmail.com', 'bigclaire', 'claire1', 'vendor');


SHOW TABLES;
SELECT * FROM cart;
SELECT * FROM cartitem;
SELECT * FROM chat;
SELECT * FROM cartitem;
SELECT * FROM color;
SELECT * FROM discount;
SELECT * FROM orderitems;
SELECT * FROM orders;
SELECT * FROM products;
SELECT * FROM returns;
SELECT * FROM users;
SELECT * FROM warranty;



INSERT INTO warranty (expire_date) VALUES
('2027-01-01'),
('2027-06-01'),
('2028-01-01'),
('2028-06-01');


INSERT INTO products (title, description, price, instock, warrantyid, vendorid) VALUES
("Crew Socks", "A pair of crew socks", 10.00, 100, 1, 8),
("Ankle Socks", "A pair of ankle socks", 20.00, 50, 2, 9),
("No-Show Socks", "A pair of no-show socks", 30.00, 25, 3, 10),
("Knee-High Socks", "A pair of knee-high socks", 15.00, 75, 4, 8),
("Over-the-Calf Socks", "A pair of over-the-calf socks", 15.00, 75, 4, 9),
("Compression Socks", "A pair of compression socks", 12.00, 80, 1, 10),
("Dress Socks", "A pair of dress socks", 18.00, 60, 2, 8),
("Athletic Socks", "A pair of athletic socks", 14.00, 90, 3, 9),
("Hiking Socks", "A pair of hiking socks", 22.00, 40, 4, 10),
("Wool Socks", "A pair of wool socks", 25.00, 30, 1, 8);



INSERT INTO discount (length, discountprice, price, productid) VALUES
(NULL, 8.00, 10.00, 1),
(NULL, 15.00, 18.00, 7),
('2026-12-31', 16.00, 20.00, 2),
('2026-12-31', 25.00, 30.00, 3);


insert into cart (total, userid) 
values (0.00, 4);

INSERT INTO cartitem (cartid, productid, quantity)
VALUES
(1, 5, 2),   -- Over-the-Calf Socks
(1, 9, 1);   -- Hiking Socks


INSERT INTO cart (total, userid)
VALUES (0.00, 3);

INSERT INTO cartitem (cartid, productid, quantity)
VALUES
(2, 1, 2),   -- Crew Socks
(2, 7, 1);   -- Dress Socks



INSERT INTO cart (total, userid)
VALUES (0.00, 5);

INSERT INTO cartitem (cartid, productid, quantity)
VALUES
(3, 3, 1),   -- No-Show Socks
(3, 10, 2);  -- Wool Socks


-- ORDER 1 — pending (user 4, cartid 1)
INSERT INTO orders (date, total, orderstatus, cartid)
VALUES ('2026-04-09', 44.00, 'pending', 1);

INSERT INTO orderitems (orderid, productid, quantity, price)
VALUES
(1, 5, 2, 15.00),   -- Over-the-Calf Socks
(1, 9, 1, 22.00);   -- Hiking Socks


-- ORDER 2 — confirmed (user 3, cartid 2)
INSERT INTO orders (date, total, orderstatus, cartid)
VALUES ('2026-04-09', 38.00, 'confirmed', 2);

INSERT INTO orderitems (orderid, productid, quantity, price)
VALUES
(2, 1, 2, 10.00),   -- Crew Socks
(2, 7, 1, 18.00);   -- Dress Socks


-- ORDER 3 — handed to partner (user 5, cartid 3)
INSERT INTO orders (date, total, orderstatus, cartid)
VALUES ('2026-04-09', 80.00, 'handed to partner', 3);

INSERT INTO orderitems (orderid, productid, quantity, price)
VALUES
(3, 3, 1, 30.00),   -- No-Show Socks
(3, 10, 2, 25.00);  -- Wool Socks


-- ORDER 4 — shipped (user 4)
INSERT INTO orders (date, total, orderstatus, cartid)
VALUES ('2026-04-09', 20.00, 'shipped', 1);

INSERT INTO orderitems (orderid, productid, quantity, price)
VALUES
(4, 2, 1, 20.00);   -- Ankle Socks


-- ORDER 5 — shipped (user 3)
INSERT INTO orders (date, total, orderstatus, cartid)
VALUES ('2026-04-09', 12.00, 'shipped', 2);

INSERT INTO orderitems (orderid, productid, quantity, price)
VALUES
(5, 6, 1, 12.00);   -- Compression Socks


-- ORDER 6 — shipped (user 5)
INSERT INTO orders (date, total, orderstatus, cartid)
VALUES ('2026-04-09', 14.00, 'shipped', 3);

INSERT INTO orderitems (orderid, productid, quantity, price)
VALUES
(6, 8, 1, 14.00);   -- Athletic Socks


-- ORDER 7 — pending (multi-vendor, user 4)
INSERT INTO orders (date, total, orderstatus, cartid)
VALUES ('2026-04-09', 53.00, 'pending', 1);

INSERT INTO orderitems (orderid, productid, quantity, price)
VALUES
(7, 4, 1, 15.00),   -- Knee-High Socks
(7, 7, 1, 18.00),   -- Dress Socks
(7, 1, 2, 10.00);   -- Crew Socks



INSERT INTO review (userid, productid, rating, reviewtext) VALUES
(3, 1, '5', 'Great quality and very comfortable.'),
(4, 5, '4', 'Good socks, fit well.'),
(5, 3, '5', 'Perfect no-show socks, don’t slip.'),
(6, 7, '3', 'Decent but thinner than expected.'),
(7, 10, '5', 'Warm and soft, great for winter.');


insert into returns (complaint, date, title, orderid, description, image, type)
values ('Received wrong item', '2026-04-10', 'Wrong Item Received', 
1, 'I ordered over-the-calf socks but received knee-high socks instead.', 'knee-high-socks.png', 'return');


insert into returns (complaint, date, title, orderid, description, image, type) values ('Received defective item', '2026-04-11', 'Defective Item Received',
2, 'The crew socks I received have holes in them.', 'defective-sock.png', 'warranty');



INSERT INTO chat (reason, userid) VALUES
('Question about Crew Socks thickness', 3),
('Shipping inquiry for Over-the-Calf Socks', 4),
('Sizing question for No-Show Socks', 5),
('Asking about Knee-High Socks restock', 6),
('Material question about Athletic Socks', 7),
('Care instructions for Wool Socks', 3),
('Return request for Crew Socks', 4),
('Durability question about Hiking Socks', 5),
('Bulk order discount inquiry for Dress Socks', 6),
('Compression Socks suitability for long flights', 7);


INSERT INTO chat (reason, userid) VALUES
('Response: Crew Socks thickness explanation', 8),
('Response: Shipping update for Over-the-Calf Socks', 9),
('Response: No-Show Socks sizing guidance', 10),
('Response: Knee-High Socks restock info', 8),
('Response: Athletic Socks material details', 9),
('Response: Wool Socks care instructions', 10),
('Response: Crew Socks return approval', 8),
('Response: Hiking Socks durability info', 9),
('Response: Dress Socks bulk discount info', 10),
('Response: Compression Socks flight suitability', 8),
('Admin support: general assistance offered', 1),
('Admin support: return request acknowledged', 2);