import sys
sys.dont_write_bytecode = True
import motor
import motor.motor_asyncio
import asyncio
import mongoCore

async def registerUser(userID:int):
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
    except:
        print(f"error: failed to register user {userID}")
        
async def registerCompany(companyName:str, ownerID:int):
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
    except:
        print(f"error: failed to register company {companyName}")

asyncio.run(registerCompany("Axiom", 123456789))

    