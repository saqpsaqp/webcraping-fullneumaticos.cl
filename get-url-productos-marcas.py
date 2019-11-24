'''
Desc:   WebCrapping to extract url of products by marca from fullneumaticos.cl
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

class WebCraping:
    
    urlsProductosEncontrados = []
    urlBase = ""

    def __init__(self, urlBase):
        self.urlBase = urlBase

    def getUrlsProductosEncontrados(self):
        return self.urlsProductosEncontrados
    
    def extraerUrlMarcas(self):

        URLS_MARCAS_DIC = []
        # Se obtiene el contenido de la página web inicial
        # y se extraen los enlaces del menu de Marcas        # 

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
        tags_menu = soup_inicio.find_all('li', class_='dropdown')
        #regex_nombre_marca = r"^[\w\W]*(neumaticos-)|(.php)"
        for tag_menu in tags_menu:
            tipo_menu = tag_menu.a.text.strip()
            if(tipo_menu == 'MARCAS'):
                
                tags_urls = tag_menu.find_all('a')

                for tag_url in tags_urls[1:]:
                    #nombre_marca = tag_url.get('href')
                    #nombre_marca = re.sub(regex_nombre_marca, "", nombre_marca, 0, re.MULTILINE)
                    URLS_MARCAS_DIC.append(tag_url.get('href'))
        print("======================================")
        print("URl extraidas: "+str(len(URLS_MARCAS_DIC)))
        print("======================================")
        return URLS_MARCAS_DIC
    
    def extraerRinesMarca(self, URL_MARCA):

        URLS_RINES_MARCA = []

        # Se carga la página de la marca correspondiente
        # y se extraen los enlaces a los tipos de rin

        page_marca = None
        reintento = 1
        reintentos = 3
        while True:
            try:
                page_marca = urllib.request.urlopen(URL_MARCA).read().decode("utf-8", 'ignore')
                break
            except:
                print("No se puede conectar a: "+URL_MARCA+". Intentando "+str(reintento)+"/"+str(reintentos))
                reintento = reintento + 1
                time.sleep(3)
                if reintento > reintentos:
                    return None
        
        soup_marca = BeautifulSoup(page_marca,features="html.parser")
        tags_rines = soup_marca.find_all('a', class_='btn btn-default')

        print("===========================================================")
        print("Extrayendo URL Rines de: "+URL_MARCA)
        print("===========================================================")

        for tag_rin in tags_rines:
            print("RIN: "+tag_rin.text)
            print("URL: "+self.urlBase+tag_rin.get('href'))
            print("------------------------------------")
            URLS_RINES_MARCA.append(self.urlBase+tag_rin.get('href'))
        
        return URLS_RINES_MARCA

    def extraerPaginas(self,URL_RIN):
        sufijo = "-orden--pos-"
        posicion = 0
        cantidad = 20

        # Para cada página de marca y rin, se extrae el contenido
        # de los resultados de cada página de resultados (paginado)

        page_rin = None
        reintento = 1
        reintentos = 3
        while True:
            try:
                page_rin = urllib.request.urlopen(URL_RIN).read().decode("utf-8", 'ignore')
                break
            except:
                print("No se puede conectar a: "+URL_RIN+". Intentando "+str(reintento)+"/"+str(reintentos))
                reintento = reintento + 1
                time.sleep(3)
                if reintento > reintentos:
                    return None

        
        soup_rin = BeautifulSoup(page_rin,features="html.parser")
        div_paginador = soup_rin.find_all('div', class_='paginador')
        
        tag_strong = div_paginador[0].find_all('strong')
        tag_a = div_paginador[0].find_all('a')
        if(len(tag_strong)>0):
            # Al menos hay un página de resultados.
            # Se extraen los resultados obtenidos y se revisa las siguientes páginas
            div_resultados = soup_rin.find_all('div', class_='shadow padding-shadow-tablas')
            print("Hay "+str(len(div_resultados))+" resultados en la página 1")

            for div_resultado in div_resultados:
                div_producto_parcial = div_resultado.find('div',class_='col-lg-4 col-md-3 col-sm-3 col-xs-7')
                a_producto_parcial = div_producto_parcial.find('a')
                self.urlsProductosEncontrados.append(self.urlBase+a_producto_parcial.get('href'))

            # Se itera por cad psible página de resultados
            pagina = 1
            while True:
                posicion = posicion + cantidad
                pagina = pagina + 1
                
                page_siguiente = None
                reintento = 1
                reintentos = 3
                while True:
                    try:
                        page_siguiente = urllib.request.urlopen(URL_RIN+sufijo+str(posicion)).read().decode("utf-8", 'ignore')
                        break
                    except:
                        print("No se puede conectar a: "+URL_RIN+sufijo+str(posicion)+". Intentando "+str(reintento)+"/"+str(reintentos))
                        reintento = reintento + 1
                        time.sleep(3)
                        if reintento > reintentos:
                            return None
                
                soup_siguiente = BeautifulSoup(page_siguiente,features="html.parser")
                resultados_siguiente = soup_siguiente.find_all('div', class_='shadow padding-shadow-tablas')
                print("Hay "+str(len(resultados_siguiente))+" resultados en la página "+str(pagina))
                
                if (len(resultados_siguiente)==0):
                    break

                for resultado_siguiente in resultados_siguiente:
                    div_producto_parcial = resultado_siguiente.find('div',class_='col-lg-4 col-md-3 col-sm-3 col-xs-7')
                    a_producto_parcial = div_producto_parcial.find('a')
                    self.urlsProductosEncontrados.append(self.urlBase+a_producto_parcial.get('href'))
                
                time.sleep(1)

        else:
            print("No hay paginas")


    def iniciarProceso(self):

        URLS_MARCAS_DIC = self.extraerUrlMarcas()
        for URL_MARCA in URLS_MARCAS_DIC: #[:1]:
            URLS_RINES = self.extraerRinesMarca(URL_MARCA)
            for URL_RIN in URLS_RINES: #[:3]:
                self.extraerPaginas(URL_RIN)
                time.sleep(2)
            time.sleep(2)
    

app = WebCraping("https://www.fullneumaticos.cl/")

app.iniciarProceso()

print(app.getUrlsProductosEncontrados())
print(str(len(app.getUrlsProductosEncontrados())))
NP.savetxt("urls-productos.txt",NP.array(app.getUrlsProductosEncontrados()),fmt="%s")

