import discord
from discord.ext import commands
from discord.ui import Modal, InputText, View, Button
from discord.commands import Option
import asyncio
import datetime
import platform
import aiohttp
import sqlite3

class ReportButton(discord.ui.View):
    def __init__(self, client):
        super().__init__(timeout=None)
        
        self.client = client
    
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green, emoji="<:check_mark:946347634199765002>")
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Are you sure about that? [yes/no]")

        def check(m):
            return m.author.id == interaction.user.id #Check the message from the button clicker only
        
        try:
            msg = await self.client.wait_for('message', timeout=60, check=check) #Timeout is 60 seconds, and you have to type only yes or no.
            if msg.content == 'yes': #Check if they say yes (lowercase only)
                await msg.delete() #Delete the message
                await interaction.edit_original_message(view=None) #Remove the button to 
                await msg.send("Done.")
                await msg.user.send(f"{str(self.ctx.author)} has submitted your report.")
            
                async def WebhookSend(self, webhookURL, content):
                    async with aiohttp.ClientSession() as session:
                        webhook = discord.Webhook.from_url(webhookURL, session=session)
                        await webhook.send(content)
                
                e = await self.client.fetch_message(interaction.message.content)
                await WebhookSend('', e) #Get your own webhook
            
            elif msg.content == "no":
                await interaction.response.send_message("Look like we are not doing it today.")
                return
            else:
                return await interaction.response.send_message("What are you putting smh. Put only yes and no.")

        except asyncio.TimeoutError: #When user didn't respond in time.
            return await interaction.response.send_message("Don't want to confirm? Alright.")

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red, emoji="<:cross:946075938137968640>")
    async def deny(self, button: discord.ui.Button, interaction: discord.Interaction):
        
        def check(m):
            return m.author.id == interaction.user.id
        try:
            msg = await self.client.wait_for("message", timeout=60, check=check)
            await msg.delete()
            await interaction.response.send_message("Done.", ephemeral=True)
            await msg.user.send(f"{str(self.ctx.author)} has denied your report. Reason: {msg.content}")

        except asyncio.TimeoutError:
            return await interaction.response.send_message("You are taking too long to reply.")

class ReportModal(Modal):
    def __init__(self, client, *args, **kwargs) -> None:
        super().__init__("Network Bot report", *args, **kwargs)
        self.client = client

        self.conn = sqlite3.connect("report.db", isolation_level=None) #SQLite database using, and I set the variable for connect, not to confuse and mix things up.
        self.c = self.conn.cursor()
        self.c.execute('CREATE TABLE IF NOT EXISTS report_case (status TEXT, user_id INTEGER, reason TEXT, proof BLOB)')

        self.add_item(InputText(label="Report user(s)", value="", style=discord.InputTextStyle.short))
        self.add_item(InputText(label="Reason", value="", style=discord.InputTextStyle.long))
        self.add_item(InputText(label="Proof:", value="", style=discord.InputTextStyle.long))
    
    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="`✦ ˑ ִֶָ 𓂃⊹ New Report Case", color=0xe74c3c)
        embed.add_field(name="Report user(s):", value=self.children[0].value, inline=False)
        embed.add_field(name="Reason:", value=self.children[1].value, inline=False)
        embed.add_field(name="Proof:", value=self.children[2].value, inline=False)
        user = interaction.user.id
        embed.set_footer(text=f"Reported by {user}", icon_url=interaction.user.avatar)

        channel = await self.client.fetch_channel() #Fetch your own channel.
        self.c.execute('INSERT INTO report_case (status, user_id, reason, proof) VALUES (?, ?, ?, ?)', ("Pending", self.children[0].value, self.children[1].value, self.children[2].value)) #Insert a data to SQLite db.
        self.conn.commit() #Commit to db.
        view = ReportButton(client=self.client)
        await channel.send(embed=embed, view=view) #Send the report to specified channel.
        await interaction.response.send_message("Your report has been sent successfully!", ephemeral=True) #Interaction responded by telling the report has been sent and not to make modals showing something went wrong.

class Report(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.conn = sqlite3.connect('report.db', isolation_level=None)
        self.c = self.conn.cursor()
        self.c.execute('CREATE TABLE IF NOT EXISTS report_case (status TEXT, user_id INTEGER, reason TEXT, proof BLOB)')

    @discord.slash_command(name="report", description="Report a malicious user or view the report.", guild_ids=["770117321226059837"]) #Reminder: remove guild_ids to make it registers as a global slash.
    async def report(self, interaction: discord.Interaction, choices: Option(str, 'Choose the option.', choices=['send', 'cmdinfo', 'view'], required=False)):
        if choices == None: #Check if user didn't put the options.
            await interaction.response.send_message("This command is for report in <@!942739456983728169> only.")
        elif choices == 'send':
            modal = ReportModal(client=self.client)
            await interaction.response.send_modal(modal) #Send modal with interaction.

        elif choices == 'cmdinfo':
            view = View()
            button = Button(label="Bot invite link", emoji="<:Invite:946349370750693386>", url="https://discord.com/api/oauth2/authorize?client_id=946430680051634207&permissions=8&scope=bot%20applications.commands")
            button2 = Button(label="Support Link", url="https://discord.gg/BEmr9V2aRv", emoji="<:support:946433875704438785>")

            embed = discord.Embed(title="`✦ ˑ ִֶָ 𓂃⊹ Network report commands", description="Create by Mr.Nab#0730 to improve its security and prevents malicious users.\n Please do not use it as a guild report or use it for reporting someone for fun.", color=3553598, timestamp=datetime.datetime.now())
            embed.add_field(name="Versions", value=f"<:pycord:946384971654905936> [{discord.__version__}](https://github.com/Pycord-Development/pycord)\n <:Python:946377742075719700> [{platform.python_version()}](https://python.org/)")
            embed.add_field(name="Instance owned by:", value="Network Team", inline=False)
            embed.add_field(name="About:", value="Network Bot is made for talking with people in different servers.\n (c) Network Team 2022-present")
            
            view.add_item(button)
            view.add_item(button2)
            await interaction.response.send_message(embed=embed, view=view)

def setup(client):
    client.add_cog(Report(client))
