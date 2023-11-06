CREATE TABLE Customer (
    username varchar(255) Primary Key,
    password varchar(255),
    fname varchar(255) not null,
    lname varchar(255) not null,
    dateOfBirth date not null,
    gender varchar(1) not null,
    phoneNum varchar(255) not null,
    email varchar(255),
    localPlace varchar(255),
    points int
);

CREATE TABLE Masuer (
    masuerId int Primary Key,
    fname varchar(255) not null,
    lname varchar(255) not null,
    dateOfBirth date not null,
    gender varchar(1) not null,
    phoneNum varchar(255) not null,
    email varchar(255),
    massuertype varchar(255) not null,
    dayoff varchar(255) not null,
    statusNow bit not null
);

CREATE TABLE Booking (
    bookingId int Primary Key,
    username varchar(255) not null,
    masuerID int not null,
    dateTime smalldatetime not null,
    Timeofmasuer smalldatetime not null,
    Timeofcheckout smalldatetime not null,
    prices float not null,
    Foreign Key (username) References Customer(username),
    Foreign Key (masuerID) References Masuer(masuerId)
);

CREATE TABLE CustomerReview (
    reviewId int Primary Key,
    username varchar(255) not null,
    bookingId int not null,
    reviewText varchar(255) not null,
    dateTime smalldatetime,
    Foreign Key (username) References Customer(username),
    Foreign Key (bookingId) References Booking(bookingId)
);


