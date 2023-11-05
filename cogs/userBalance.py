import discord
from discord.ext import commands
from discord import app_commands
import sys
import dataHandler


sys.dont_write_bytecode = True

class balance(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="balance", description="Check the balance of your personal account")
    async def balance(self, interaction:discord.Interaction):
        member=interaction.user
        memberBal = await dataHandler.balance.user.check(member.id)
        if memberBal:
            balanceEmbed = discord.Embed(title=f"{member.name}'s Balance", description=f"${memberBal}", color=discord.Color.brand_green())
            balanceEmbed.set_thumbnail(url=member.avatar.url)
            await interaction.response.send_message(embed=balanceEmbed, ephemeral= True)
        else: await interaction.response.send_message("error: your discord account is not tied to an INB account", ephemeral=True)

async def setup(client):
    await client.add_cog(balance(client))