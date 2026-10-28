import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", "0"))

# Existing Rich Waters IDs
ANNOUNCEMENTS_CHANNEL_ID = 1454759203070808224
WL_CHAT_CHANNEL_ID = 1377119716434378792

FOUNDER_ROLE_ID = 1482564578087796826
CO_FOUNDER_ROLE_ID = 1377119587878834196
STAFF_ROLE_ID = 1377119611409006654
WL_ROLE_ID = 1377119583336530062
VERIFIED_ROLE_ID = 1377119585953779722
RICH_BADDIES_ROLE_ID = 1377119576810328064
KEY_ROLE_ID = 1377119561979265084

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

class RichWatersBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        if GUILD_ID:
            guild = discord.Object(id=GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()

bot = RichWatersBot()

def has_any_role_id(member: discord.Member, *role_ids: int) -> bool:
    ids = {r.id for r in member.roles}
    return any(role_id in ids for role_id in role_ids)

def is_owner_level(member: discord.Member) -> bool:
    return has_any_role_id(member, FOUNDER_ROLE_ID, CO_FOUNDER_ROLE_ID)

async def get_or_create_role(guild, name, *, permissions=None, hoist=False):
    role = discord.utils.get(guild.roles, name=name)
    if role:
        return role
    return await guild.create_role(
        name=name,
        permissions=permissions or discord.Permissions.none(),
        hoist=hoist,
        reason="Rich Waters automated setup"
    )

async def get_or_create_category(guild, name, overwrites=None):
    category = discord.utils.get(guild.categories, name=name)
    if category:
        if overwrites is not None:
            await category.edit(overwrites=overwrites)
        return category
    return await guild.create_category(name, overwrites=overwrites, reason="Rich Waters automated setup")

async def get_or_create_text(category, name, overwrites=None):
    channel = discord.utils.get(category.text_channels, name=name)
    if channel:
        if overwrites is not None:
            await channel.edit(overwrites=overwrites)
        return channel
    return await category.create_text_channel(name, overwrites=overwrites)

async def get_or_create_voice(category, name, overwrites=None):
    channel = discord.utils.get(category.voice_channels, name=name)
    if channel:
        if overwrites is not None:
            await channel.edit(overwrites=overwrites)
        return channel
    return await category.create_voice_channel(name, overwrites=overwrites)

async def get_or_create_forum(category, name, overwrites=None):
    for ch in category.channels:
        if isinstance(ch, discord.ForumChannel) and ch.name == name:
            if overwrites is not None:
                await ch.edit(overwrites=overwrites)
            return ch
    return await category.create_forum(name, overwrites=overwrites)

@bot.event
async def on_ready():
    print(f"Rich Waters is online as {bot.user} ({bot.user.id})")

@bot.tree.command(name="setup", description="Build the Rich Waters server layout and permissions.")
@app_commands.guild_only()
async def setup(interaction: discord.Interaction):
    if not isinstance(interaction.user, discord.Member) or not is_owner_level(interaction.user):
        await interaction.response.send_message("Founder or Co Founder only.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True, thinking=True)
    guild = interaction.guild

    # Existing roles
    founder = guild.get_role(FOUNDER_ROLE_ID)
    co_founder = guild.get_role(CO_FOUNDER_ROLE_ID)
    staff_master = guild.get_role(STAFF_ROLE_ID)
    wl = guild.get_role(WL_ROLE_ID)
    verified = guild.get_role(VERIFIED_ROLE_ID)
    rich_baddies = guild.get_role(RICH_BADDIES_ROLE_ID)

    missing = [
        label for label, role in [
            ("Founder", founder), ("Co Founder", co_founder), ("Staff", staff_master),
            ("WL", wl), ("Verified", verified), ("Rich Baddies", rich_baddies)
        ] if role is None
    ]
    if missing:
        await interaction.followup.send(
            "Setup stopped. I couldn't find these existing roles: " + ", ".join(missing),
            ephemeral=True
        )
        return

    # Rename roles we are preserving.
    await founder.edit(name="👑・𝐅𝐎𝐔𝐍𝐃𝐄𝐑")
    await co_founder.edit(name="💎・𝐂𝐎 𝐅𝐎𝐔𝐍𝐃𝐄𝐑")
    await staff_master.edit(name="🛡️・𝐒𝐓𝐀𝐅𝐅")
    await wl.edit(name="🔑・𝐖𝐋")
    await verified.edit(name="✅・𝐕𝐄𝐑𝐈𝐅𝐈𝐄𝐃")
    await rich_baddies.edit(name="💋・𝐑𝐈𝐂𝐇 𝐁𝐀𝐃𝐃𝐈𝐄𝐒")

    # New functional/display roles.
    head_staff = await get_or_create_role(guild, "♛・𝐇𝐄𝐀𝐃 𝐎𝐅 𝐒𝐓𝐀𝐅𝐅", hoist=True)
    management = await get_or_create_role(guild, "💼・𝐌𝐀𝐍𝐀𝐆𝐄𝐌𝐄𝐍𝐓", hoist=True)
    administrator = await get_or_create_role(guild, "🛡️・𝐀𝐃𝐌𝐈𝐍𝐈𝐒𝐓𝐑𝐀𝐓𝐎𝐑", hoist=True)
    moderator = await get_or_create_role(guild, "⚖️・𝐌𝐎𝐃𝐄𝐑𝐀𝐓𝐎𝐑", hoist=True)
    trial_mod = await get_or_create_role(guild, "🔰・𝐓𝐑𝐈𝐀𝐋 𝐌𝐎𝐃", hoist=True)
    events_team = await get_or_create_role(guild, "🎟️・𝐄𝐕𝐄𝐍𝐓𝐒 𝐓𝐄𝐀𝐌", hoist=True)
    female_verifier = await get_or_create_role(guild, "💋・𝐅𝐄𝐌𝐀𝐋𝐄 𝐕𝐄𝐑𝐈𝐅𝐈𝐄𝐑", hoist=True)
    partner = await get_or_create_role(guild, "🤝・𝐏𝐀𝐑𝐓𝐍𝐄𝐑", hoist=True)
    await get_or_create_role(guild, "🎥・𝐂𝐎𝐍𝐓𝐄𝐍𝐓 𝐂𝐑𝐄𝐀𝐓𝐎𝐑", hoist=True)
    await get_or_create_role(guild, "🔴・𝐒𝐓𝐑𝐄𝐀𝐌𝐄𝐑", hoist=True)
    await get_or_create_role(guild, "🏳️‍🌈・𝐋𝐆𝐁𝐓𝐐", hoist=False)

    everyone = guild.default_role

    hidden = {everyone: discord.PermissionOverwrite(view_channel=False)}
    welcome_ow = {
        everyone: discord.PermissionOverwrite(view_channel=True, send_messages=False),
        verified: discord.PermissionOverwrite(view_channel=True),
        staff_master: discord.PermissionOverwrite(view_channel=True, send_messages=True),
    }
    verify_ow = {
        everyone: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        staff_master: discord.PermissionOverwrite(view_channel=True, send_messages=True),
    }
    verified_only = {
        everyone: discord.PermissionOverwrite(view_channel=False),
        verified: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        staff_master: discord.PermissionOverwrite(view_channel=True, send_messages=True),
    }
    wl_access = {
        everyone: discord.PermissionOverwrite(view_channel=False),
        wl: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        staff_master: discord.PermissionOverwrite(view_channel=True, send_messages=True),
    }
    read_only_wl = {
        everyone: discord.PermissionOverwrite(view_channel=False),
        wl: discord.PermissionOverwrite(view_channel=True, send_messages=False),
        staff_master: discord.PermissionOverwrite(view_channel=True, send_messages=True),
    }

    # Welcome
    welcome_cat = await get_or_create_category(guild, "🌴・𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝐑𝐈𝐂𝐇 𝐖𝐀𝐓𝐄𝐑𝐒")
    await get_or_create_text(welcome_cat, "👋・𝐖𝐄𝐋𝐂𝐎𝐌𝐄", welcome_ow)
    await get_or_create_text(welcome_cat, "📜・𝐑𝐔𝐋𝐄𝐒", welcome_ow)
    await get_or_create_text(welcome_cat, "🔐・𝐕𝐄𝐑𝐈𝐅𝐘", verify_ow)

    # Whitelist
    whitelist_cat = await get_or_create_category(guild, "🔑・𝐆𝐄𝐓 𝐖𝐇𝐈𝐓𝐄𝐋𝐈𝐒𝐓𝐄𝐃", hidden)
    await get_or_create_text(whitelist_cat, "🎟️・𝐑𝐄𝐐𝐔𝐄𝐒𝐓-𝐖𝐋", verified_only)

    # Community
    community = await get_or_create_category(guild, "💎・𝐑𝐈𝐂𝐇 𝐂𝐎𝐌𝐌𝐔𝐍𝐈𝐓𝐘", hidden)

    wl_chat = guild.get_channel(WL_CHAT_CHANNEL_ID)
    if wl_chat:
        await wl_chat.edit(name="💬・𝐖𝐇𝐈𝐓𝐄𝐋𝐈𝐒𝐓𝐄𝐃-𝐂𝐇𝐀𝐓", category=community, overwrites=wl_access)

    await get_or_create_text(community, "📸・𝐅𝐋𝐈𝐂𝐊𝐒", wl_access)
    await get_or_create_text(community, "🎬・𝐂𝐋𝐈𝐏𝐒", wl_access)
    await get_or_create_forum(community, "💡・𝐒𝐔𝐆𝐆𝐄𝐒𝐓𝐈𝐎𝐍𝐒", wl_access)
    await get_or_create_text(community, "🎭・𝐑𝐎𝐋𝐄-𝐑𝐄𝐐𝐔𝐄𝐒𝐓", wl_access)
    await get_or_create_forum(community, "♂️・𝐌𝐀𝐋𝐄-𝐖𝐋-𝐈𝐓𝐄𝐌𝐒", wl_access)
    await get_or_create_forum(community, "♀️・𝐅𝐄𝐌𝐀𝐋𝐄-𝐖𝐋-𝐈𝐓𝐄𝐌𝐒", wl_access)
    await get_or_create_voice(community, "🔊・𝐆𝐄𝐍𝐄𝐑𝐀𝐋-𝐕𝐂", wl_access)

    baddies_ow = {
        everyone: discord.PermissionOverwrite(view_channel=False),
        rich_baddies: discord.PermissionOverwrite(view_channel=True, send_messages=True, connect=True),
        staff_master: discord.PermissionOverwrite(view_channel=True, send_messages=True, connect=True),
    }
    await get_or_create_text(community, "💋・𝐑𝐈𝐂𝐇-𝐁𝐀𝐃𝐃𝐈𝐄𝐒", baddies_ow)
    await get_or_create_voice(community, "🥂・𝐁𝐀𝐃𝐃𝐈𝐄𝐒-𝐕𝐂", baddies_ow)

    # Word Around Town
    town = await get_or_create_category(guild, "🌃・𝐖𝐎𝐑𝐃 𝐀𝐑𝐎𝐔𝐍𝐃 𝐓𝐎𝐖𝐍", hidden)

    announcements = guild.get_channel(ANNOUNCEMENTS_CHANNEL_ID)
    if announcements:
        await announcements.edit(name="📢・𝐀𝐍𝐍𝐎𝐔𝐍𝐂𝐄𝐌𝐄𝐍𝐓𝐒", category=town, overwrites=read_only_wl)

    await get_or_create_text(town, "🌆・𝐂𝐈𝐓𝐘-𝐔𝐏𝐃𝐀𝐓𝐄𝐒", read_only_wl)
    await get_or_create_text(town, "🎥・𝐒𝐍𝐄𝐀𝐊-𝐏𝐄𝐄𝐊𝐒", read_only_wl)

    event_ow = {
        everyone: discord.PermissionOverwrite(view_channel=False),
        wl: discord.PermissionOverwrite(view_channel=True, send_messages=False),
        events_team: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        staff_master: discord.PermissionOverwrite(view_channel=True, send_messages=True),
    }
    await get_or_create_text(town, "🎉・𝐄𝐕𝐄𝐍𝐓-𝐀𝐍𝐍𝐎𝐔𝐍𝐂𝐄𝐌𝐄𝐍𝐓𝐒", event_ow)
    await get_or_create_text(town, "🎁・𝐆𝐈𝐕𝐄𝐀𝐖𝐀𝐘𝐒", read_only_wl)
    await get_or_create_text(town, "🌐・𝐑𝐄𝐋𝐀𝐓𝐄𝐃-𝐒𝐄𝐑𝐕𝐄𝐑𝐒", read_only_wl)

    partner_ow = {
        everyone: discord.PermissionOverwrite(view_channel=False),
        wl: discord.PermissionOverwrite(view_channel=True, send_messages=False),
        partner: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        staff_master: discord.PermissionOverwrite(view_channel=True, send_messages=True),
    }
    await get_or_create_text(town, "🤝・𝐏𝐀𝐑𝐓𝐍𝐄𝐑𝐒", partner_ow)

    events_private = {
        everyone: discord.PermissionOverwrite(view_channel=False),
        events_team: discord.PermissionOverwrite(view_channel=True, send_messages=True, connect=True),
        staff_master: discord.PermissionOverwrite(view_channel=True, send_messages=True, connect=True),
    }
    await get_or_create_text(town, "🎬・𝐄𝐕𝐄𝐍𝐓𝐒-𝐓𝐄𝐀𝐌-𝐂𝐇𝐀𝐓", events_private)
    await get_or_create_voice(town, "🎙️・𝐄𝐕𝐄𝐍𝐓𝐒-𝐓𝐄𝐀𝐌-𝐕𝐂", events_private)

    # Marketplace
    market = await get_or_create_category(guild, "💰・𝐓𝐇𝐄 𝐌𝐀𝐑𝐊𝐄𝐓𝐏𝐋𝐀𝐂𝐄", hidden)
    await get_or_create_text(market, "💳・𝐃𝐎𝐍𝐀𝐓𝐈𝐎𝐍-𝐈𝐍𝐅𝐎", read_only_wl)
    market_forum = await get_or_create_forum(market, "💎・𝐑𝐈𝐂𝐇-𝐌𝐀𝐑𝐊𝐄𝐓", wl_access)
    desired_tags = ["🏢 BUSINESS", "🏙️ MLO", "🏎️ CARS", "🔫 WEAPONS", "🟢 AVAILABLE", "🔴 SOLD"]
    if not market_forum.available_tags:
        await market_forum.edit(available_tags=[discord.ForumTag(name=x) for x in desired_tags])

    # Support
    support = await get_or_create_category(guild, "🎫・𝐂𝐈𝐓𝐘 𝐒𝐔𝐏𝐏𝐎𝐑𝐓", hidden)
    await get_or_create_text(support, "🎫・𝐎𝐏𝐄𝐍-𝐀-𝐓𝐈𝐂𝐊𝐄𝐓", wl_access)
    await get_or_create_text(support, "🐛・𝐁𝐔𝐆-𝐑𝐄𝐏𝐎𝐑𝐓𝐒", wl_access)
    await get_or_create_text(support, "💥・𝐂𝐑𝐀𝐒𝐇-𝐑𝐄𝐏𝐎𝐑𝐓𝐒", wl_access)
    await get_or_create_voice(support, "🔊・𝐖𝐀𝐈𝐓𝐈𝐍𝐆-𝐅𝐎𝐑-𝐒𝐔𝐏𝐏𝐎𝐑𝐓-𝟏", wl_access)
    await get_or_create_voice(support, "🔊・𝐖𝐀𝐈𝐓𝐈𝐍𝐆-𝐅𝐎𝐑-𝐒𝐔𝐏𝐏𝐎𝐑𝐓-𝟐", wl_access)
    await get_or_create_voice(support, "🔊・𝐖𝐀𝐈𝐓𝐈𝐍𝐆-𝐅𝐎𝐑-𝐒𝐔𝐏𝐏𝐎𝐑𝐓-𝟑", wl_access)

    female_verify_ow = {
        everyone: discord.PermissionOverwrite(view_channel=False),
        wl: discord.PermissionOverwrite(view_channel=True, connect=True),
        female_verifier: discord.PermissionOverwrite(view_channel=True, connect=True, move_members=True),
        staff_master: discord.PermissionOverwrite(view_channel=True, connect=True, move_members=True),
    }
    await get_or_create_voice(support, "💋・𝐅𝐄𝐌𝐀𝐋𝐄-𝐕𝐄𝐑𝐈𝐅𝐈𝐂𝐀𝐓𝐈𝐎𝐍", female_verify_ow)

    # Staff HQ
    staff_ow = {
        everyone: discord.PermissionOverwrite(view_channel=False),
        staff_master: discord.PermissionOverwrite(view_channel=True, send_messages=True, connect=True),
    }
    staff_cat = await get_or_create_category(guild, "🛡️・𝐒𝐓𝐀𝐅𝐅 𝐇𝐐", staff_ow)
    for name in [
        "📢・𝐒𝐓𝐀𝐅𝐅-𝐀𝐍𝐍𝐎𝐔𝐍𝐂𝐄𝐌𝐄𝐍𝐓𝐒",
        "💬・𝐒𝐓𝐀𝐅𝐅-𝐂𝐇𝐀𝐓",
        "📋・𝐒𝐓𝐀𝐅𝐅-𝐍𝐎𝐓𝐄𝐒",
        "📥・𝐖𝐋-𝐑𝐄𝐐𝐔𝐄𝐒𝐓𝐒",
        "🎫・𝐓𝐈𝐂𝐊𝐄𝐓-𝐋𝐎𝐆𝐒",
        "💰・𝐃𝐎𝐍𝐀𝐓𝐈𝐎𝐍-𝐋𝐎𝐆𝐒",
        "💋・𝐅𝐄𝐌𝐀𝐋𝐄-𝐕𝐄𝐑𝐈𝐅𝐈𝐂𝐀𝐓𝐈𝐎𝐍-𝐋𝐎𝐆𝐒",
    ]:
        await get_or_create_text(staff_cat, name, staff_ow)
    await get_or_create_voice(staff_cat, "🔊・𝐒𝐓𝐀𝐅𝐅-𝐕𝐂", staff_ow)

    await interaction.followup.send(
        "✅ Rich Waters base layout is built. Existing WL chat, announcements, and preserved roles were reused.",
        ephemeral=True
    )

@bot.tree.command(name="event", description="Post a Rich Waters event announcement.")
@app_commands.describe(
    name="Event name",
    date_time="Date/time, e.g. Tonight at 9 PM EST",
    location="In-city location",
    description="What is happening?",
    host="Event host",
    image_url="Optional image URL"
)
@app_commands.guild_only()
async def event(
    interaction: discord.Interaction,
    name: str,
    date_time: str,
    location: str,
    description: str,
    host: str,
    image_url: str | None = None
):
    guild = interaction.guild
    member = interaction.user
    events_role = discord.utils.get(guild.roles, name="🎟️・𝐄𝐕𝐄𝐍𝐓𝐒 𝐓𝐄𝐀𝐌")
    allowed = isinstance(member, discord.Member) and (
        has_any_role_id(member, STAFF_ROLE_ID, FOUNDER_ROLE_ID, CO_FOUNDER_ROLE_ID)
        or (events_role and events_role in member.roles)
    )
    if not allowed:
        await interaction.response.send_message("Events Team or Staff only.", ephemeral=True)
        return

    channel = discord.utils.get(guild.text_channels, name="🎉・𝐄𝐕𝐄𝐍𝐓-𝐀𝐍𝐍𝐎𝐔𝐍𝐂𝐄𝐌𝐄𝐍𝐓𝐒")
    if not channel:
        await interaction.response.send_message("Event announcement channel not found. Run /setup first.", ephemeral=True)
        return

    embed = discord.Embed(
        title=f"🌃 {name.upper()}",
        description=description
    )
    embed.add_field(name="🗓️ DATE / TIME", value=date_time, inline=True)
    embed.add_field(name="📍 LOCATION", value=location, inline=True)
    embed.add_field(name="🥂 HOST", value=host, inline=False)
    embed.set_footer(text="RICH WATERS • WORD AROUND TOWN")
    if image_url:
        embed.set_image(url=image_url)

    await channel.send(embed=embed)
    await interaction.response.send_message("✅ Event posted.", ephemeral=True)

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing. Add it to your environment variables.")

bot.run(TOKEN)
