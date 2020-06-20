#!/usr/bin/env python
# coding: utf-8

# # Extraccion de informacion
# 
# Script para extraer información desde Metacritic por medio de tecnicas de web scraping. Deja como salida un archivo csv con la información de las reviews

import requests
from bs4 import BeautifulSoup
import time
import random as rand 
import pandas as pd
from langdetect import detect
import multiprocessing as mp
import numpy as np
import os.path
from os import path

# Funcion que detecta el lenguaje de una review en un dataframe
def add_language(df):
    df['langreview'] = df['review'].apply(detect)
    return df

# Main
if __name__ == '__main__':

    if(path.exists('./trainingSet.csv')):
        review_dict = pd.read_csv('./trainingSet.csv')
    else:
        review_dict = pd.DataFrame(columns=['name','product','platform','date','rating','upVotes','totVotes','review','langreview'])

    # Lectura del archivo de urls
    if(path.exists('./urls.csv')):
        resources = pd.read_csv('./urls.csv')
    else:
        print('No hay archivo de urls. Cree el archivo urls.csv con las siguientes columnas:')
        print('     url,status,paginasProcesadas,paginasTotales')
        exit(1)
    
    urls = resources.loc[resources['status'] != 'S']

    # Lectura del archivo de control
    if(path.exists('./control.csv')):
        control = pd.read_csv('./control.csv')
    else:
        control = pd.DataFrame(columns=['url','page','status'])

    # Configuracion de request
    headers = {'User-agent': 'Mozilla/5.0'}

    i = 1
    print('Descargando Reviews')
    for url in urls.url:
        # Se toma el numero de paginas de reviews
        response = requests.get(url, headers=headers)
        if(response.status_code != 200):
            resources.loc[resources.url == url, 'status'] = 'F'
            continue
        resources.loc[resources.url == url, 'status'] = 'W'
        soup = BeautifulSoup(response.text, 'html.parser')
        lastPageList = soup.find('li', class_='last_page')
        numPages = 10
        if(lastPageList):
            pageRef = lastPageList.find('a', class_='page_num')
            if(pageRef):
                numPages = int(pageRef.text)
        resources.loc[resources.url == url, 'paginasProcesadas'] = 0
        procesadas = 0
        resources.loc[resources.url == url, 'paginasTotales'] = numPages
        for page in range(0,numPages):
            print('Procesando url {} de {}  {:.1%}\r'.format(i,len(urls),(page+1)/numPages),end='')
            filter1 = control['url'] == url
            filter2 = control['page'] == page
            filter3 = control['status'] == 'S'
            register = control.query('url == "'+url+'" and page == '+str(page)+' and status == "S"')
            if(len(register) > 0):
                procesadas += 1
                resources.loc[resources.url == url, 'paginasProcesadas'] += 1
                continue
            headers = {'User-agent': 'Mozilla/5.0'}
            reviewUrl = url + '?page=' + str(numPages)
            response  = requests.get(url, headers = headers)
            if(response.status_code != 200):
                if(len(control.loc[filter1 & filter2]) > 0):
                    control.loc[filter1 & filter2,'status'] = 'F'
                else:
                    control.loc[len(control)] = {'url':url,'page':page,'status':'F'}
                continue
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('div', class_='product_title')
            reviews = soup.find('div', class_='product_reviews')
            product = ''
            platform = ''
            if(title):
                productHead = title.find('h1')
                if(productHead):
                    product = productHead.text
                platformHead = title.find('span', class_='platform')
                if(platformHead):
                    platform = platformHead.text.strip()
            if(product and reviews):
                for review in reviews.find_all('div', class_='review_content'):
                    row = {'name':'', 'product':'', 'platform':'', 'date':'', 'rating':'', 'upVotes':'', 'totVotes':'', 'review':'', 'langreview':''}
                    name = review.find('div', class_='name')
                    if name:
                        row['name'] = name.text.strip().replace('\n','')
                    row['product'] = product
                    row['platform'] = platform
                    date = review.find('div', class_='date')
                    if(date):
                        row['date'] = date.text 
                    rating = review.find('div', class_='review_grade')
                    if(rating):
                        row['rating'] = rating.text.strip().replace('\n','')
                    upsVotes = review.find('span', class_='total_ups')
                    if(upsVotes):
                        row['upVotes'] = upsVotes.text
                    totVotes = review.find('span', class_='total_thumbs')
                    if(totVotes):
                        row['totVotes'] = totVotes.text
                    content = review.find('span', class_='blurb blurb_expanded')
                    if(content):
                        row['review'] = content.text.replace('\n',' ').replace('\r','').strip()
                    else:
                        content = review.find('div', class_='review_body')
                        if(content):
                            row['review'] = content.text.replace('\n',' ').strip()
                    review_dict.loc[len(review_dict)] = row
                if(len(control.loc[filter1 & filter2]) > 0):
                    control.loc[filter1 & filter2,'status'] = 'S'
                else:
                    control.loc[len(control)] = {'url':url,'page':page,'status':'S'}
                procesadas += 1
                resources.loc[resources.url == url, 'paginasProcesadas'] += 1
            else:
                if(len(control.loc[filter1 & filter2]) > 0):
                    control.loc[filter1 & filter2,'status'] = 'F'
                else:
                    control.loc[len(control)] = {'url':url,'page':page,'status':'F'}
        if(procesadas == numPages):
            resources.loc[resources.url == url, 'status'] = 'S'
        else:
            resources.loc[resources.url == url, 'status'] = 'P'
        i += 1
        control.to_csv('control.csv',index=False)
        resources.to_csv('urls.csv',index=False)
        review_dict.to_csv('trainingSet.csv', index = False, header=True)
    print('')
    print('Descarga terminada')
    print('Detectando idiomas...')

    pendingReviews = review_dict.query('langreview == ""')
    readyReviews = review_dict.query('langreview != ""')

    # Deteccion de idiomas paralelo
    cores = mp.cpu_count()-1
    print('  Usando: {} cores'.format(cores))
    split_reviews = np.array_split(pendingReviews, cores)
    pool = mp.Pool(cores)
    newReviews = pd.concat(pool.map(add_language,split_reviews))
    newReviews = pd.concat([newReviews,readyReviews])
    #review_dict['langreview'] = review_dict['review'].apply(detect)


    print('Guardando resultados')
    control.to_csv('control.csv',index=False)
    resources.to_csv('urls.csv',index=False)
    newReviews.to_csv('trainingSet.csv', index = False, header=True)

    exitosas = len(resources.query('status == "S"'))
    parciales = len(resources.query('status == "P"'))
    fallidas = len(resources.query('status == "F"'))
    pagFallidas = len(control.query('status == "F"'))
    total = len(newReviews)
    print('******************************')
    print('Resumen:')
    print('- Total de reviews: {}'.format(total))
    print('- Urls Exitosas: {}'.format(exitosas))
    print('- Urls Parciales: {}'.format(parciales))
    print('- Urls Fallidas: {}'.format(fallidas))
    print('- Paginas Fallidas: {}'.format(pagFallidas))