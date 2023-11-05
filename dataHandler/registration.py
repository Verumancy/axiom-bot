import sys
sys.dont_write_bytecode = True
import motor
import motor.motor_asyncio
from dataHandler import mongoCore

async def user(userID:int):
    db = await mongoCore.pullData()
    post={
                "_id": userID,
                "balance": 0,
                "creditScore": 600,
                "accountTier": 0,
                "lockBoxSubscription": False,
                "loans": {},
            }
    try: 
        await db.user.insert_one(post)
        return True
    except:
        print(f"error: failed to register user {userID}")
        
async def company(companyName:str, ownerID:int):
    db = await mongoCore.pullData()
    post = {
                "_id": companyName,
                "balance": 0,
                "publicTicker": None,
                "userAccess": {
                    f"{ownerID}": 1
                }
    }
    try: 
        await db.company.insert_one(post)
        return True
    except:
        print(f"error: failed to register company {companyName}")
        return False