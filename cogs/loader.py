import discord
from discord.ext import commands

class Loader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.is_owner()
    @commands.command()
    async def load(self,ctx, extension):
            await commands.load_extension(f"cogs.{extension}")
            await ctx.send(f"{extension} extension succefly loaded!")
            
    @commands.is_owner()
    @commands.command()
    async def unload(self,ctx, extension):
            await commands.unload_extension(f"cogs.{extension}")
            await ctx.send(f"{extension} extension succefly unloaded!")
        
async def setup(bot):
    await bot.add_cog(Loader(bot))
