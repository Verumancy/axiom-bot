import discord
from discord.ext import commands
from discord import app_commands
import sys
import dataHandler
import configs

loggingID = configs.loggingChannelID

sys.dont_write_bytecode = True

class createCompany(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="manager-create-company", description="Chreate a new company account (Bank Managers)")
    @app_commands.checks.has_role(configs.bankAdminID)
    async def createCompany(self, interaction:discord.Interaction, companyname:str, initialowner:discord.Member, ):
        if await dataHandler.registration.company(companyname, initialowner) == True:
            await interaction.response.send_message(f"Successfully created company '{companyname}', with primary owner {initialowner.mention}", ephemeral=True)
            await initialowner.send(f"You have been registered as the head of the company '{companyname}.'")
            loggingChannel = self.client.get_channel(loggingID)
            loggingEmbed = discord.Embed(title="Registered New Company", description=f"Branch manager {interaction.user.name}({interaction.user.id}) created a new company '{companyname}' with the primary owner being {initialowner.name}({initialowner.id})")
            await loggingChannel.send(embed = loggingEmbed)
        else: 
            await interaction.response.send_message("Failed to create company, does it already exist?", ephemeral=True)

async def setup(client):
    await client.add_cog(createCompany(client))