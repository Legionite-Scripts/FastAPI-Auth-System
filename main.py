from fastapi import FastAPI, Request, HTTPException, Depends, Form
import bcrypt
from pymongo import MongoClient
from pymongo.collection import Collection
from datetime import timedelta
from jwtHandler import createAccessToken
from jwtHandler import createResetToken
from jwtHandler import decodeResetToken
from dotenv import load_dotenv
from utils.email_utils import send_reset_email
import os

from typing import Dict
from schema import (
    SignupRequest,
    LoginRequest,
    ForgotPasswordRequest,
)

app = FastAPI()
load_dotenv()
database_url = os.getenv("DATABASE_URL")

# Connect to MongoDB
client = MongoClient(database_url)
db = client["user"]  # DB
signupCollection: Collection = db["signupDetails"]  # Collection/Table name


@app.get("/")
def read_root():
    return {"message": "FastAPI Application is up and running"}


@app.post("/signup")
async def userSignup(signup_request: SignupRequest):
    try:
        # Extract data from the request
        name = signup_request.name
        email = signup_request.email
        password = signup_request.password

        # Check if the email already exists in the database
        existing_user = signupCollection.find_one({"email": email})
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Account already exists.",
            )

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        # Convert the hash to a string before storing it
        hashed_password_str = hashed_password.decode("utf-8")

        # Insert Data into MongoDB
        result = signupCollection.insert_one(
            {"name": name, "email": email, "password": hashed_password_str}
        )

        # Return success message with inserted ID
        return {
            "message": "Successful",
            "data": {"id": str(result.inserted_id), "name": name, "email": email},
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail="Signup Error")


@app.post("/login")
async def userLogin(login_request: LoginRequest):
    try:
        email = login_request.email
        password = login_request.password

        # Check if the account exists in the database
        user = signupCollection.find_one({"email": email})
        if user:
            # User exists, now verify the password
            hashed_password = user[
                "password"
            ]  # Get the hashed password from the database

            # Check if the entered password matches the hashed password
            if not bcrypt.checkpw(
                password.encode("utf-8"), hashed_password.encode("utf-8")
            ):
                raise HTTPException(status_code=400, detail="Incorrect password.")

            # Create access token
            access_token_expires = timedelta(minutes=30)
            access_token = createAccessToken(
                data={"sub": email}, expires_delta=access_token_expires
            )

            # Return success message with access token
            return {
                "message": "Login successful",
                "access_token": access_token,
                "token_type": "bearer",
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Account doesn't exist. Please create an account.",
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail="Login Error")


@app.post("/forgotPassword")
async def forgotPassword(forgot_password_request: ForgotPasswordRequest):
    try:
        email = forgot_password_request.email

        # Check if the user exists in the database
        existing_user = signupCollection.find_one({"email": email})
        if existing_user:
            # Generate a password reset token
            reset_token = createResetToken(email)
            reset_link = f"http://localhost:8000/reset-password?token={reset_token}"

            # Send the password reset email
            send_reset_email(email, reset_link)

            return {"message": "Password reset email sent successfully!"}
        else:
            raise HTTPException(
                status_code=404, detail="Error: Account Does not Exist."
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/reset-password")
async def reset_password(token: str = Form(...), new_password: str = Form(...)):
    try:
        # Verify the reset token
        email = decodeResetToken(token)
        if not email:
            raise HTTPException(status_code=400, detail="Invalid or expired token")

        # Hash the new password
        hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
        hashed_password_str = hashed_password.decode("utf-8")

        # Update the password in the database
        result = signupCollection.update_one(
            {"email": email}, {"$set": {"password": hashed_password_str}}
        )

        if result.modified_count == 1:
            return {"message": "Password has been reset successfully"}
        else:
            raise HTTPException(status_code=400, detail="Password reset failed")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/displayStuff")
def display():
    print("Sharpiru")
