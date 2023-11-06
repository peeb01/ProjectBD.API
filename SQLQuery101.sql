create table Customer(
	username varchar(255) int Primary Key,
	pasword varchar(255),
	fname varchar(255) not null,
	lname varchar(255) not null,
	dateOfBirth date not null,
	gender varchar(1) not null,
	phoneNum varchar(255) not null,
	email varchar(255),
	localPlace varchar(255),
	points int
);


create table Masuer(
	masuerId int Primary Key,
	fname varchar(255) not null,
	lname varchar(255) not null,
	dateOfBirth date not null,
	gender varchar(1) not null,
	phoneNum varchar(255) not null,
	email varchar(255),
	massuertype varchar(255) not null,
	dayoff varchar not null,
	statusNow bit not null,

);

create table Booking(
	bookingId int Primary Key,
	username varchar(255) not null,
	masuerID int not null,
	datTime smalldatetime not null,
	Timemasuer smalldatetime not null, 
	Timeofout smalldatetime not null,
	prices float not null,
	Foreign Key (username) References Customer(username),
	Foreign Key (masuerID) References Masuer(masuerId)
);

create table CustomerReview(
	reviewId int Primary Key,
	username varchar(255) not null,
	bookingId int not null,
	reviewText varchar(255) not null,
	dateTim smalldatetime,
	Foreign Key (username) References Customer(username),
	Foreign Key (bookingId) References Booking(bookingId)
	
);


