######## Todos Direitos Reservados ########
############### Mitsuya-Dev ###############

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import cloudscraper
import csv
import time

MOEDAS = ['USD', 'EUR', 'JPY', 'GBP', 'CAD', 'AUD', 'CHF', 'NZD']

def get_news():
    noticias_dict = {}

    # INICIALIZA SESSÃO COM SERVIDOR DE NOTÍCIAS
    headers = requests.utils.default_headers()
    headers.update(
        {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0'})

    scraper = cloudscraper.create_scraper()

    response = scraper.get(
        'http://br.investing.com/economic-calendar/', headers=headers)

    data_hoje = datetime.now().strftime('%Y/%m/%d')  # data do dia atual

    if response.status_code == requests.codes.ok:
        data = BeautifulSoup(response.text, 'html.parser')

        noticias = ((data.find('table', {'id': 'economicCalendarData'})).find(
            'tbody')).findAll('tr', {'class': 'js-event-item'})

        for noticia in noticias:

            impacto = int(str((noticia.find('td', {'class': 'sentiment'})).get(
                'data-img_key')).replace('bull', ''))

            data_hora = str(noticia.get('data-event-datetime'))
            hora = data_hora.split()[1][:5]

            data = data_hora.split()[0]

            moeda = (noticia.find(
                'td', {'class': 'left flagCur noWrap'})).text.strip()

            if data_hoje != data or moeda not in MOEDAS:
                continue

            if moeda not in noticias_dict.keys():
                noticias_dict[moeda] = {}

            if hora in noticias_dict[moeda].keys() and noticias_dict[moeda][hora] < impacto:
                noticias_dict[moeda][hora] = impacto
            elif hora not in noticias_dict[moeda].keys():
                noticias_dict[moeda][hora] = impacto

        with open('noticias.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)

            for key in noticias_dict.keys():
                row = [datetime.now().strftime('%Y-%m-%d'), key]
                for value in noticias_dict[key].keys():
                    row.append(f"{value} {noticias_dict[key][value]*'+'}")
                writer.writerow(row)

    else:
        pass

# Verifica se o dia mudou e chama a função get_news() para atualizar o arquivo
ultima_data = ""
while True:
    data_hoje = datetime.now().strftime('%Y-%m-%d')
    if data_hoje != ultima_data:
        ultima_data = data_hoje
        get_news()
    time.sleep(60)  # espera 60 segundos antes de verificar novamente
