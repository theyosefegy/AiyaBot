import discord
from discord.ext import commands
import asyncio
from translate import Translator
import requests
from discord import app_commands


class Utility(commands.Cog):
    def __init__(self, bot) -> None:
        super().__init__()
        self.bot = bot
        self.user_dict = {}
        self.deleted_messages = []
        self.latest_emoji_url = ""
            
    # Reminder CMD
    @commands.command(aliases=["r"],help="Sets a reminder for a task within a designated time period.")
    async def reminder(self, ctx: commands.Context, time: str, *, task=None):
        
    
        if self.user_dict.get(ctx.author.id):
            await ctx.send("You currently have an active reminder. Please wait until it finishes.")
            return

        def convert(time: int):
            units = {
                "s": 1,
                "m": 60,
                "h": 3600,
                "d": 3600 * 60,
            }

            converted_time = int(time[:-1]) * units[time[-1]]
            return converted_time

        await ctx.reply(f"Reminder set! It will last for {time}.")
        self.user_dict[ctx.author.id] = 1

        await asyncio.sleep(convert(time))

        if task is None:
            await ctx.send(f"{ctx.author.mention}, your {time} reminder is up! 🕒")
        else:
            await ctx.send(f"{ctx.author.mention}, your reminder for '{task}' is up! 🕒")

        self.user_dict.pop(ctx.author.id)

    @reminder.error
    async def reminder_error(self, ctx, error):
        print(error)  # Print the error to the console for debugging
        
    # Define CMD    
    @commands.command(help="Fetches words' meanings and definitions w/examples.")
    async def define(self, ctx: commands.Context, word: str):
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list):
                # Extract relevant information from the API response
                word_data = data[0]

                # Word and phonetic pronunciation
                word_text = word_data.get("word", "")
                phonetic_text = word_data.get("phonetic", "")

                # Extract and format phonetics information
                phonetics_info = "\n".join(
                    f"{phonetic.get('text', '')} - [Audio]({phonetic.get('audio', '')})"
                    if "text" in phonetic else phonetic.get("text", "")
                    for phonetic in word_data.get("phonetics", [])
                )

                # Extract and format meanings information as a single string
                meanings_info = "\n".join(
                    f"**{meaning['partOfSpeech'].capitalize()}:**\n"
                    + "\n".join(
                        f"  - {definition['definition']}\n\nExample: {definition.get('example', '') }"
                        for definition in meaning['definitions']
                    )
                    for meaning in word_data.get("meanings", [])
                )
                
                meanings_info = meanings_info.replace('-', '--')

                # Construct an embed with the word information
                embed_data = {
                    "title": word_text.capitalize(),
                    "description": f"\n**Meanings:**\n{meanings_info}",
                    "color": int(ctx.author.top_role.color),  # Green color
                }

                embed = discord.Embed.from_dict(embed_data)
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"No definition found for {word}.")
        else:
            await ctx.send(f"Failed to fetch definition for {word}. Status code: {response.status_code}")

    # Translate CMD
    @commands.command(help="Translates text to another language.")
    async def translate(self, ctx: commands.Context, *, sentence: str, lang="arabic"):
        try:
            translator = Translator(to_lang=lang)
            translated_text = translator.translate(sentence)
            await ctx.send(f"Original: {sentence}\nTranslated ({lang}): {translated_text}")
        except Exception as e:
            print(f"An error occurred: {e}")
            await ctx.send("An error occurred during translation.")    

    # Snitch CMD
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author != self.bot.user:
            self.deleted_messages.append({
                "author": str(message.author),
                "content": message.content,
                "timestamp": message.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "channel": {
                    "id": str(message.channel.id),
                    "name": message.channel.name,
                },
                # Add other relevant information you want to store
            })

            # Limit the size of the list to keep a history
            self.deleted_messages = self.deleted_messages[-10:]

            # Schedule a task to clear the list after 10 seconds
            asyncio.create_task(self.clear_deleted_messages())

    async def clear_deleted_messages(self):
        await asyncio.sleep(10)
        self.deleted_messages.clear()

    @commands.command(help="Displays the latest deleted message")
    async def snitch(self, ctx: commands.Context):
        if self.deleted_messages:
            # Get the most recent deleted message
            most_recent_message = self.deleted_messages[-1]

            # Prepare an embedded message
            response = (
            "🕵️ **Deleted Message Report** 🕵️\n"
            "```python\n"
            f"{{\n"
            f"    'Author': '{most_recent_message['author']}',\n"
            f"    'Content': '{most_recent_message['content']}',\n"
            f"    'Channel': '#{most_recent_message['channel']['name']}',\n"
            f"    'Timestamp': '{most_recent_message['timestamp']}',\n"
            f"}}\n"
            "```"
            )

            # Send the message
            await ctx.send(response)
        else:
            # If no deleted messages
            await ctx.send("No deleted messages to report. The shadows remain silent.")
               
    # Emoji CMD                
    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        if message.content and len(message.content) == 1 and ord(message.content) > 127462:
            self.latest_emoji_url = str(message.content)
        else:
            for char in message.content:
                if ord(char) > 127462:
                    self.latest_emoji_url = str(char)
        
        
    @commands.command(help="Steals the latest emoji represented in chat.")
    async def steal(self, ctx: commands.Context):
        if self.latest_emoji_url:
            await ctx.send(f"👀 **Stolen Emoji:** {self.latest_emoji_url}")
        else:
            await ctx.send("😔 No emoji sent to steal. The shadows remain silent.")
        
async def setup(bot):
    await bot.add_cog(Utility(bot))
