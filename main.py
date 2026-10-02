import os
import asyncio
import random
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from openai import OpenAI

# Puxa as configurações seguras do Render
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
SESSION_STRING = os.getenv('SESSION_STRING')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Inicia as conexões
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Personalidade da Valeria
PROMPT_SISTEMA = """
Você é a Valeria, uma atendente virtual muito educada, simpática e prestativa.
Você trabalha para [NOME DA SUA EMPRESA].
Seus clientes estão conversando com você pelo Telegram.
Responda de forma natural, humana e concisa. Não use markdown (negrito, itálico) para parecer mais humano.
Se não souber a resposta, diga que vai verificar com a equipe e que responderá em breve.
Nunca diga que é uma IA ou um robô. Aja como uma pessoa real.
"""

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    if event.out:
        return
    sender = await event.get_sender()
    if getattr(sender, 'bot', False):
        return

    user_message = event.message.message
    if not user_message:
        return

    try:
        async with client.action(event.chat_id, 'typing'):
            delay = min(len(user_message) * 0.05, 4.0) + random.uniform(1.0, 2.5)
            await asyncio.sleep(delay)

            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": PROMPT_SISTEMA},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=300
            )

            reply_text = response.choices[0].message.content
            await event.reply(reply_text)

    except Exception as e:
        print(f"Erro ao responder: {e}")

async def main():
    await client.start()
    print("Atendente Valeria online!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
