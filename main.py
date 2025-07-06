import discord
import os
from discord.ext import commands
import random
import shlex
from dotenv import load_dotenv
import asyncio
from typing import List
import google.generativeai as genai
from gtts import gTTS
import io

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if TOKEN is None:
    print("Error: DISCORD_TOKEN environment variable not found.")
    exit()

if GEMINI_API_KEY is None:
    print("Error: GEMINI_API_KEY environment variable not found.")
    exit()

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def hello(ctx):
    await ctx.send(f'Hello {ctx.author.display_name}!')

@bot.command(name='teams', help='Randomizes players into two teams. Separate players with spaces. If a name contains spaces, use quotes (e.g., "John Doe").')
async def randomize_teams(ctx, *, players: str = None):
    if not players:
        await ctx.send("Please provide a list of players to randomize. Example: `!teams Player1 Player2 Player3 Player4`")
        return

    try:
        player_list = shlex.split(players)
    except ValueError:
        await ctx.send("Invalid input. Make sure the quotes are correct.")
        return
    if len(player_list) < 2:
        await ctx.send('Please provide at least two players.')
        return

    random.shuffle(player_list)
    
    team_a = player_list[:len(player_list)//2]
    team_b = player_list[len(player_list)//2:]

    team_a_str = ', '.join(team_a)
    team_b_str = ', '.join(team_b)

    response = f"**Team A:** {team_a_str}\n**Team B:** {team_b_str}"
    await ctx.send(response)

@bot.command(name='which', help='Chooses a game (or anything from given options).')
async def which_command(ctx, *, options: str = None):
    if not options:
        await ctx.send('Please provide a list of options. Example: `!which CS Valorant "League of Legends"`')
        return

    try:
        option_list = shlex.split(options)
    except ValueError:
        await ctx.send("Invalid input. Make sure the quotes are correct.")
        return
    if len(option_list) < 2:
        await ctx.send('Please provide at least two options.')
        return

    choice = random.choice(option_list)

    response = f"**I have chosen:** {choice}"
    await ctx.send(response)

@bot.command(name='ask', help='Asks mentioned users a question via DM and reports their answers. Usage: !ask @User1 @User2 Your question here')
async def ask_users(ctx, members: commands.Greedy[discord.Member], *, question: str):
    if not members:
        await ctx.send('**Usage:** `!ask @User1 @User2 Your question here`')
        return

    responses = {}
    member_names = ", ".join([member.display_name for member in members])
    
    await ctx.send(f"Sending the question \"{question}\" to {member_names}. They have 60 seconds to answer.")

    async def get_response(member):
        try:
            dm_channel = await member.create_dm()
            await dm_channel.send(f"You have a question from {ctx.author.display_name} in the server '{ctx.guild.name}':\n\n**{question}**\n\nPlease reply to this message with your answer. You have 60 seconds.")

            def check(message):
                return message.author == member and message.channel == dm_channel

            try:
                response_message = await bot.wait_for('message', timeout=60.0, check=check)
                responses[member.display_name] = response_message.content
            except asyncio.TimeoutError:
                responses[member.display_name] = "No answer (timed out)."

        except discord.Forbidden:
            responses[member.display_name] = "Could not send DM (user has DMs disabled)."
        except Exception as e:
            responses[member.display_name] = f"An error occurred: {e}"

    await asyncio.gather(*(get_response(member) for member in members))

    result_message = f"**Results for the question:** \"{question}\"\n\n"
    for name, answer in responses.items():
        result_message += f"**{name}:** {answer}\n"

    await ctx.send(result_message)

@bot.command(name='prompt', help='Creates content from user-provided input and a promt. Usage: !poem @User1 @User2 Your prompt here')
async def input_prompt(ctx, members: commands.Greedy[discord.Member], *, prompt: str):
    if not members:
        await ctx.send('**Usage:** `!poem @User1 @User2 Your prompt for the content`')
        return

    words = {}
    member_names = ", ".join([member.display_name for member in members])
    
    await ctx.send(f"Asking for input from {member_names} for the prompt: \"{prompt}\". They have 60 seconds to answer.")

    async def get_word(member):
        try:
            dm_channel = await member.create_dm()
            await dm_channel.send(f"You have a request from {ctx.author.display_name} for a prompt: \"{prompt}\".\n\nPlease reply with a short and simple answer. You have 60 seconds.")

            def check(message):
                return message.author == member and message.channel == dm_channel

            try:
                response_message = await bot.wait_for('message', timeout=60.0, check=check)
                words[member.display_name] = response_message.content
            except asyncio.TimeoutError:
                words[member.display_name] = None  # Mark as no response

        except discord.Forbidden:
            words[member.display_name] = None
        except Exception:
            words[member.display_name] = None

    await asyncio.gather(*(get_word(member) for member in members))

    responded = [name for name, word in words.items() if word is not None]
    not_responded = [name for name, word in words.items() if word is None]

    response_summary = ""
    if len(responded) == len(members):
        response_summary = "All users responded. "
    else:
        if responded:
            response_summary += f"Responded: {', '.join(responded)}. "
        if not_responded:
            response_summary += f"Did not respond: { ', '.join(not_responded)}. "

    await ctx.send(f"{response_summary}Generating content with Gemini...")

    provided_words = [word for word in words.values() if word is not None]

    if not provided_words:
        await ctx.send("No one provided any input, so I can't create anything.")
        return

    final_prompt = f"{prompt}. Use the following words provided by users: {', '.join(provided_words)}"

    try:
        response = model.generate_content(final_prompt)
        await ctx.send(f"**Here is the result based on your prompt and input:**\n\n{response.text}")
    except Exception as e:
        await ctx.send(f"An error occurred while generating content with Gemini: {e}")

@bot.command(name='prompt_audio', help='Creates content from user-provided input and a promt. Usage: !poem @User1 @User2 Your prompt here')
async def input_prompt_with_audio(ctx, members: commands.Greedy[discord.Member], *, prompt: str):
    if not members:
        await ctx.send('**Usage:** `!poem @User1 @User2 Your prompt for the content`')
        return

    words = {}
    member_names = ", ".join([member.display_name for member in members])
    
    await ctx.send(f"Asking for input from {member_names} for the prompt: \"{prompt}\". They have 60 seconds to answer.")

    async def get_word(member):
        try:
            dm_channel = await member.create_dm()
            await dm_channel.send(f"You have a request from {ctx.author.display_name} for a prompt: \"{prompt}\".\n\nPlease reply with a short and simple answer. You have 60 seconds.")

            def check(message):
                return message.author == member and message.channel == dm_channel

            try:
                response_message = await bot.wait_for('message', timeout=60.0, check=check)
                words[member.display_name] = response_message.content
            except asyncio.TimeoutError:
                words[member.display_name] = None  # Mark as no response

        except discord.Forbidden:
            words[member.display_name] = None
        except Exception:
            words[member.display_name] = None

    await asyncio.gather(*(get_word(member) for member in members))

    responded = [name for name, word in words.items() if word is not None]
    not_responded = [name for name, word in words.items() if word is None]

    response_summary = ""
    if len(responded) == len(members):
        response_summary = "All users responded. "
    else:
        if responded:
            response_summary += f"Responded: {', '.join(responded)}. "
        if not_responded:
            response_summary += f"Did not respond: { ', '.join(not_responded)}. "

    await ctx.send(f"{response_summary}Generating content with Gemini...")

    provided_words = [word for word in words.values() if word is not None]

    if not provided_words:
        await ctx.send("No one provided any input, so I can't create anything.")
        return

    final_prompt = f"{prompt}. Use the following words provided by users: {', '.join(provided_words)}"

    try:
        response = model.generate_content(final_prompt)
        gemini_text = response.text

        # Create TTS audio in memory
        tts = gTTS(text=gemini_text, lang='en')
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)

        # Send text and audio file
        await ctx.send(f"**Here is the result based on your prompt and input:**\n\n{gemini_text}", 
                     file=discord.File(fp=audio_fp, filename='generated_content.mp3'))

    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@bot.command(name='gemini', help='Ask Gemini anything. Usage: !gemini Your question here')
async def gemini_command(ctx, *, prompt: str = None):
    if not prompt:
        await ctx.send("Please provide a prompt for Gemini. Example: `!gemini What is the meaning of life?`")
        return

    try:
        await ctx.send(f"Asking Gemini: \"{prompt}\". Please wait...")
        response = model.generate_content(prompt)
        await ctx.send(response.text)
    except Exception as e:
        await ctx.send(f"An error occurred while communicating with Gemini: {e}")

bot.remove_command("help")
@bot.command(name='help', help='Displays a list of all available commands and their usage.')
async def help_command(ctx):    
    help_message = "```Available Commands:\n\n"    
    for command in bot.commands:        
        if command.help:            
            help_message += f"!{command.name}: {command.help}\n\n"        
        else:            
            help_message += f"!{command.name}: No description available.\n\n"
    help_message += "```" 
    await ctx.send(help_message)

bot.run(TOKEN)
