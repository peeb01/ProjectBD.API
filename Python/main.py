import subprocess

from fastapi import FastAPI, HTTPException
import pyodbc
import uvicorn
from datetime import date, datetime
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
#-------------------------------------------------INITIALIZATION--------------------------------------------#


DRIVER_NAME = 'ODBC Driver 17 for SQL Server'
SERVER_NAME = 'DESKTOP-M9VL3MH\SQLEXPRESS'
DATABASE_NAME = 'PP'
connection_string = f"DRIVER={{{DRIVER_NAME}}};SERVER={SERVER_NAME};DATABASE={DATABASE_NAME};Trusted_Connection=yes;"

conn = pyodbc.connect(connection_string)
cursor = conn.cursor()
app = FastAPI()

origins = [
    "http://localhost",  # Add your frontend's domain here
    "http://localhost:3000",  # Add more origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow any origin for testing (restrict this in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow any HTTP method for testing (restrict this in production)
    allow_headers=["*"],  # Allow any headers for testing (restrict this in production)
)

#-------------------------------------------------Masuer register -----------------------------------------#
class MasuerRegistration(BaseModel):
    fname: str
    lname: str
    dateOfBirth: str
    gender: str
    phoneNum: str
    email: str
    masuerType: str
    dayoff: str

def register_masuer(masuer_data: MasuerRegistration):
    data = cursor.execute("SELECT * FROM Masuer").fetchall()
    Id = len(data) + 1
    try:
        query = """
        INSERT INTO Masuer (masuerId, fname, lname, dateOfBirth, gender, phoneNum, email, massuertype, dayoff, statusNow)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (Id, masuer_data.fname, masuer_data.lname, datetime.strptime(masuer_data.dateOfBirth, "%Y-%m-%d").date(),
                              masuer_data.gender, masuer_data.phoneNum, masuer_data.email, masuer_data.masuerType, masuer_data.dayoff, 1))
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database error")

@app.post('/register-masuer')
def register_masuer_endpoint(new_masuer: MasuerRegistration):
    try:
        register_masuer(new_masuer)
        return {"message": "Masuer registered successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error: " + str(e))



#--------------------------------------------------REGISTER-------------------------------------------------#
class CustomerRegistration(BaseModel):
    username: str
    pasword: str
    fname: str
    lname: str
    dateOfBirth: str
    gender: str
    phoneNum: str
    email: str
    localPlace: str

def register_customer(customer_data : tuple):

    try:
        query = """
        INSERT INTO Customer (username, pasword, fname, lname, dateOfBirth, gender, phoneNum, email, localPlace, points)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, customer_data)
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database error")

@app.post('/register')
def register(new_customer : CustomerRegistration):
    try:
        customer_data = (
            new_customer.username,
            new_customer.pasword,
            new_customer.fname,
            new_customer.lname,
            datetime.strptime(new_customer.dateOfBirth, "%Y-%m-%d").date(),
            new_customer.gender,
            new_customer.phoneNum,
            new_customer.email,
            new_customer.localPlace,
            0
        )
        register_customer(customer_data)
        return {"message": "Customer registered successfully"}
    except:
        raise HTTPException(status_code=500, detail="Database failed.")



#----------------------------------------------------LOGIN----------------------------------------------#
class UserCredentials(BaseModel):
    username: str
    password: str


def verify_credentials(username: str, password: str) -> bool:
    try:

        query = "SELECT COUNT(*) FROM Customer WHERE username = ? AND pasword = ?"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()
        return result[0] > 0
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.post("/login")
async def login(credentials: UserCredentials):
    if verify_credentials(credentials.username, credentials.password):
        return {"message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

#--------------------------------------------------Masuer Login---------------------------------------------------#

class MasuerCredentials(BaseModel):
    Id: int
    masuerName : str

def verify_masuer(Id: str, masuerName: str) -> bool:

    try:

        query = "select count(*) from Masuer where masuerId = ? and fname = ?"
        cursor.execute(query, (Id, masuerName))
        result = cursor.fetchone()
        return result[0] > 0
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.post("/login-masuer")
async def loginMasuer(credentials: MasuerCredentials):
    if verify_masuer(credentials.Id, credentials.masuerName):
        return {"message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")


#---------------------------------------------------- MAIN PAGE --------------------------------------------------#
import json

def selectMasuer():
    try:
        query = """
                select M.masuerId, M.fname, M.lname, M.gender, M.massuertype
                from Masuer M
                where ( M.dayoff <> (select datename(weekday, getdate()) as CurrentDayOfWeek)) and (M.statusNow = 1) 
                """      
        cursor.execute(query)
        results = cursor.fetchall()
        # print(results)
        # df = pd.DataFrame(results, columns=['fname', 'lname', 'gender', 'massuertype'])
        # result_json = df.to_json(orient='index')

        dict_list = [{'ID' : item[0],'First Name': item[1], 'Last Name': item[2], 'Gender': item[3], 'Massage Type': item[4]} for item in results]
        result_json = json.dumps(dict_list, ensure_ascii=False, indent=5)
        return result_json
    except Exception as e:
        return str(e)

@app.get("/main")
async def main():
    try:
        result_json = selectMasuer() 
        return result_json
    except Exception as e:
        return {"error": str(e)}



#------------------------------------------------- SELECT MASSUER TYPE ---------------------------------------#
class MassuerType(BaseModel):
    massuertype : str

def selectType(massuerType):
    try:
        query = """
                select M.fname, M.lname
                from Masuer M
                where M.massuertype = ?
                """
        cursor.execute(query, (massuerType.massuertype,))
        results = cursor.fetchall()
        dict_list = [{'First Name': item[0], 'Last Name': item[1]} for item in results]
        results_json = json.dumps(dict_list, ensure_ascii=False, indent=2)
        return results_json
    except Exception as e:
        return str(e)

@app.post("/main/massuertype")
async def massuertype(mtype: MassuerType):
    try:
        results = selectType(mtype)
        return results
    except:
        raise HTTPException(status_code=500, detail="Nothing.")
    

#------------------------------------------------- Queue and next Time -------------------------------------------------------#
class selectDay(BaseModel):
    dateTimes: str
    massuertype: str

@app.post("/main/massuertype/selectnexttime")
async def select_next_time(select_day: selectDay):
    try:
        input_date_str = select_day.dateTimes
        massuertype = select_day.massuertype

        # Parse the date with the correct format (e.g., "2023-12-15")
        input_date = datetime.strptime(input_date_str, "%Y-%m-%d")

        day_of_week = input_date.strftime("%A")
        query = """
                select M.masuerId, M.fname, M.lname
                from Masuer M
                where M.dayoff <> ? and M.massuertype = ? and M.statusNow = 1
                """

        # Assuming you have a cursor and database connection set up
        cursor.execute(query, (day_of_week, massuertype))
        result = cursor.fetchall()
        dict_list = [{'ID': item[0], 'First Name': item[1], 'Last Name': item[2]} for item in result]

        # Return the result as JSON
        return dict_list
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

#-------------------------------------------- Buy, Booking -----------------------------------------#
from datetime import timedelta

class init_buy(BaseModel):
    username : str
    masuerId : int
    timewant : int      # minutes
    time_bookingwant : str


@app.post("/main/massuertype/selectnexttime/book-appointment")
async def book_appointment(booking_info: init_buy):

    username = booking_info.username
    masuerId = booking_info.masuerId
    timewant = booking_info.timewant
    timebookwill = datetime.strptime(booking_info.time_bookingwant, "%Y-%m-%d %H-%M-%S")
    execute_cursor = cursor.execute("select * from Booking").fetchall()
    bookingId = len(execute_cursor) + 1
    points = timewant

    if timewant < 30:
        return{"message": "Only bookings of more than 30 minutes are allowed."}
    current_time = datetime.now()
    # print(username, masuerId, timewant)
    # print(timebookwill)
    # print(current_time)
    if timebookwill <= current_time:
        return {"message": "Booking time must be after the current time."}

    timeout = timebookwill + timedelta(minutes=timewant)
    prices = timewant * 10
    try:
        current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')

        conflict_query = """
                        select count(*) from Booking
                        where masuerID = ? and
                              (Timeofout >= ? and Timemasuer <= ?)
                        """
        conflict_count = cursor.execute(conflict_query, (masuerId, timebookwill, timeout)).fetchone()[0]

        if conflict_count > 0:
            return {"message": "Booking conflicts with an existing appointment for the same masuerId."}

        points_query = "select points from Customer where username = ?"
        current_points = cursor.execute(points_query, username).fetchone()[0]
        

        new_points = current_points + points

        update_point = """
                update Customer
                set points = ?
                where username = ?
                """
        cursor.execute(update_point, (new_points, username))
        

        query = """
                insert into Booking (bookingId, username, masuerID, datTime, Timemasuer, Timeofout, prices)
                values (?, ?, ?, ?, ?, ?, ?)
                """
        cursor.execute(query, (bookingId, username, masuerId, current_time_str, timebookwill, timeout, prices))
        
        conn.commit()

        return {"message": "Appointment booked successfully"}
    except Exception as e:
        return {"message": f"Error: {str(e)}"}

#--------------------------------------------------Massuer Scheduling------------------------------------------#


class MassuerScheduiling(BaseModel):
    masuerId: int

@app.post("/main/massuerscheduling")
def selectMasuerScheduling(massuer: MassuerScheduiling):
    try:
        masuerId = massuer.masuerId

        current_time = datetime.now()

        query = """
                select M.fname, M.lname, C.fname, B.Timemasuer
                from Customer C, Masuer M, Booking B
                where (B.username = C.username) and (M.masuerId = B.masuerID) and (B.masuerID = ?) and (B.Timemasuer >= ?)
                """
        cursor.execute(query, (masuerId, current_time))
        result = cursor.fetchall()
        dict_list = [{'Masuer firstname': item[0], 'Masuer lastname': item[1], 'Customer name': item[2], 'start Time': item[3].isoformat()} for item in result]

        # Sort the results by 'start Time'
        sorted_dict_list = sorted(dict_list, key=lambda item: item['start Time'])

        return JSONResponse(content=sorted_dict_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
#------------------------------------------------- Massuer Salary ---------------------------------------------#
def getMassuerSalary():
    try:
        qeury = """
                select B.masuerID, B.massuerName, (sum(B.prices))*0.75 as TotalPrices
                from Booking B
                where B.Timemasuer >= dateadd(month, datediff(month, 0, getdate()), 0)
                group by B.masuerID, B.massuerName
                """
        cursor.execute(qeury)
        results = cursor.fetchall()
        
        dict_list = [{'Masuer ID': item[0],'Masuer Name': item[1], 'Total income': item[2]} for item in results]
        results_json = json.dumps(dict_list, ensure_ascii=False, indent=3)
        return results_json   
    except Exception as e:
        return str(e)

@app.get('/massuerSalary')
async def massuerSalary():
    try:
        result_json = getMassuerSalary()
        return result_json
    except Exception as e:
        return {"error": str(e)} 


#------------------------------------------------- Customer Review ---------------------------------------------#
class Reviews(BaseModel):
    username : str
    bookingId : int
    reviewsText : str

@app.post('/reviews')
def cusReview(review: Reviews):
    username = review.username
    text = review.reviewsText
    bookingId = review.bookingId
    ids = cursor.execute("select * from CustomerReview").fetchall()
    reviewId = len(ids) + 1
    current_time = datetime.now()
    try:
        query = """
                insert into CustomerReview(reviewId, username, reviewText, dateTim, bookingId)
                values (?, ?, ?, ?, ?)
                """

        cursor.execute(query, (reviewId, username, text, current_time, bookingId))
        conn.commit()

        return {"message": "Review inserted successfully"}
    except Exception as e:
        return {"message": f"Error: {str(e)}"}
    
class selectReview(BaseModel):
    username : str


@app.post('/selectreview')
def selectReviews(review: selectReview):
    try:
        qeury = """
                select B.bookingId, B.Timemasuer, B.prices
                from Booking B
                left join CustomerReview Cr on B.bookingId = Cr.bookingId
                where Cr.bookingId IS NULL
                and B.username = ?
                and B.Timeofout <= getdate();
                """
        cursor.execute(qeury, review.username)
        results = cursor.fetchall()
        
        dict_list = [{'Booking ID': item[0],'Time Masuee': str(item[1]), 'Prices':item[2]} for item in results]
        results_json = json.dumps(dict_list, ensure_ascii=False, indent=3)
        return results_json   
    except Exception as e:
        return str(e)

#------------------------------------------------- History -------------------------------------------------------#
class viewStory(BaseModel):
    username : str

@app.post('/viewhistory')
def getHistory(historys: viewStory):
    try:
        username = historys.username
        query = """
                select C.fname, M.fname, M.massuerType, B.Timemasuer 
                from Booking B, Masuer M, Customer C
                where (B.username = ?) and (B.username = C.username) and (B.masuerID = M.masuerId) 
                """
        cursor.execute(query, (username,))
        results = cursor.fetchall()
        dict_list = [{'Name': item[0], 'Masuer Name': item[1], 'Type': item[2], 'Time': item[3].isoformat()} for item in results]
        return JSONResponse(content=dict_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#------------------------------------------------- Massuer Income -------------------------------------------
def getMassuerIncome():
    try:
        qeury = """
                select B.masuerID, sum(B.prices) as TotalPrices
                from Booking B
                where B.Timemasuer >= dateadd(month, datediff(month, 0, getdate()), 0) and B.Timeofout <= getdate()
                group by B.masuerID
                """
        cursor.execute(qeury)
        results = cursor.fetchall()
        
        dict_list = [{'Masuer ID': item[0], 'Total income': item[1]} for item in results]
        sorted_dict_list = sorted(dict_list, key=lambda x: x['Total income'], reverse=True)

        return JSONResponse(sorted_dict_list)

    except Exception as e:
        return str(e)

@app.get('/massuerIncome')
async def massuerIncome():
    try:
        result_json = getMassuerIncome()
        return result_json
    except Exception as e:
        return {"error": str(e)}

#------------------------------------------------- Bonus -------------------------------------------------------#
class Bonus(BaseModel):
    masuerId : int

@app.post('/masuerbonus')
def bonusCalculator(Bonus: Bonus):
    try:
        masuerId = Bonus.masuerId
        query = """
                SELECT M.fname, SUM(B.prices) * 0.15 AS BonusPrices
                FROM Booking B
                INNER JOIN Masuer M ON B.masuerID = M.masuerId
                WHERE B.masuerID = ?
                    AND CONVERT(DATE, B.Timeofout) >= DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()), 0) -- 1st day of the current month
                    AND CONVERT(DATE, B.Timeofout) <= CAST(GETDATE() AS DATE) -- Current date
                GROUP BY M.fname;
                """
        cursor.execute(query, (masuerId,))
        results = cursor.fetchall()
        dict_list = [{'Name': item[0], 'Salary': 15500, 'Bonus': item[1]} for item in results]
        return JSONResponse(content=dict_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/allmasuerbonus')
def getAllMasuerBonus():
    try:
        qeury = """
                SELECT M.fname, SUM(B.prices) * 0.15 AS BonusPrices
                FROM Booking B
                INNER JOIN Masuer M ON B.masuerID = M.masuerId
                WHERE CONVERT(DATE, B.Timeofout) >= DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()), 0) -- 1st day of the current month
                    AND CONVERT(DATE, B.Timeofout) <= CAST(GETDATE() AS DATE) -- Current date
                GROUP BY M.fname;

                """
        cursor.execute(qeury)
        results = cursor.fetchall()
            
        dict_list = [{'Name': item[0], 'Salary': 15500, 'Bonus': item[1]} for item in results]
        return JSONResponse(dict_list)
    
    except Exception as e:
        return str(e)
#------------------------------------------------- GET TABLE -------------------------------------------------------#
@app.get('/getMasuer')
def getMasuer():
    try: 
        query = """
                select M.masuerId, M.fname, M.lname, M.massuertype from Masuer M
                """
        cursor.execute(query)
        results = cursor.fetchall()

        dict_list = [{'ID': item[0], 'name': item[1] + ' ' + item[2], 'Type': item[3]} for item in results]
        return JSONResponse(dict_list)
    except Exception as e:
        return str(e)

@app.get('/getCustomer')
def getCustomer():
    try:
        query = """
                select C.username, C.pasword, C.fname, C.lname from Customer C
                """
        cursor.execute(query)
        results = cursor.fetchall()
        dict_list = [{'Username': item[0], 'Password': item[1], 'Name': item[2] + ' ' + item[3]} for item in results]
        return JSONResponse(dict_list)
    except Exception as e:
        return str(e)
    
@app.get('/getBooking')
def getBook():
    try:
        query = """
                select B.bookingId, B.username, B.masuerID, B.prices from Booking B
                """
        cursor.execute(query)
        results = cursor.fetchall()
        dict_list = [{'Booking ID': item[0], 'Username': item[1], 'Masuer ID': item[2], 'Prices': item[3]} for item in results]
        return JSONResponse(dict_list)
    except Exception as e:
        return str(e)

@app.get('/getCustomerReview')
def getCusReview():
    try:
        query = """
                select R.reviewId, R.username, R.bookingId, R.reviewText from CustomerReview R
                """
        cursor.execute(query)
        results = cursor.fetchall()
        dict_list = [{'Review ID': item[0], 'Username': item[1], 'Booking ID': item[2], 'Text':item[3]} for item in results]
        return JSONResponse(dict_list)
    except Exception as e:
        return str(e)
    
    
#------------------------------------------------- RUN -------------------------------------------------------#

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
