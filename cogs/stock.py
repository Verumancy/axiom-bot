import discord
from discord.ext import commands
from discord import app_commands
import sys
import dataHandler


sys.dont_write_bytecode = True

class stock(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="stock", description="Check the details of a stock on the market")
    @app_commands.describe(ticker="A valid stock ticker")
    async def stock(self, interaction:discord.Interaction, ticker:str):
        db = await dataHandler.mongoCore.pullData()
        stock = await db.stock.find_one({"_id": ticker})
        if stock:
            shareCount = stock["shareCount"]
            prevValues = stock["prevPrices"]
            currentPrice = stock["stockPrice"]
            prev1 = prevValues[-1]
            if len(prevValues) >= 7:
                prev7 = prevValues[len(prevValues)]
            else: prev7 = prevValues[0]
            prevAll = prevValues[0]
            prev1 = round(((currentPrice-prev1)/prev1)*100, 2)
            prev7 = round(((currentPrice-prev7)/prev7)*100, 2)
            prevAll = round(((currentPrice-prevAll)/prevAll)*100, 2)
            
            sellVolume = 0
            sellOrders = stock["orders"]["sell"]
            for x in sellOrders:
                sellVolume += sellOrders[str(x)]["shareCount"]
                
            lowestSellPrice = None
            if sellVolume > 0:
                lowestSellPrice = await dataHandler.stocks.quick.buy.quote(1, ticker, 1)
            
            buyVolume = 0
            buyOrders = stock["orders"]["buy"]
            for x in buyOrders:
                buyVolume += buyOrders[str(x)]["shareCount"]
                
            lowestBuyPrice = None
            if sellVolume > 0:
                lowestBuyPrice = await dataHandler.stocks.quick.sell.quote(1, ticker, 1)

            embed = discord.Embed(title= f"${ticker}", color=discord.Color.dark_gold())
            embed.add_field(name="Price", value=f"${currentPrice}", inline=False)
            if prev1>0:
                embed.add_field(name="Fluctuation (1 Day)", value=f"🟩 +{abs(prev1)}%")
            else: 
                if prev1 == 0:
                    embed.add_field(name="Fluctuation (1 Day)", value=f"🟨 +{abs(prev1)}%")
                else:
                    if prev1<0:
                        embed.add_field(name="Fluctuation (1 Day)", value=f"🟥 -{abs(prev1)}%")
            if prev7>0:
                embed.add_field(name="Fluctuation (7 Days)", value=f"🟩 +{abs(prev7)}%")
            else: 
                if prev7 == 0:
                    embed.add_field(name="Fluctuation (7 Days)", value=f"🟨 +{abs(prev7)}%")
                else:
                    if prev7<0:
                        embed.add_field(name="Fluctuation (7 Days)", value=f"🟥 -{abs(prev7)}%")
            
            if prevAll>0:
                embed.add_field(name="Fluctuation (All Time)", value=f"🟩 +{abs(prevAll)}%")
            else: 
                if prevAll == 0:
                    embed.add_field(name="Fluctuation (All Time)", value=f"🟨 +{abs(prevAll)}%")
                else:
                    if prevAll<0:
                        embed.add_field(name="Fluctuation (All Time)", value=f"🟥 -{abs(prevAll)}%")

            embed.add_field(name="Share Count", value=shareCount, inline=False)
            embed.add_field(name="**__Statistics__**\nSell", value=f"Price: {lowestSellPrice}\nVolume: {sellVolume}", inline=False)
            embed.add_field(name="Buy", value=f"Price: {lowestBuyPrice}\nVolume: {buyVolume}", inline=False)
            await interaction.response.send_message(embed=embed)
        else: 
            await interaction.response.send_message("error: stock does not exist, maybe you made a typo?", ephemeral=True)
            
        

async def setup(client):
    await client.add_cog(stock(client))