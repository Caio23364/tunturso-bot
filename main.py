import discord
from discord.ext import commands

import asyncio
import requests
from bs4 import BeautifulSoup


# Define o token de autenticação do bot
TOKEN = 'SEU_TOKEN_AQUI'

# Define as URLs dos sites de concursos
PE_URL = 'https://concursosnobrasil.com/concursos/pe/'
TO_URL = 'https://concursosnobrasil.com/concursos/to/'

# ID do canal a ser enviado as mensagens
ID_CANAL = 'ID_DO_CANAL'

# Define as intents que o bot usará
intents = discord.Intents.default()
intents.members = True

# Cria uma instância do bot
client = commands.Bot(command_prefix='/', intents=intents)


async def send_table(url, headers, channel):
    """Faz uma requisição HTTP para a URL passada e envia uma tabela com informações dos concursos para o canal especificado"""

    # Faz a requisição HTTP para a URL
    response = requests.get(url)

    # Cria um objeto BeautifulSoup a partir do HTML retornado pela requisição
    soup = BeautifulSoup(response.content, 'html.parser')

    # Encontra a tabela com as informações dos concursos
    table = soup.find('table')

    # Cria uma lista vazia para armazenar as informações dos concursos
    data = []

    # Itera pelas linhas da tabela e armazena as informações em um dicionário
    for row in table.find_all('tr')[1:]:
        cells = row.find_all('td')
        item = {}
        for i in range(len(headers)):
            item[headers[i]] = cells[i].text.strip()
        data.append(item)

    # Cria uma mensagem com a tabela de concursos e envia para o canal especificado
    table_message = '**Tabela de concursos abertos:**\n'
    for row in data:
        table_message += f"- **{row['Órgão']}**: {row['Vagas']}\n"

    await channel.send(table_message)


async def update_tables():
    """Atualiza a tabela de concursos para os canais especificados"""

    # Espera até que o bot esteja pronto
    await client.wait_until_ready()

    # Obtém o canal onde a tabela de concursos será enviada
    channel = client.get_channel(ID_CANAL)

    # Define os cabeçalhos da tabela
    headers = ['Órgão', 'Vagas']

    # Envia a tabela de concursos para as URLs especificadas
    await send_table(PE_URL, headers, channel)
    await send_table(TO_URL, headers, channel)


@client.event
async def on_ready():
    """Executado quando o bot estiver pronto"""

    # Imprime uma mensagem no console indicando que o bot está conectado
    print(f'Bot conectado como {client.user}!')

    # Atualiza a tabela de concursos
    await update_tables()

    # Aguarda 12 horas e atualiza a tabela novamente
    while True:
        await asyncio.sleep(21600)
        await update_tables()


@client.command()
async def atualizar(ctx):
    """Comando para atualizar manualmente a tabela de concursos"""

    await update_tables()


# Inicia o bot
client.run(TOKEN)
