import discord
from discord.ext import commands
import asyncio
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv('TOKEN')
PE_URL = 'https://concursosnobrasil.com/concursos/pe/'
TO_URL = 'https://concursosnobrasil.com/concursos/to/'
PB_URL = 'https://concursosnobrasil.com/concursos/pb/'
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix=None, intents=intents)

async def send_table(url, channel, state):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table')
    data = [
        {
            'Órgão': cells[0].text.strip(),
            'Vagas': cells[1].text.strip()
        }
        for row in table.find_all('tr')[1:]
        for cells in [row.find_all('td')]
    ]
    unique_data = {item['Órgão']: item['Vagas'] for item in data}
    table_message = f'📋 **Tabela de concursos abertos ({state}):**\n\n'
    table_message += '\n'.join([f"• **{orgao}**: {vagas}" for orgao, vagas in unique_data.items()])
    await channel.send(table_message)

async def update_tables():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    await send_table(PE_URL, channel, 'Pernambuco')
    await send_table(TO_URL, channel, 'Tocantins')
    await send_table(PB_URL, channel, 'Paraíba')

@client.event
async def on_ready():
    print(f'🤖 Bot conectado como {client.user}!')
    await update_tables()
    while True:
        await asyncio.sleep(12 * 60 * 60)  # Espera 12 horas (em segundos) antes de atualizar as tabelas
        await update_tables()

client.run(TOKEN)
