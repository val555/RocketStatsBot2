# bot.py
import asyncio
import discord
from discord.ext import commands
from config import DISCORD_TOKEN, DM_TIMEOUT, WEBHOOK_CHANNEL_ID
from db import init_db
from user_manager import get_user_by_discord_id, set_user_pseudo
from replay_manager import download_last_replays, process_new_replays
from report_manager import check_and_generate_report
from sqlalchemy import delete
from db import AsyncSessionLocal
from models import User, Replay
from user_manager import get_user_by_discord_id

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def prompt_pseudo(user: discord.User, text: str):
    dm = await user.create_dm()
    await dm.send(text)
    def ck(m): return m.author.id == user.id and isinstance(m.channel, discord.DMChannel)
    try:
        msg = await bot.wait_for("message", check=ck, timeout=DM_TIMEOUT)
        return msg.content.strip()
    except:
        return None

@bot.event
async def on_ready():
    await init_db()
    print(f"[BOT] {bot.user} prêt.")

@bot.command()
async def setup(ctx: commands.Context):
    discord_id = str(ctx.author.id)
    user = await get_user_by_discord_id(discord_id)
    if user:
        return await ctx.reply(f"Tu es déjà configuré : **{user.pseudo}**")
    await ctx.reply("Check tes DMs pour configurer ton pseudo RL.")
    pseudo = await prompt_pseudo(ctx.author, "Quel est ton pseudo Rocket League ?")
    if not pseudo:
        return await ctx.author.send("Timeout ou DM fermées.")
    await set_user_pseudo(discord_id, pseudo)
    await ctx.author.send(f"✅ Pseudo **{pseudo}** enregistré.")
    # téléchargement + parsing
    channel = bot.get_channel(WEBHOOK_CHANNEL_ID)
    files = await download_last_replays(channel, 50)
    await ctx.author.send(f"📥 {len(files)} replays téléchargés.")
    await ctx.author.send("🔄 Parsing en cours…")
    await process_new_replays(pseudo)
    await ctx.author.send("🎉 Parsing terminé. Stats à jour.")

@bot.command()
async def setpseudo(ctx: commands.Context, *, nouveau: str):
    discord_id = str(ctx.author.id)
    user = await get_user_by_discord_id(discord_id)
    if not user:
        return await ctx.reply("Pas encore configuré, lance `!setup` d'abord.")
    await set_user_pseudo(discord_id, nouveau)
    await ctx.reply(f"✅ Pseudo mis à jour : **{nouveau}**")

@bot.command()
async def report(ctx: commands.Context, count: int = 5):
    discord_id = str(ctx.author.id)
    user = await get_user_by_discord_id(discord_id)
    if not user:
        return await ctx.reply("Pas encore configuré, lance `!setup` d'abord.")
    from stats_manager import get_last_replays, aggregate_stats
    replays = await get_last_replays(user.pseudo, count)
    if not replays:
        return await ctx.reply("Aucune partie trouvée.")
    stats = await aggregate_stats(replays)
    total = stats["total"]
    wins = stats["wins"]
    losses = stats["losses"]
    mmr = stats["mmr_delta"]
    goals = stats["goals"]
    saves = stats["saves"]

    mmr_str = f"{'+' if mmr and mmr>=0 else ''}{mmr} 📈" if mmr is not None else "N/A"
    msg = (
    f"Sur tes {total} derniers matchs :\n"
    f"{wins} victoires 🏅\n"
    f"{losses} défaites ❌\n\n"
    f"MMR : {mmr_str}\n\n"
    f"Buts : {goals} ⚽\n"
    f"Saves : {saves} 🧤"
    )
    await ctx.reply(msg)

@bot.command(name="resetpseudo")
async def resetpseudo(ctx: commands.Context):
    """
    Supprime le pseudo de l'utilisateur et (optionnellement) tous ses replays.
    """
    discord_id = str(ctx.author.id)
    # Récupère l'utilisateur
    user = await get_user_by_discord_id(discord_id)
    if not user:
        return await ctx.reply("ℹ️ Tu n'es pas configuré·e. Lance `!setup` pour commencer.")

    # Confirmation : essaie de supprimer en base
    async with AsyncSessionLocal() as session:
        # Optionnel : supprimer aussi ses replays
        await session.execute(
            delete(Replay).where(Replay.user_pseudo == user.pseudo)
        )
        # Supprimer l'utilisateur
        await session.execute(
            delete(User).where(User.discord_id == discord_id)
        )
        await session.commit()

    await ctx.reply(
        "✅ Ton pseudo et ton historique de replays ont été supprimés.\n"
        "Tu peux relancer `!setup` pour recommencer."
    )

def run_bot():
    bot.run(DISCORD_TOKEN)

if __name__ == "__main__":
    run_bot()

    


