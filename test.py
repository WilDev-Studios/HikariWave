from __future__ import annotations

from dotenv import load_dotenv

import hikari
import hikariwave
import os

load_dotenv()


bot: hikari.GatewayBot = hikari.GatewayBot(os.environ["TOKEN"], logs="DEBUG")
voice: hikariwave.VoiceClient = hikariwave.VoiceClient(bot)

@bot.listen(hikari.VoiceStateUpdateEvent)
async def voice_state_update(event: hikari.VoiceStateUpdateEvent) -> None:
    if (event.state.user_id == bot.get_me().id): # type: ignore
        return

    if event.state.channel_id:
        await voice.connect(event.guild_id, event.state.channel_id, deaf=False)
        await voice.play_file(event.guild_id, "test.mp3")
    else:
        await voice.disconnect(event.guild_id)

bot.run()
