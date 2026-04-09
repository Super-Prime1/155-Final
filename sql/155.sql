create database online_store;
use online_store;
SET FOREIGN_KEY_CHECKS = 0;

create table pendingusers(
name varchar(255)not null,
email varchar(255) not null,
username varchar(255) not null,
password varchar(255) not null,
userid int primary key auto_increment,
role enum ("admin","vendor","customer")
);

create table users(
name varchar(255)not null,
email varchar(255) not null,
username varchar(255) not null,
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
length date not null,
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
 )




--admin
insert into users (name, email, username,password, userid, role)
values ('jackson', 'jackson12@gmail.com', 'bigjack', 'jackjack', 1, 'admin');

insert into users (name, email, username,password, userid, role)
values ('joshua', 'joshua12@gmail.com', 'littlejoshua', 'joshua', 2, 'admin');

--customers
insert into users (name, email, username,password, userid, role)
values ('manuel', 'manuel12@gmail.com', 'bigmanuel', 'manuel1', 3, 'customer');

insert into users (name, email, username,password, userid, role)
values ('collin', 'collin12@gmail.com', 'littlecollin', 'collin1', 4, 'customer');

insert into users (name, email, username,password, userid, role)
values ('steve', 'steve12@gmail.com', 'bigsteve', 'steve1', 5, 'customer');

insert into users (name, email, username,password, userid, role)
values ('mike', 'mike12@gmail.com', 'bigmike', 'mike1', 6, 'customer');

insert into users (name, email, username,password, userid, role)
values ('caleb', 'caleb12@gmail.com', 'bigcaleb', 'caleb1', 7, 'customer');

--vendors
insert into users (name, email, username,password, userid, role)
values ('owen', 'owen12@gmail.com', 'bigowen', 'owen1', 8, 'vendor');

insert into users (name, email, username,password, userid, role)
values ('jim', 'jim12@gmail.com', 'bigjim', 'jim1', 9, 'vendor');

insert into users (name, email, username,password, userid, role)
values ('clairel', 'claire12@gmail.com', 'bigclaire', 'claire1', 10, 'vendor');


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


-- untimed discount on 2
-- products and timed discount on 2 more, some items added
-- to cart in 3 customer accounts, at least 7 orders (with
-- different order status) and 3 shipped orders from at least 3
-- customers some orders must have multiple products from multiple
-- vendors

INSERT INTO warranty (expire_date) VALUES
('2027-01-01'),
('2027-06-01'),
('2028-01-01'),
('2028-06-01');


INSERT INTO products (title, description, price, instock, warrantyid) VALUES
("Crew Socks", "A pair of crew socks", 10.00, 100, 1),
("Ankle Socks", "A pair of ankle socks", 20.00, 50, 2),
("No‑Show Socks", "A pair of no-show socks", 30.00, 25, 3),
("Knee‑High Socks", "A pair of knee-high socks", 15.00, 75, 4),
("Over‑the‑Calf Socks", "A pair of over-the-calf socks", 15.00, 75, 4),
("Compression Socks", "A pair of compression socks", 12.00, 80, 1),
("Dress Socks", "A pair of dress socks", 18.00, 60, 2),
("Athletic Socks", "A pair of athletic socks", 14.00, 90, 3),
("Hiking Socks", "A pair of hiking socks", 22.00, 40, 4),
("Wool Socks", "A pair of wool socks", 25.00, 30, 1);



INSERT INTO discount (length, discountprice, price, productid) VALUES
('NULL', 8.00, 10.00, 1),
('NULL', 15.00, 18.00, 7),
('2026-12-31', 16.00, 20.00, 2),
('2026-12-31', 25.00, 30.00, 3),


