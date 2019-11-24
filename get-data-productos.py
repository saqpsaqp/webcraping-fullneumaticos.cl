'''
Desc:   WebCrapping to extract tires data from fullneumaticos.cl
Author: Saúl Quintero
        saqpsaqp@gmail.com
'''
import urllib.request
from bs4 import BeautifulSoup
import time
import re
import pprint
import sys
import numpy as NP
import csv
from requests.utils import requote_uri

class WebCrapingData:
    
    urlBase = ""

    def __init__(self, urlBase):
        self.urlBase = requote_uri(urlBase)
    
    def extraerData(self):

        DATA = {}
        
        page_inicio = None
        reintento = 1
        reintentos = 3
        while True:
            try:
                page_inicio = urllib.request.urlopen(self.urlBase).read().decode("utf-8", 'ignore')
                break
            except:
                print("No se puede conectar a: "+self.urlBase+". Intentando "+str(reintento)+"/"+str(reintentos))
                reintento = reintento + 1
                time.sleep(3)
                if reintento > reintentos:
                    return None
        
        soup_inicio = BeautifulSoup(page_inicio,features="html.parser")

        # Extrayendo Nombre Producto
        h1_title = soup_inicio.find_all('h1')
        title_text = h1_title[0].get_text()

        # Extrayendo Rin del Neumático
        rin_search = re.search('R[0-9]{1,2}', title_text, re.IGNORECASE)
        rin_text = ""
        if rin_search:
            rin_text = rin_search.group(0)

        # Extrayendo Perfil del Neumático
        perfil_text = ""
        perfil_search = re.search('(/[\d]{2})', title_text, re.IGNORECASE)
        if perfil_search:
            perfil_text = perfil_search.group(0).replace('/','')

        # Extrayendo Ancho del Neumático
        ancho_text = ""
        ancho_search = re.search('([\d]{2,3}/)', title_text, re.IGNORECASE)
        if ancho_search:
            ancho_text = ancho_search.group(0).replace('/','')

        # Extrayendo Código
        div_title = soup_inicio.find('div', class_='col-lg-6 col-md-6 col-sm-6 col-xs-12 col-ms-12 datos-destacado')
        p_title = div_title.p.get_text()
        codigo_text = ""
        codigo_search = re.search('(Código: )[\w]*[\d]*', p_title, re.IGNORECASE)
        if codigo_search:
            codigo_text = codigo_search.group(0).replace('Código: ','').strip()
        
        # Extrayendo procedencia
        procedencia_text = ""
        procedencia_search = re.search('(Procedencia: )[\w]*[\d]*', p_title, re.IGNORECASE)
        if procedencia_search:
            procedencia_text = procedencia_search.group(0).replace('Procedencia: ','').strip()
        
        # Extrayendo Marca
        marca_text = ""
        marca_search = re.search('([\w]*$)', title_text, re.IGNORECASE)
        if marca_search:
            marca_text = marca_search.group(0)

        # Extrayendo precio
        p_precio = soup_inicio.find('p', class_='precio-unidad-final')
        precio_text = p_precio.get_text().replace('Precio unidad: ','')
        
        # Extrayendo url imagen
        div_imagen = soup_inicio.find('div', class_='img-neumatico-destacado')
        tag_img = div_imagen.img
        imagen_url = tag_img.get('src')

        # Extrayendo Descripcion
        div_descripcion = soup_inicio.find('div', class_='col-lg-10 col-md-12 col-sm-12 col-xs-12 hidden-ms')
        descripcion_text = div_descripcion.p.get_text().replace('<br/>','').strip()
        
        DATA['Nombre'] = title_text
        DATA['Rin'] = rin_text
        DATA['Perfil'] = perfil_text
        DATA['Ancho'] = ancho_text
        DATA['Marca'] = marca_text
        DATA['Codigo'] = codigo_text
        DATA['Procedencia'] = procedencia_text
        DATA['Precio'] = precio_text
        DATA['ImagenUrl'] = imagen_url
        DATA['Descripcion'] = descripcion_text
        
        return DATA

#def guardarImagen(URL,FOLDER):


def leerUrls(FILETXT):
    f = open(FILETXT,'r')
    x = f.readlines()
    f.close()
    return x

def guardarCSV(DATA):
    csv_columns = ['Nombre','Marca','Rin','Perfil','Ancho','Codigo','Procedencia','Precio','Descripcion','ImagenUrl']
    csv_file = "Productos.csv"
    try:
        with open(csv_file, 'a') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writerow(DATA)
    except IOError:
        print("I/O error")

def procesar(URLS):

    for URL in URLS:
        URL = URL.replace('\n','')
        print("Procesando "+URL+"...")
        app = WebCrapingData(URL)
        DATA = app.extraerData()
        guardarCSV(DATA)
        time.sleep(2)



URLS_DATA = leerUrls("urls-productos-test.txt")
procesar(URLS_DATA)

#

#app.iniciarProceso()

#print(app.getUrlsProductosEncontrados())
#print(str(len(app.getUrlsProductosEncontrados())))
#NP.savetxt("urls-productos.txt",NP.array(app.getUrlsProductosEncontrados()),fmt="%s")

