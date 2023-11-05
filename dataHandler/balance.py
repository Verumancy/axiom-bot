import sys
sys.dont_write_bytecode = True
import motor
import motor.motor_asyncio
from dataHandler import mongoCore

class user:
    async def check(userID:int):
                db = await mongoCore.pullData()
                try:
                    userAccount = await db.user.find_one({"_id": userID})
                    balance = userAccount["balance"]
                    return balance
                except:
                    print(f"error: failed to find user {userID}")

    async def change(userID:int, value:int):
                db = await mongoCore.pullData()
                try:
                    balance = await user.check(userID)
                    await db.user.update_one(
                        {"_id": userID},
                        {"$set": {"balance": balance + value}}
                    )
                    return True
                except:
                    print(f"error: failed to change user {userID}'s balance by {value}")
                    return False

class company:
        async def check(companyName:str):
                db = await mongoCore.pullData()
                try:
                    companyAccount = await db.company.find_one({"_id":companyName})
                    balance = companyAccount["balance"]
                    return balance
                except:
                    print(f"error: failed to find company {companyName}")

        async def change(companyName:str, value:int):
                db = await mongoCore.pullData()
                try:
                    balance = await company.check(companyName)
                    await db.company.update_one(
                        {"_id": companyName},
                        {"$set": {"balance": balance + value}}
                    )
                    return True
                except:
                    print(f"error: failed to change company {companyName}'s balance by {value}")
                    return False