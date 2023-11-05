import sys
sys.dont_write_bytecode = True
import motor
import motor.motor_asyncio
from dataHandler import mongoCore, balance
import decimal

class management:

    async def register(parentAccount:str, primaryShareHolderID:int, stockTicker:str, shareCount:int, ipo: int):
        db = await mongoCore.pullData()

        post = {
            "_id": stockTicker,
            "parentCompany": parentAccount,
            "shareCount": shareCount,
            "stockPrice": ipo,
            "prevPrices": [ipo],
            "stockHolders": {str(primaryShareHolderID): shareCount},
            "orders": {"sell":{}, "buy":{}}
            }
        try:
            await db.stock.insert_one(post)
            await db.company.update_one(
                    {"_id": parentAccount},
                    {"$set": {"publicTicker": stockTicker}}
                    )
            return True
        except:
            print(f"error: failed to create stock {stockTicker}")
            return False

class orders:
    class sell:
        async def addShares(userID:int, ticker:str, shareCount:int, price:int):
            db = await mongoCore.pullData()
            marketInfo = await db.market.find_one({"_id": "marketInfo"})
            stock = await db.stock.find_one({"_id": ticker})
            if stock:
                userCount = stock["stockHolders"][str(userID)]
                if userCount >= shareCount:
                    if price == 0:
                        price = stock["stockPrice"] - marketInfo["decFactor"]
                    existingStocksInOrder:int
                    try:
                        existingStocksInOrder = stock["orders"]["sell"][str(userID)]["shareCount"]
                    except:
                        existingStocksInOrder = 0
                    newCount = existingStocksInOrder + shareCount
                    await db.stock.update_one(
                        {"_id": ticker},
                        {"$set":{f"orders.sell.{userID}":{"shareCount": newCount, "price":price}}})
                    userCount -= shareCount
                    if userCount !=0:
                        await db.stock.update_one(
                            {"_id": ticker},
                            {"$set":{f"stockHolders.{userID}": userCount}})
                    else: 
                        await db.stock.update_one(
                            {"_id": ticker},
                            {"$unset":{f"stockHolders.{userID}": 1}})
                    return True
            return False
        
        async def removeShares(userID:int, ticker:str, shareCount:int):
            db = await mongoCore.pullData()
            marketInfo = await db.market.find_one({"_id": "marketInfo"})
            stock = await db.stock.find_one({"_id": ticker})
            if stock:
                userCount = stock["stockHolders"][str(userID)]
                existingStocksInOrder:int
                try:
                    existingStocksInOrder = stock["orders"]["sell"][str(userID)]["shareCount"]
                except:
                    return False
                if existingStocksInOrder - shareCount < 0 or shareCount == 0:
                    shareCount = existingStocksInOrder
                if existingStocksInOrder != 0:
                    price = stock["orders"]["sell"][str(userID)]["price"]
                    newCount = existingStocksInOrder - shareCount
                    if newCount != 0:
                        await db.stock.update_one(
                            {"_id": ticker},
                            {"$set":{f"orders.sell.{userID}":{"shareCount": newCount, "price":price}}})
                    else: 
                        await db.stock.update_one(
                            {"_id": ticker},
                            {"$umset":{f"orders.sell.{userID}":1}})
                    userCount += shareCount
                    await db.stock.update_one(
                        {"_id": ticker},
                        {"$set":{f"stockHolders.{userID}": userCount}})
                    return True
            return False
        
        async def editPrice(userID:int, ticker:str, price:int):
                print("attempting")
                db = await mongoCore.pullData()
                marketInfo = await db.market.find_one({"_id": "marketInfo"})
                stock = await db.stock.find_one(({"_id": ticker}))
                if stock:
                    if price == 0:
                        price = stock["stockPrice"] - marketInfo["decFactor"]
                    
                    exists = await db.stock.find_one({"$and": [{"_id":ticker}, {f"orders.sell.{userID}": {"$exists": True}}]})
                    if exists:
                        await db.stock.update_one(
                            {"_id": ticker},
                            {"$set":{f"orders.sell.{userID}.price": price}})
                        return True
                return False
    
    class buy:
        async def addShares(userID:int, ticker:str, shareCount:int, price:int):
            db = await mongoCore.pullData()
            marketInfo = await db.market.find_one({"_id": "marketInfo"})
            stock = await db.stock.find_one({"_id": ticker})
            if stock:
                if shareCount <= stock["shareCount"]:
                    buyerBal = await balance.user.check(userID)
                    if price == 0:
                        price = stock["stockPrice"] + marketInfo["incFactor"]
                            
                    existingStocksInOrder:int
                    existingDepositAmount:int
                    try:
                        existingStocksInOrder = stock["orders"]["buy"][str(userID)]["shareCount"]
                        existingDepositAmount = stock["orders"]["buy"][str(userID)]["deposit"]
                    except:
                        existingStocksInOrder = 0
                        existingDepositAmount = 0

                    newCount = existingStocksInOrder + shareCount
                    deposit = newCount*price
                    takeAmount = deposit - existingDepositAmount
                    if buyerBal >= takeAmount:
                        await db.stock.update_one(
                            {"_id": ticker},
                            {"$set":{f"orders.buy.{userID}":{"shareCount": newCount, "price":price, "deposit": deposit}}})
                        await balance.user.change(userID, -takeAmount)
                        return True
            return False
        
        async def removeShares(userID:int, ticker:str, shareCount:int):
                db = await mongoCore.pullData()
                stock = await db.stock.find_one(({"_id": ticker}))
                if stock:
                    oldCount = stock["orders"]["buy"][str(userID)]["shareCount"]
                    if oldCount:
                        if shareCount == 0:
                            shareCount = oldCount
                        newCount = oldCount-shareCount
                        deposit = stock["orders"]["buy"][str(userID)]["deposit"]
                        sharePrice = stock["orders"]["buy"][str(userID)]["price"]
                        if newCount < 0: shareCount=0
                        if newCount != 0:
                            newDep = deposit - (shareCount*sharePrice)
                            await db.stock.update_one(
                                {"_id": ticker},
                                {"$set":{f"orders.buy.{userID}":{"shareCount": newCount, "price":sharePrice, "deposit": newDep}}})
                            await balance.user.change(userID, shareCount*sharePrice)
                        else:
                            await db.stock.update_one(
                                    {"_id": ticker},
                                    {"$unset":{f"orders.buy.{userID}": 1}})
                            await balance.user.change(userID, deposit)
                        return True
                return False
        
        async def editPrice(userID:int, ticker:str, price:int):
                db = await mongoCore.pullData()
                stock = await db.stockData.find_one(({"_id": ticker}))
                marketInfo = await db.market.find_one({"_id": "marketInfo"})
                if price == 0:
                    price = stock["stockPrice"] + marketInfo["incFactor"]
                if stock:
                    exists = await db.stockData.find_one({"$and": [{"_id":ticker}, {f"orders.buy.{userID}": {"$exists": True}}]})
                    if exists:
                        await orders.buy.addShares(userID, ticker, 0, price)
                        return True
                return False

class quick:
    
    class sell:
        async def quote(userID:int, ticker:str, shareCount:int):
                db = await mongoCore.pullData()
                stock = await db.stock.find_one(({"_id": ticker}))
                if stock:
                    buyOrders = stock["orders"]["buy"]
                    buyOrders = sorted(buyOrders.items(), key = lambda x: x[1]["price"], reverse=True)
                    stocksNeeded = shareCount
                    totalPrice = 0
                    for x in buyOrders:
                        if int(x[0]) != userID:
                            while stocksNeeded != 0 and x[1]["shareCount"] != 0:
                                (buyerID, orderData) = x
                                stocksNeeded -= 1
                                orderData["shareCount"] -= 1
                                totalPrice += orderData["price"]
                    if stocksNeeded == 0:
                        return totalPrice
                    else: return None
                else: return False
        
        async def confirm(userID:int, ticker:str, shareCount:int, quote:int):
                db = await mongoCore.pullData()
                marketInfo = await db.market.find_one({"_id": "marketInfo"})
                stock = await db.stock.find_one(({"_id": ticker}))
                if stock:
                    hasStock = stock["stockHolders"][f"{userID}"]
                    if hasStock >= shareCount:
                        buyOrders = stock["orders"]["buy"]
                        buyOrders = sorted(buyOrders.items(), key = lambda x: x[1]['price'], reverse=True)
                        sharesNeeded = shareCount
                        totalPrice = 0
                        buyerCache = {}
                        for x in buyOrders:
                            
                            buyerID = int(x[0])
                            if buyerID != userID:
                                if buyerID not in buyerCache:
                                    buyerCache[buyerID] = {}
                                    buyerCache[buyerID]["shareCount"] = 0
                                    buyerCache[buyerID]["userOwes"] = 0
                                
                                while sharesNeeded != 0 and stock["orders"]["buy"][str(buyerID)]["shareCount"] != 0:
                                    sharesNeeded -= 1
                                    stock["orders"]["buy"][str(buyerID)]["shareCount"] -= 1
                                    totalPrice += x[1]["price"]
                                
                                    buyerCache[buyerID]["shareCount"] += 1
                                    buyerCache[buyerID]["userOwes"] += x[1]["price"]  
                            
                        if sharesNeeded == 0 and totalPrice == quote:
                            taxFactor = float(str(marketInfo["marketCut"]))
                            for x in buyerCache:
                                if stock["orders"]["buy"][str(buyerID)]["shareCount"] != 0:
                                    await db.stockData.update_one(
                                    {"_id": ticker},
                                    {"$set":{f"orders.buy.{x}":{"shareCount": stock["orders"]["buy"][str(x)]["shareCount"], 
                                                                "price":stock["orders"]["buy"][str(x)]["price"], 
                                                                "deposit": stock["orders"]["buy"][str(x)]["deposit"] - buyerCache[x]['userOwes']}}})
                                else:
                                    await db.stockData.update_one(
                                    {"_id": ticker},
                                    {"$unset":{f"orders.buy.{x}":{"shareCount": 1}}})
                                if await db.stockData.find_one({"$and": [{"_id":ticker}, {f"stockHolders.{int(x)}": {"$exists": True}}]}):
                                    userStocks = stock["stockHolders"][str(x)]
                                else: userStocks = 0
                                userStocks += buyerCache[x]["shareCount"]
                                
                                await db.stock.update_one(
                                    {"_id": ticker}, 
                                    {"$set":{f"stockHolders.{int(x)}": userStocks}})
                                continue
                            await balance.user.change(userID, round(totalPrice*((1.0-taxFactor))))
                            await balance.company.change("Icenia National Bank", round(totalPrice*(taxFactor)))
                            
                            return(buyerCache)
                return False
    class buy:
                
                async def quote(userID:int, ticker:str, shareCount:int):
                    db = await mongoCore.pullData()
                    stock = await db.stock.find_one(({"_id": ticker}))
                    if stock:
                        sellOrders = stock["orders"]["sell"]
                        sellOrders = sorted(sellOrders.items(), key = lambda x: x[1]["price"], reverse=False)
                        stocksNeeded = shareCount
                        totalPrice = 0
                        for x in sellOrders:
                            if int(x[0]) != userID:
                                while stocksNeeded != 0 and x[1]["shareCount"] != 0:
                                    (sellerID, orderData) = x
                                    stocksNeeded -= 1
                                    orderData["shareCount"] -= 1
                                    totalPrice += orderData["price"]
                        if stocksNeeded == 0:
                            return totalPrice
                        else: return None
                    else: return False 

                
                async def confirm(userID, ticker:str, shareCount:int, quote:int):
                    db = await mongoCore.pullData()
                    marketInfo = await db.market.find_one({"_id": "marketInfo"})
                    stock = await db.stock.find_one(({"_id": ticker}))
                    if stock:

                        sellOrders = stock["orders"]["sell"]
                        sellOrders = sorted(sellOrders.items(), key = lambda x: x[1]["price"], reverse=False)
                        sharesNeeded = shareCount
                        totalPrice = 0
                        sellerCache = {}
                        for x in sellOrders:
                            sellerID = x[0]
                            if sellerID != userID:
                                if sellerID not in sellerCache:
                                    sellerCache[sellerID] = {}
                                    sellerCache[sellerID]["shareCount"] = 0
                                    sellerCache[sellerID]["userOwed"] = 0
                                
                                
                                while sharesNeeded != 0 and stock["orders"]["sell"][sellerID]["shareCount"] != 0:
                                    sharesNeeded -= 1
                                    stock["orders"]["sell"][str(sellerID)]["shareCount"] -= 1
                                    totalPrice += x[1]["price"]
                                
                                    sellerCache[sellerID]["shareCount"] += 1
                                    sellerCache[sellerID]["userOwed"] += x[1]["price"]
                        userBal = await balance.user.check(userID)
                        if sharesNeeded == 0 and totalPrice == quote and userBal >= totalPrice:
                            taxFactor = float(str(marketInfo["marketCut"]))
                            for x in sellerCache:
                                if stock["orders"]["sell"][str(sellerID)]["shareCount"] != 0:
                                    await db.stock.update_one(
                                    {"_id": ticker},
                                    {"$set":{f"orders.sell.{int(x)}":{"shareCount": stock["orders"]["sell"][str(x)]["shareCount"], 
                                                                "price":stock["orders"]["sell"][str(x)]["price"]}}})
                                else:
                                    await db.stock.update_one(
                                    {"_id": ticker},
                                    {"$unset":{f"orders.sell.{int(x)}":{"shareCount": 1}}})
                                await balance.user.change(int(x), round(sellerCache[x]["userOwed"]*(1-taxFactor)))
                                
                                continue
                            await balance.user.change(userID, -totalPrice)
                            if await db.stockData.find_one({"$and": [{"_id":ticker}, {f"stockHolders.{userID}": {"$exists": True}}]}):
                                    userStocks = stock["stockHolders"][str(userID)]
                            else: userStocks = 0
                            userStocks += shareCount
                                
                            await db.stock.update_one(
                                {"_id": ticker}, 
                                {"$set":{f"stockHolders.{int(x)}": userStocks}})
                            await balance.company.change("Icenia National Bank", round(totalPrice*(taxFactor)))
                                
                            return sellerCache
                    return False