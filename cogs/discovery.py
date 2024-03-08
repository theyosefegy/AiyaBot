import discord
from discord.ext import commands
import requests
import datetime
import asyncio

class Discovery(commands.Cog):
    def __init__(self, bot) -> None:
        super().__init__()
        self.bot = bot
        self.deleted_messages = []

    @commands.command(aliases=["anime"],help="Explore anime details and stories")
    async def animelist(self, ctx: commands.Context, *, anime: str = None):
        if anime is None:
            await ctx.send("You forgot to tell me the name of the anime! 🤔")
            return

        url = f"https://kitsu.io/api/edge/anime?filter[text]={anime}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            if "data" in data and data["data"]:
                
                
                anime_data = data["data"][0]["attributes"]

                # Extract relevant information
                title = anime_data["titles"]["en"]
                synopsis = anime_data["synopsis"]
                average_rating = anime_data["averageRating"]
                created_At = anime_data.get("createdAt", "")  # Handle case where "createdAt" is not present
                favoritesCount = anime_data["favoritesCount"]
                thumbnail = anime_data["posterImage"]["original"]
                isnsfw = anime_data["nsfw"]
                youtubeVideoId = anime_data.get("youtubeVideoId", "")

                embed = {
                    "title": title,
                    "description": synopsis,
                    "url": f"https://www.youtube.com/watch?v={youtubeVideoId}",
                    "fields": [
                        {"name": "**Average Rating**:", "value": average_rating, "inline": True},
                        {"name": "**Created at**:", "value": datetime.datetime.strptime(created_At, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y/%m/%d"), "inline": True},
                        {"name": "**Favorites Count**:", "value": f"{favoritesCount} ❤", "inline": True},
                        {"name": "**NSFW**:🔞", "value": isnsfw, "inline": True},
                        {"name": "**Status**:", "value": anime_data["status"], "inline": True},
                        {"name": "**Anime 🆔:**", "value": data["data"][0]["id"], "inline": True},
                    ],
                    "thumbnail": {"url": thumbnail},
                    "footer": {"text": f"Requested by {ctx.author.name}", "icon_url": ctx.author.avatar.url},
                    "color": int(ctx.author.top_role.color)
                }

                # Display the information
                await ctx.send(embed=discord.Embed().from_dict(embed))

            else:
                await ctx.send(f"Sorry, couldn't find any info about `{anime}`. 😢")
        else:
            await ctx.send(f"Oops! Something went wrong while fetching anime data. Status code: {response.status_code}")

async def setup(bot):
    await bot.add_cog(Discovery(bot))

