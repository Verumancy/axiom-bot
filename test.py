import dataHandler
import asyncio
async def test(ticker):
    db = await dataHandler.mongoCore.pullData()
    stock = await db.stock.find_one({"_id": ticker})
    if stock:
        prevValues = stock["prevPrices"]
        print(prevValues)

asyncio.run(test("ABC"))