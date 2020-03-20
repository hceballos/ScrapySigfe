# scrapy crawl devengo
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.http import FormRequest
import requests
import scrapy
import os
import re
import requests
import json


class Sigfe3SpiderSpider(scrapy.Spider):

    def monto(self, linea):
        cadena  = re.findall('(?<=<nobr>).*?(?=<\/nobr><\/td>)', linea)[5]
        monto   = cadena.replace('.', '')
        return int(monto)

    URL = 'https://www.sigfe.gob.cl/sigfe/faces/autenticacion'
    name = 'devengo'
    start_urls = [URL]

    #rules = (Rule(LinkExtractor(allow=(), restrict_xpaths=('//a[@class="button next"]',)), callback="parse_page", follow= True),)

    def parse(self, response):
        if len(response.xpath('//html').re(r"2008, Oracle and")) == 1:
            return scrapy.Request(
                url = response.url + '?_afrLoop=' + response.xpath('//html').re(r"_afrLoop=(\d+)")[0],
                callback = self.parse
            )

        if len(response.xpath('//html').re(r"Formulario de Autenticaci")) == 1:
            return scrapy.FormRequest.from_response(
                response,
                formdata = {
                    'j_username': 'hceballosa',
                    'j_password': 'Finanzas01',
                    'event': 'idCBIngresar',
                    'event.idCBIngresar': '<m xmlns="http://oracle.com/richClient/comm"><k v="type"><s>action</s></k></m>'
                },
                callback = self.redireccionador
            )

    def redireccionador(self, response):
        if len(response.xpath('//html').re(r"2008, Oracle and")) == 1:
            return scrapy.Request(
                url = response.url+'?_afrWindowMode=0&_afrLoop='+response.xpath('//html').re(r"_afrLoop=(\d+)")[0],
                callback = self.bienvenido
            )

    def bienvenido(self, response):
        if response.xpath('//*[@id="cmdLSC"]/text()').extract_first() == 'Cerrar Sesion Activa':
            print("          >>>>>>>>>>>>>>>>>>>>>>> ESTADO :", re.findall('(?<=href="#">).*?(?=<\/a><div><\/div>)',response.text)[0], "<<<<<<<<<<<<<<<<<<<<<<<" )
            return scrapy.FormRequest.from_response(
                response,
                url = 'https://www.sigfe.gob.cl/sigfe/faces/errorAutenticacion?error=used_user;1739;hceballosa',
                formdata = {
                    '_adf.ctrl-state': re.findall(r'ctrl-state=(.+)', response.url)[0],
                    'org.apache.myfaces.trinidad.faces.FORM': 'idFormGeneraVariacion',
                    'event': 'cmdLSC',
                    'event.cmdLSC': '<m xmlns="http://oracle.com/richClient/comm"><k v="type"><s>action</s></k></m>'
                },
                callback = self.parse
            )

        if len(response.xpath('//html').re(r"2008, Oracle and")) == 1:
            return scrapy.Request(
                url = response.url+'&_afrLoop='+response.xpath('//html').re(r"_afrLoop=(\d+)")[0],
                callback = self.bienvenido
            )


        return scrapy.FormRequest.from_response(
            response,
            formdata = {
                'event'                 : 'idPgTpl:j_id31',
                'event.idPgTpl:j_id31'  : '<m xmlns="http://oracle.com/richClient/comm"><k v="type"><s>action</s></k></m>'
            },
            callback= self.consulta
        )

    def consulta(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formdata = {
                'idTmpB:idSeonraOpcionBusqueda'                         : '0' ,
                'idTmpB:filtroEjercicioId'                              : '11' ,
                #'idTmpB:idFolioVariacion'                               : '02691',
                'org.apache.myfaces.trinidad.faces.FORM'                : 'idTmpB:idFormBuscarVariacion',
                'event'                                                 : 'idTmpB:compBotonBuscarVarPresu:idCmbIrBuscar',
                'event.idTmpB:compBotonBuscarVarPresu:idCmbIrBuscar'    : '<m xmlns="http://oracle.com/richClient/comm"><k v="type"><s>action</s></k></m>'
            },
            callback= self.CriteriosDeBusqueda
        )


    def CriteriosDeBusqueda(self, response):
        LineasDeTabla = response.xpath('//html').re(r'(?<=_afrrk=").*?(?=Historial de Ajustes)')
        for linea in LineasDeTabla:
            print(" ")
            #print(linea)
            """
            print('     A.Numero_Linea       : ' , str(re.findall('(?<="idTmpB:tRes:).(?=:idCmlIrVisualizar)',linea)[0]) )
            print('     B.Id                 : ' , re.findall('(?<=<nobr>).*?(?=<\/nobr><\/td>)', linea)[0] )
            print('     C.Folio              : ' , re.findall('(?<=<nobr>).*?(?=<\/nobr><\/td>)', linea)[1] )
            print('     D.Ejercicio          : ' , re.findall('(?<=<nobr>).*?(?=<\/nobr><\/td>)', linea)[2] )
            print('     E.Numero_Documento   : ' , re.findall('(?<=<nobr>).*?(?=<\/nobr><\/td>)', linea)[3] )
            print('     F.Moneda             : ' , re.findall('(?<=<nobr>).*?(?=<\/nobr><\/td>)', linea)[4] )
            print('     G.Monto              : ' , re.findall('(?<=<nobr>).*?(?=<\/nobr><\/td>)', linea)[3] )
            print('     F.todo               : ' , re.findall('(?<=<nobr>).*?(?=<\/nobr><\/td>)', linea) )
            print('     Event                : ' , re.findall('(?<=Ajustar<\/a><a id=").*?(?=" class="variacion buscar variacion)', linea)[0] )
            """

            if 'idTmpB:tRes:0:idCmlIrVisualizar' == re.findall('(?<=Ajustar<\/a><a id=").*?(?=" class="variacion buscar variacion)', linea)[0]:
                print( 'idTmpB:tRes:0:idCmlIrVisualizar' )

                yield scrapy.FormRequest.from_response(
                    response,
                    meta = {
                        'numero': '1',
                        'linea': linea
                    },
                    dont_filter = True,
                    formdata = {
                        'Request URL': response.url,
                        'idTmpB:idSeonraOpcionBusqueda':'0',
                        'idTmpB:filtroEjercicioId': '11',
                        'org.apache.myfaces.trinidad.faces.FORM': 'idTmpB:idFormBuscarVariacion',
                        'oracle.adf.view.rich.DELTAS': '{idTmpB:tRes={rows=10,scrollTopRowKey|p=0,selectedRowKeys=0}}',
                        'event': 'idTmpB:tRes:0:idCmlIrVisualizar',
                        'event.'+'idTmpB:tRes:0:idCmlIrVisualizar' : '<m xmlns="http://oracle.com/richClient/comm"><k v="type"><s>action</s></k></m>'
                    }
                )

                yield scrapy.FormRequest.from_response(
                    response,
                    meta = {
                        'numero': '1',
                        'linea' : linea
                    },
                    dont_filter = True,
                    formdata = {
                        'Request URL': response.url,
                        'Adf-Rich-Message': 'true',
                        'org.apache.myfaces.trinidad.faces.FORM': 'idTmpB:idFormcambioArea',
                        'oracle.adf.view.rich.DELTAS': '{idTmpB:tRes={scrollTopRowKey|p=0}}',
                        'event': 'VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs',
                        'event.VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs': '<m xmlns="http://oracle.com/richClient/comm"><k v="suppressMessageClear"><s>true</s></k><k v="type"><s>fetch</s></k></m>',
                        'oracle.adf.view.rich.PROCESS': 'VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs'
                    },
                    callback = self.modal
                )

                filename = 'if.html'
                with open(filename, 'wb') as f:
                    f.write(response.body)
                self.log('Saved file %s' % filename)



            else:
                print( 'Nones' )




        # Pagina siguiente - INICIO
        siguiente = re.findall(r'(?<=id="idTmpB:itLink:).*?(?=:linkDinamic")', response.text)[-1:]
        for x in siguiente:
            print(">>>>>>>>>>>>>>>>>>>< SIGUIENTE : ")

            yield scrapy.FormRequest.from_response(
                response,
                formdata = {
                    'idTmpB:idSeonraOpcionBusqueda': '0',
                    'idTmpB:filtroEjercicioId': '11',
                    'org.apache.myfaces.trinidad.faces.FORM': 'idTmpB:idFormBuscarVariacion',
                    'oracle.adf.view.rich.DELTAS': '{idTmpB:tRes={rows=10,scrollTopRowKey|p=0}}',
                    'event': 'idTmpB:itLink:'+x+':linkDinamic',
                    'event.idTmpB:itLink:'+x+':linkDinamic': '<m xmlns="http://oracle.com/richClient/comm"><k v="type"><s>action</s></k></m>'
                },
                callback= self.CriteriosDeBusqueda
            )
        # Pagina siguiente - FIN




    def modal(self, response):

        numero  = response.meta.get('numero')
        linea   = response.meta.get('linea')

        print('     A.Numero_Linea       : ' , str(re.findall('(?<="idTmpB:tRes:).(?=:idCmlIrVisualizar)',linea)[0]) )
        print('     B.Id                 : ' , re.findall('(?<=<nobr>).*?(?=<\/nobr><\/td>)', linea)[0] )
        print('     C.Folio              : ' , re.findall('(?<=<nobr>).*?(?=<\/nobr><\/td>)', linea)[1] )
        print('     D.Ejercicio          : ' , re.findall('(?<=<nobr>).*?(?=<\/nobr><\/td>)', linea)[2] )
        print('     E.Numero_Documento   : ' , re.findall('(?<=<nobr>).*?(?=<\/nobr><\/td>)', linea)[3] )
        print('     F.Moneda             : ' , re.findall('(?<=<nobr>).*?(?=<\/nobr><\/td>)', linea)[4] )
        print('     G.Monto              : ' , re.findall('(?<=<nobr>).*?(?=<\/nobr><\/td>)', linea)[3] )
        print('     F.todo               : ' , re.findall('(?<=<nobr>).*?(?=<\/nobr><\/td>)', linea) )
        print('     Event                : ' , re.findall('(?<=Ajustar<\/a><a id=").*?(?=" class="variacion buscar variacion)', linea)[0] )



        print("modal : ", numero )
        print("modal : ", linea )

        filename = str(numero)+'.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)

        """
        org.apache.myfaces.trinidad.faces.FORM: idTmpB:idFormBuscarVariacion
        javax.faces.ViewState: !-1241s4dqc4
        oracle.adf.view.rich.DELTAS: {idTmpB:tRes={rows=10,scrollTopRowKey|p=0,selectedRowKeys=0}}
        event: idTmpB:tRes:0:idCmlIrVisualizar
        event.idTmpB:tRes:0:idCmlIrVisualizar: <m xmlns="http://oracle.com/richClient/comm"><k v="type"><s>action</s></k></m>


        # -----------------------------------
        idTmpB:idSeonraOpcionBusqueda: 0
        idTmpB:filtroEjercicioId: 11
        org.apache.myfaces.trinidad.faces.FORM: idTmpB:idFormBuscarVariacion
        oracle.adf.view.rich.DELTAS: {idTmpB:tRes={rows=10,scrollTopRowKey|p=0,selectedRowKeys=0}}
        event: idTmpB:tRes:0:idCmlIrVisualizar
        event.idTmpB:tRes:0:idCmlIrVisualizar: <m xmlns="http://oracle.com/richClient/comm"><k v="type"><s>action</s></k></m>

        org.apache.myfaces.trinidad.faces.FORM: idTmpB:idFormcambioArea
        oracle.adf.view.rich.DELTAS: {idTmpB:tRes={scrollTopRowKey|p=0}}
        event: VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs
        event.VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs: <m xmlns="http://oracle.com/richClient/comm"><k v="suppressMessageClear"><s>true</s></k><k v="type"><s>fetch</s></k></m>
        oracle.adf.view.rich.PROCESS: VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs
        # -----------------------------------
        idTmpB:idSeonraOpcionBusqueda: 0
        idTmpB:filtroEjercicioId: 11
        org.apache.myfaces.trinidad.faces.FORM: idTmpB:idFormBuscarVariacion
        oracle.adf.view.rich.DELTAS: {VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs={_shown=},idTmpB:tRes={selectedRowKeys=1}}
        event: idTmpB:tRes:1:idCmlIrVisualizar
        event.idTmpB:tRes:1:idCmlIrVisualizar: <m xmlns="http://oracle.com/richClient/comm"><k v="type"><s>action</s></k></m>

        org.apache.myfaces.trinidad.faces.FORM: idTmpB:idFormcambioArea
        oracle.adf.view.rich.DELTAS: {idTmpB:tRes={scrollTopRowKey|p=0}}
        event: VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs
        event.VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs: <m xmlns="http://oracle.com/richClient/comm"><k v="suppressMessageClear"><s>true</s></k><k v="type"><s>fetch</s></k></m>
        oracle.adf.view.rich.PROCESS: VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs
        # -----------------------------------
        idTmpB:idSeonraOpcionBusqueda: 0
        idTmpB:filtroEjercicioId: 11
        org.apache.myfaces.trinidad.faces.FORM: idTmpB:idFormBuscarVariacion
        oracle.adf.view.rich.DELTAS: {VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs={_shown=}}
        event: idTmpB:tRes:2:idCmlIrVisualizar
        event.idTmpB:tRes:2:idCmlIrVisualizar: <m xmlns="http://oracle.com/richClient/comm"><k v="type"><s>action</s></k></m>

        org.apache.myfaces.trinidad.faces.FORM: idTmpB:idFormcambioArea
        oracle.adf.view.rich.DELTAS: {idTmpB:tRes={scrollTopRowKey|p=0}}
        event: VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs
        event.VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs: <m xmlns="http://oracle.com/richClient/comm"><k v="suppressMessageClear"><s>true</s></k><k v="type"><s>fetch</s></k></m>
        oracle.adf.view.rich.PROCESS: VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs
        # -----------------------------------
        idTmpB:idSeonraOpcionBusqueda: 0
        idTmpB:filtroEjercicioId: 11
        org.apache.myfaces.trinidad.faces.FORM: idTmpB:idFormBuscarVariacion
        oracle.adf.view.rich.DELTAS: {VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs={_shown=},idTmpB:tRes={selectedRowKeys=3}}
        event: idTmpB:tRes:3:idCmlIrVisualizar
        event.idTmpB:tRes:3:idCmlIrVisualizar: <m xmlns="http://oracle.com/richClient/comm"><k v="type"><s>action</s></k></m>

        org.apache.myfaces.trinidad.faces.FORM: idTmpB:idFormcambioArea
        oracle.adf.view.rich.DELTAS: {idTmpB:tRes={scrollTopRowKey|p=0}}
        event: VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs
        event.VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs: <m xmlns="http://oracle.com/richClient/comm"><k v="suppressMessageClear"><s>true</s></k><k v="type"><s>fetch</s></k></m>
        oracle.adf.view.rich.PROCESS: VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs
        # -----------------------------------
        idTmpB:idSeonraOpcionBusqueda: 0
        idTmpB:filtroEjercicioId: 11
        org.apache.myfaces.trinidad.faces.FORM: idTmpB:idFormBuscarVariacion
        oracle.adf.view.rich.DELTAS: {VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs={_shown=},idTmpB:tRes={selectedRowKeys=4}}
        event: idTmpB:tRes:4:idCmlIrVisualizar
        event.idTmpB:tRes:4:idCmlIrVisualizar: <m xmlns="http://oracle.com/richClient/comm"><k v="type"><s>action</s></k></m>

        org.apache.myfaces.trinidad.faces.FORM: idTmpB:idFormcambioArea
        oracle.adf.view.rich.DELTAS: {idTmpB:tRes={scrollTopRowKey|p=0}}
        event: VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs
        event.VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs: <m xmlns="http://oracle.com/richClient/comm"><k v="suppressMessageClear"><s>true</s></k><k v="type"><s>fetch</s></k></m>
        oracle.adf.view.rich.PROCESS: VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs
        # -----------------------------------
        idTmpB:idSeonraOpcionBusqueda: 0
        idTmpB:filtroEjercicioId: 11
        org.apache.myfaces.trinidad.faces.FORM: idTmpB:idFormBuscarVariacion
        oracle.adf.view.rich.DELTAS: {VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs={_shown=},idTmpB:tRes={selectedRowKeys=5}}
        event: idTmpB:tRes:5:idCmlIrVisualizar
        event.idTmpB:tRes:5:idCmlIrVisualizar: <m xmlns="http://oracle.com/richClient/comm"><k v="type"><s>action</s></k></m>

        org.apache.myfaces.trinidad.faces.FORM: idTmpB:idFormcambioArea
        oracle.adf.view.rich.DELTAS: {idTmpB:tRes={scrollTopRowKey|p=0}}
        event: VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs
        event.VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs: <m xmlns="http://oracle.com/richClient/comm"><k v="suppressMessageClear"><s>true</s></k><k v="type"><s>fetch</s></k></m>
        oracle.adf.view.rich.PROCESS: VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs
        # -----------------------------------
        org.apache.myfaces.trinidad.faces.FORM: idTmpB:idFormcambioArea
        oracle.adf.view.rich.DELTAS: {idTmpB:tRes={scrollTopRowKey|p=0}}
        event: VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs
        event.VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs: <m xmlns="http://oracle.com/richClient/comm"><k v="suppressMessageClear"><s>true</s></k><k v="type"><s>fetch</s></k></m>
        oracle.adf.view.rich.PROCESS: VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs

        idTmpB:idSeonraOpcionBusqueda: 0
        idTmpB:filtroEjercicioId: 11
        org.apache.myfaces.trinidad.faces.FORM: idTmpB:idFormBuscarVariacion
        oracle.adf.view.rich.DELTAS: {VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs={_shown=}}
        event: idTmpB:tRes:6:idCmlIrVisualizar
        event.idTmpB:tRes:6:idCmlIrVisualizar: <m xmlns="http://oracle.com/richClient/comm"><k v="type"><s>action</s></k></m>
        # -----------------------------------
        org.apache.myfaces.trinidad.faces.FORM: idTmpB:idFormcambioArea
        javax.faces.ViewState: !dwl9xif5k
        oracle.adf.view.rich.DELTAS: {idTmpB:tRes={scrollTopRowKey|p=0}}
        event: VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs
        event.VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs: <m xmlns="http://oracle.com/richClient/comm"><k v="suppressMessageClear"><s>true</s></k><k v="type"><s>fetch</s></k></m>
        oracle.adf.view.rich.PROCESS: VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs

        idTmpB:idSeonraOpcionBusqueda: 0
        idTmpB:filtroEjercicioId: 11
        org.apache.myfaces.trinidad.faces.FORM: idTmpB:idFormBuscarVariacion
        oracle.adf.view.rich.DELTAS: {VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs={_shown=},idTmpB:tRes={selectedRowKeys=7}}
        event: idTmpB:tRes:7:idCmlIrVisualizar
        event.idTmpB:tRes:7:idCmlIrVisualizar: <m xmlns="http://oracle.com/richClient/comm"><k v="type"><s>action</s></k></m>
        # -----------------------------------
        org.apache.myfaces.trinidad.faces.FORM: idTmpB:idFormcambioArea
        oracle.adf.view.rich.DELTAS: {idTmpB:tRes={scrollTopRowKey|p=0}}
        event: VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs
        event.VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs: <m xmlns="http://oracle.com/richClient/comm"><k v="suppressMessageClear"><s>true</s></k><k v="type"><s>fetch</s></k></m>
        oracle.adf.view.rich.PROCESS: VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs

        idTmpB:idSeonraOpcionBusqueda: 0
        idTmpB:filtroEjercicioId: 11
        org.apache.myfaces.trinidad.faces.FORM: idTmpB:idFormBuscarVariacion
        oracle.adf.view.rich.DELTAS: {VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs={_shown=},idTmpB:tRes={selectedRowKeys=8}}
        event: idTmpB:tRes:8:idCmlIrVisualizar
        event.idTmpB:tRes:8:idCmlIrVisualizar: <m xmlns="http://oracle.com/richClient/comm"><k v="type"><s>action</s></k></m>
        # -----------------------------------
        org.apache.myfaces.trinidad.faces.FORM: idTmpB:idFormcambioArea
        javax.faces.ViewState: !dwl9xif5m
        oracle.adf.view.rich.DELTAS: {idTmpB:tRes={scrollTopRowKey|p=0}}
        event: VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs
        event.VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs: <m xmlns="http://oracle.com/richClient/comm"><k v="suppressMessageClear"><s>true</s></k><k v="type"><s>fetch</s></k></m>
        oracle.adf.view.rich.PROCESS: VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs

        idTmpB:idSeonraOpcionBusqueda: 0
        idTmpB:filtroEjercicioId: 11
        org.apache.myfaces.trinidad.faces.FORM: idTmpB:idFormBuscarVariacion
        oracle.adf.view.rich.DELTAS: {VisualizaOtrosDocsPopup:idPopVisualizaOtrosDocs={_shown=},idTmpB:tRes={selectedRowKeys=9}}
        event: idTmpB:tRes:9:idCmlIrVisualizar
        event.idTmpB:tRes:9:idCmlIrVisualizar: <m xmlns="http://oracle.com/richClient/comm"><k v="type"><s>action</s></k></m>
        """









