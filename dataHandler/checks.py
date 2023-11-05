import sys
sys.dont_write_bytecode = True
import motor
import motor.motor_asyncio
from dataHandler import mongoCore

async def accessDegree(userID:int, companyName:str):
    db = await mongoCore.pullData()
    companyAccount = await db.company.find_one({"_id": companyName})
    degree = companyAccount["userAccess"][userID]
    return degree