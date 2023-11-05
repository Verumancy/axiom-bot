import sys
sys.dont_write_bytecode = True
import motor
import motor.motor_asyncio

with open("mongoURL.txt") as f: url = f.readline()

#Pulls Data from mongo DB database
async def pullData():
    data = motor.motor_asyncio.AsyncIOMotorClient(url)["axiomDB"]
    return data