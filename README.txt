RICH WATERS BOT — BASE BUILD

This is Phase 1:
- Preserves/renames the existing Rich Waters roles by ID
- Preserves/moves the existing Whitelisted Chat and Announcements channels
- Creates the approved categories, channels, voice channels, and forums
- Applies the Verified -> WL -> special role -> Staff visibility structure
- Adds /setup (Founder/Co Founder only)
- Adds /event for Events Team/Staff

IMPORTANT BEFORE RUNNING:
1. Create a brand-new Discord application/bot in the Discord Developer Portal.
2. Enable SERVER MEMBERS INTENT and MESSAGE CONTENT INTENT for the bot.
3. Invite the bot with bot + applications.commands scopes.
4. For initial setup, give the bot Administrator permission.
5. Put the bot role ABOVE the roles it needs to rename/manage.
6. In Railway Variables add:
   DISCORD_TOKEN = your bot token
   GUILD_ID = the Rich Waters server ID
7. Deploy.
8. When the bot is online, Founder or Co Founder runs /setup ONCE.

Existing IDs preserved:
Announcements channel: 1454759203070808224
Whitelisted chat: 1377119716434378792
Founder: 1482564578087796826
Co Founder: 1377119587878834196
Staff: 1377119611409006654
WL: 1377119583336530062
Verified: 1377119585953779722
Rich Baddies: 1377119576810328064
Key role: 1377119561979265084

NOTE:
This is intentionally the base build first. Ticket buttons, WL approval,
role requests, female verification automation, giveaways, moderation,
logging, and automatic anti-spam/security can be added after this base
is confirmed online and the server layout is correct.
