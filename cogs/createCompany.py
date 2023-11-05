import discord
from discord.ext import commands
from discord import app_commands
import sys
import dataHandler
import configs

sys.dont_write_bytecode = True

class createCompany(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="create-company", description="Chreate a new company account (Bank Managers)")
    @app_commands.checks.has_role(configs.bankAdminID)
    async def createCompany(self, interaction:discord.Interaction, companyname:str, initialowner:discord.Member, ):
        if await dataHandler.registration.company(companyname, initialowner) == True:
            await interaction.response.send_message(f"Successfully created company '{companyname}', with primary owner {initialowner.mention}", ephemeral=True)
            await initialowner.send(f"You have been registered as the head of the company '{companyname}.'")
            print(1)
            loggingChannel = await interaction.guild.get_channel_or_thread(configs.loggingChannelID)
            print(2)
            loggingEmbed = discord.Embed(title="Registered New Company", description=f"Branch manager {interaction.user.name}({interaction.user.id}) created a new company '{companyname}' with the primary owner being {initialowner.name}({initialowner.id})")
            print(3)
            await loggingChannel.send(loggingEmbed)
        else: 
            await interaction.response.send_message("Failed to create company, does it already exist?", ephemeral=True)

async def setup(client):
    await client.add_cog(createCompany(client))