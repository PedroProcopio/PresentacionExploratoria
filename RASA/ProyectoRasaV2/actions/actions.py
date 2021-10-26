# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


import json
import logging
import copy
from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests
import csv
import re
import pandas as pd
import urllib3
import time
import datetime

class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="Hello World!")

        return []
class ActionDataRead(Action):
    def documentar(usuario, idGrupo, conducta):
        t = time.localtime()
        current_time = time.strftime("%a, %d %b %Y %H:%M:%S +0000", t)
        archivo = open('C:\\Users\\Tobias\\ProyectoRasaV2\\DB\\logIntervenciones.txt', 'a')
        archivo.write( current_time +', '+ usuario +', '+ idGrupo + ' se detecto la conducta ' + conducta + '\n')

    def name(self) -> Text:
        return "action_DataRead"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        input_data=tracker.latest_message
        #print(input_data["metadata"]["message"]["from"])
        user_info=input_data["metadata"]["message"]["from"]
        user_name=input_data["metadata"]["message"]["from"]["first_name"]
        group_id=input_data["metadata"]["message"]["chat"]["title"] 
        user_id=input_data["metadata"]["message"]["from"]["id"] 
        user_id2=input_data["metadata"]["message"]["chat"]["id"]     
        intencion = tracker.get_intent_of_latest_message()

        #Analizar si intervenir o no y modificar relacion con el grupo.
        ActionDataRead.RD(str(user_name),str(group_id),str(user_id))

        #Analizar si intervenir en el grupo o no dependiendo de la relacion general.
        ActionDataRead.intervencionGrupal(str(group_id),str(user_id2))

    def intervencionGrupal(grupo,id):
        datos = pd.read_csv("C:\\Users\\Tobias\\ProyectoRasaV2\\DB\\MatrizGrupo.csv",header= 0)
        total= datos[grupo].sum()

        datos2 = pd.read_csv("C:\\Users\\Tobias\\ProyectoRasaV2\\DB\\Grupos.csv",header= 0)

        datos3 = pd.read_csv("C:\\Users\\Tobias\\ProyectoRasaV2\\DB\\Perfiles.csv",header= 0)
        totalI = len(datos3.loc[(datos3["IDGROUP"] == "Rasa")]) #cantidad de intregrantes

        date1= datetime.datetime.now()
        if not(((datos2["Grupos"]==grupo)).any()):
            date2=str(date1.strftime('%Y-%m-%d'))
            datos2.loc[len(datos2)]=[grupo,total,date2,0]
        
        date2 = pd.to_datetime(datos2.loc[(datos2["Grupos"] == grupo),"UltInt"])
        diff = date1 - date2
        fecha=str(diff).split(" ")
        #print(fecha)
        datos2.loc[(datos2["Grupos"] == grupo),"Estado"]=total
        if ((total < -2*totalI) and (int(fecha[3]) >= 5 )):
            respuesta1="Estoy notando que la situacion del grupo esta un poco tensa, les recomiendo que charlen detenidamente lo que exige cada uno."
            respuesta2="Si no lo pueden resolver contactense con un profesor."
            ActionDataRead.Enviar_Mensaje(id,respuesta1)
            ActionDataRead.Enviar_Mensaje(id,respuesta2)
            datos2.loc[(datos2["Grupos"] == grupo),"UltInt"]=str(date1.strftime('%Y-%m-%d'))
            datos2.loc[(datos2["Grupos"] == grupo),"CantInt"]=float(datos2.loc[(datos2["Grupos"] == grupo),"CantInt"]) + 1
        datos2.to_csv("C:\\Users\\Tobias\\ProyectoRasaV2\\DB\\Grupos.csv", index=False)    


    def Enviar_Mensaje(id,respuesta):
        http = urllib3.PoolManager()
        url = 'https://api.telegram.org/bot1916645289:AAF8Re0v55EnPpJ3-orc6DlZL-zJwr5_Wa8/sendMessage?chat_id='+id+'&text='+respuesta
        http.request('GET', url)

    def I_sugerencia(usuario,id,grupo):
        respuesta1 = 'Hola ' + usuario + ', veo que estas teniendo dificultades para decidir en que parte del proyecto del grupo ' + grupo + ' participar'
        respuesta2 = 'Podrias optar por seguir alguno de los siguientes consejos:'
        respuesta3 = '• Consultarle al profesor que hacer en este caso'
        respuesta4 = '• Podrias trabajar en lo que consideres que le falta al trabajo, independientemente de lo que hagan tus compañeros'
        respuesta5 = '• Tratar de sumarte a lo que este haciendo otro compañero'
        #respuesta6 = 'https://www.youtube.com/watch?v=of_3rje8oKA&list=RDof_3rje8oKA&start_radio=1'
        ActionDataRead.Enviar_Mensaje(str(id),str(respuesta1))
        time.sleep(1.5)
        ActionDataRead.Enviar_Mensaje(str(id),str(respuesta2))
        time.sleep(1.5)
        ActionDataRead.Enviar_Mensaje(str(id),str(respuesta3))
        time.sleep(1.5)
        ActionDataRead.Enviar_Mensaje(str(id),str(respuesta5))
        time.sleep(1.5)
        ActionDataRead.Enviar_Mensaje(str(id),str(respuesta4))
        time.sleep(1.5)
        #ActionDataRead.Enviar_Mensaje(str(id),str(respuesta6))

    def I_daPocaOpinion(usuario,id, grupo,PV):
        respuesta1 = 'Hola ' + usuario + ', estoy notando que no estas participando mucho con tus compañeros de ' + grupo + ' a la hora de dar tu opinión'
        respuestaAlt1 = '---------------------------------------'
        respuestaAlt2 ='Por otro lado, tambien noto que no estas participando mucho con tus compañeros de ' + grupo + ' a la hora de dar tu opinion'
        respuesta2 = 'Estaría bueno que pudieras dar tu opinión más seguido'
        if (PV):
            time.sleep(3)
            ActionDataRead.Enviar_Mensaje(str(id),str(respuestaAlt1))
            ActionDataRead.Enviar_Mensaje(str(id),str(respuestaAlt2))
        else:
            ActionDataRead.Enviar_Mensaje(str(id),str(respuesta1))
        time.sleep(1.5)
        ActionDataRead.Enviar_Mensaje(str(id),str(respuesta2))

    def I_daMuchaOpinion(usuario,id, grupo, PV):
        respuesta1= usuario + ', gracias por brindar tu opinión y participar en el grupo ' + grupo +', pero estamos notando que estas participando mucho'
        respuestaAlt1 = '---------------------------------------'
        respuestaAlt2 = 'Por otro lado, algo bueno es que brindas tu opinion y sos participativo con el grupo ' + grupo + ' pero quiza te estas excediendo.'
        respuesta2= 'estaria bueno que des la oportunidad a tus compañeros de dar sus propias opiniones'
        respuesta3= 'si estas teniendo un problema con tus compañeros, no dudes en avisarle a tu profesor a cargo.'
        if (PV):
            time.sleep(3)
            ActionDataRead.Enviar_Mensaje(str(id),str(respuestaAlt1))
            ActionDataRead.Enviar_Mensaje(str(id),str(respuestaAlt2))
        else:
            ActionDataRead.Enviar_Mensaje(str(id),str(respuesta1))
        time.sleep(1.5)
        ActionDataRead.Enviar_Mensaje(str(id),str(respuesta2))
        time.sleep(1.5)
        ActionDataRead.Enviar_Mensaje(str(id),str(respuesta3))

    def I_daPocaInformacion(usuario,id, grupo, PV):
        respuesta1= 'Hola ' + usuario + ', estaria bueno que pudieras ayudar mas a tus compañeros de ' + grupo + '.'
        respuestaAlt1 = '---------------------------------------'
        respuestaAlt2 = 'Por otro lado, estaria bueno que pudieras ayudar mas a tus compañeros de ' + grupo + '.'
        respuesta2= 'participa mas con tus compañeros brindando todo tipo de informacion que consideres necesaria'
        respuesta3= 'queremos que todos participen brindando información que consideren relevante al grupo'
        if (PV):
            time.sleep(3)
            ActionDataRead.Enviar_Mensaje(str(id),str(respuestaAlt1))
            ActionDataRead.Enviar_Mensaje(str(id),str(respuestaAlt2))
        else:
            ActionDataRead.Enviar_Mensaje(str(id),str(respuesta1))
        time.sleep(1.5)
        ActionDataRead.Enviar_Mensaje(str(id),str(respuesta2))
        time.sleep(1.5)
        ActionDataRead.Enviar_Mensaje(str(id),str(respuesta3))
    
    def I_daMuchaInformacion(usuario,id, grupo,PV):
        respuesta1= 'Hola ' + usuario + ', te escribo porque note que en el grupo' + grupo + ' estas dando mucha informacion'
        respuestaAlt1 = '---------------------------------------'
        respuestaAlt2 = 'Ademas, noto que estas dando mucha informacion'
        respuesta2= 'el llamado de atención no es porque este mal esta conducta sino porque esperamos que todos los miembros del grupo participen en esa tarea'
        respuesta3= 'si tenes algun problema no dudes en consultarlo con el profesor a cargo' 
        if (PV):
            time.sleep(3)
            ActionDataRead.Enviar_Mensaje(str(id),str(respuestaAlt1))
            ActionDataRead.Enviar_Mensaje(str(id),str(respuestaAlt2))
        else:
            ActionDataRead.Enviar_Mensaje(str(id),str(respuesta1))
        time.sleep(1.5)
        ActionDataRead.Enviar_Mensaje(str(id),str(respuesta2))
        time.sleep(1.5)
        ActionDataRead.Enviar_Mensaje(str(id),str(respuesta3))

    def I_desacuerdo(usuario,id, grupo,PV):
        respuesta1= 'Hola ' + usuario + ', estuve viendo que en el grupo ' + grupo + ' hay conflicto de desacuerdo'
        respuestaAlt1 = '----------------------------------'
        respuestaAlt2 = 'Otro conflicto que noto es que, no estas logrando ponerte de acuerdo con tus compañeros de ' + grupo
        respuesta2= 'es normal a veces no estar de acuerdo, pero siempre escuchen a sus compañeros, traten de resolverlo por su cuenta'
        respuesta3= 'si no lo pueden resolver pueden consultar al profesor a cargo'
        if (PV):
            time.sleep(3)
            ActionDataRead.Enviar_Mensaje(str(id),str(respuestaAlt1))
            ActionDataRead.Enviar_Mensaje(str(id),str(respuestaAlt2))
        else:
            ActionDataRead.Enviar_Mensaje(str(id),str(respuesta1))
        time.sleep(1.5)
        ActionDataRead.Enviar_Mensaje(str(id),str(respuesta2))
        time.sleep(1.5)
        ActionDataRead.Enviar_Mensaje(str(id),str(respuesta3))

    def I_pideOpinion(usuario,id, grupo,PV):
        respuesta1 = 'Hola ' + usuario + ', te escribo porque note que estas pidiendo muchas opiniones, probablemente relacionadas con el desarrollo del trabajo'
        respuestaAlt1 = '---------------------------------------'
        respuestaAlt2 = 'Ademas, veo que estas pidiendo muchas opiniones, que seguramente estan relacionadas con el desarrollo del trabajo'
        respuesta2 = 'Desde aca puedo pensar que esto puede ser por dos razones:' 
        respuesta3 = '• Tus compañeros no te estan contestando'
        respuesta4 = '• No estas seguro de que deberían hacer ahora'
        respuesta5 = 'Si tus compañeros no te estan ayudando no dudes en insistir o finalmente hablar con el profesor a cargo, si es la segunda, traten de reunirse para discutir todas las ideas y aclarar los detalles del proyecto'
        if (PV):
            time.sleep(3)
            ActionDataRead.Enviar_Mensaje(str(id),str(respuestaAlt1))
            ActionDataRead.Enviar_Mensaje(str(id),str(respuestaAlt2))
        else:
            ActionDataRead.Enviar_Mensaje(str(id),str(respuesta1))
        time.sleep(1.5)
        ActionDataRead.Enviar_Mensaje(str(id),str(respuesta2))
        time.sleep(1.5)
        ActionDataRead.Enviar_Mensaje(str(id),str(respuesta3))
        time.sleep(1.5)
        ActionDataRead.Enviar_Mensaje(str(id),str(respuesta4))
        time.sleep(1.5)
        ActionDataRead.Enviar_Mensaje(str(id),str(respuesta5))

    def I_pideInformacion(usuario,id,grupo,PV):
        respuesta1 = 'Hola ' + usuario +', necesitas ayuda? Note que estas pidiendo mucha informacion en el grupo ' + grupo +' trata de descansar por tu cuenta y de releer los conceptos solo'
        respuestaAlt1 = '---------------------------------------'
        respuestaAlt2 = 'Otro conflicto que detectamos es que estas pidiendo mucha informacion sobre el trabajo'
        respuesta3 = 'No dudes en preguntarle a tu profesor si algo no te quedo claro' 
        respuesta2 = 'Si es un problema conceptual trataria de buscar informacion en internet o consultarlo con otras personas que lo conozcan'
        if (PV):
            time.sleep(3)
            ActionDataRead.Enviar_Mensaje(str(id),str(respuestaAlt1))
            ActionDataRead.Enviar_Mensaje(str(id),str(respuestaAlt2))
        else:
            ActionDataRead.Enviar_Mensaje(str(id),str(respuesta1))
        time.sleep(1.5)
        ActionDataRead.Enviar_Mensaje(str(id),str(respuesta3))
        time.sleep(1.5)
        ActionDataRead.Enviar_Mensaje(str(id),str(respuesta2))
        time.sleep(1.5)

    def I_participacion(usuario,id,grupo):
        respuesta1 = 'Hola ' + usuario +', note que estas teniendo poca participacion en el grupo ' + grupo
        respuesta2 = 'Si estas teniendo alguna clase de problema con los integrantes no dudes en charlarlo con ellos o con un profesor.'
        respuesta3 = 'Si tenes algun problema personal que te dificulta poder participar contactate lo antes posible con el profesor para poder llegar a una solucion.'
        ActionDataRead.Enviar_Mensaje(str(id),str(respuesta1))
        ActionDataRead.Enviar_Mensaje(str(id),str(respuesta2))
        ActionDataRead.Enviar_Mensaje(str(id),str(respuesta3))
   
    def SumarMatrizGrupo(usuario,grupo_id,numero):
        datos = pd.read_csv("C:\\Users\\Tobias\\ProyectoRasaV2\\DB\\MatrizGrupo.csv",header= 0)  
        if not(grupo_id in datos):
            datos[grupo_id] = 0 
        if not((datos["UG"]==usuario).any()):
            cant = len(datos.columns)
            lista = list()
            i = 0
            user=[usuario]
            while (i < cant-1):
                lista.append(0)
                i = i+1
            lis = user + lista
            datos.loc["UG"]=lis 
        if not((datos.loc[(datos["UG"]==usuario),grupo_id]).any()):
            datos.loc[(datos["UG"]==usuario),grupo_id] = 0 
        datos.loc[(datos["UG"]==usuario),grupo_id] = float(datos.loc[(datos["UG"]==usuario),grupo_id]) + float(numero)  
        datos.to_csv("C:\\Users\\Tobias\\ProyectoRasaV2\\DB\\MatrizGrupo.csv", index=False)
        #print(datos)  

    def RD(usuario,group_id,id):
        datos = pd.read_csv("C:\\Users\\Tobias\\ProyectoRasaV2\\DB\\Perfiles.csv",header= 0)  
        #print(datos)
        conductas = list()
        #agregamos a la lista los datos guardados en el csv sobre el usuario.
        Total = float(datos.loc[(datos["Nombre"]==usuario) & (datos["IDGROUP"]==group_id), "Total"])
        #print(Total)
        conductas.append(float(datos.loc[(datos["Nombre"]==usuario) & (datos["IDGROUP"]==group_id), "C1"])/ Total)
        conductas.append(float(datos.loc[(datos["Nombre"]==usuario) & (datos["IDGROUP"]==group_id), "C2"])/ Total)
        conductas.append(float(datos.loc[(datos["Nombre"]==usuario) & (datos["IDGROUP"]==group_id), "C3"])/ Total)
        conductas.append(float(datos.loc[(datos["Nombre"]==usuario) & (datos["IDGROUP"]==group_id), "C4"])/ Total)
        conductas.append(float(datos.loc[(datos["Nombre"]==usuario) & (datos["IDGROUP"]==group_id), "C5"])/ Total)
        conductas.append(float(datos.loc[(datos["Nombre"]==usuario) & (datos["IDGROUP"]==group_id), "C6"])/ Total)
        conductas.append(float(datos.loc[(datos["Nombre"]==usuario) & (datos["IDGROUP"]==group_id), "C7"])/ Total)
        conductas.append(float(datos.loc[(datos["Nombre"]==usuario) & (datos["IDGROUP"]==group_id), "C8"])/ Total)
        conductas.append(float(datos.loc[(datos["Nombre"]==usuario) & (datos["IDGROUP"]==group_id), "C9"])/ Total)
        #print(conductas)
        #print(conductas[0])
        umbral = float(datos.loc[(datos["Nombre"]==usuario) & (datos["IDGROUP"]==group_id), "Umbral"])
        #Planteamos las posibles situaciones donde el bot deberia intervenir.
        #-------------------
        datos2 = datos.loc[(datos["IDGROUP"] == group_id)]
        total2= datos2["Total"].sum()
        porcentaje = (float(datos2.loc[(datos2["Nombre"]==usuario) & (datos2["IDGROUP"]==group_id), "Total"])/float(total2))
        #-------------------               
        PV = False
        ActionDataRead.SumarMatrizGrupo(str(usuario),str(group_id),0)
        if ((porcentaje < 0.09) and (total2 >= len(datos2)*6)):
            ActionDataRead.I_participacion(usuario,id,group_id)
            PV=True
        if (umbral > 0):
            datos.loc[(datos["Nombre"]==usuario) & (datos["IDGROUP"]==group_id),"Umbral"] = float(datos.loc[(datos["Nombre"]==usuario) & (datos["IDGROUP"]==group_id), "Umbral"]) -1
            datos.to_csv("C:\\Users\\Tobias\\ProyectoRasaV2\\DB\\Perfiles.csv", index=False)
        else:   
            if (conductas[0] > 0.05) or (conductas[1] > 0.10) or (conductas[2] > 0.10):
                ActionDataRead.SumarMatrizGrupo(str(usuario),str(group_id),1) #C1, C2, C3 Relax, Sol, Apr
            if (conductas[7] > 0.25 ):
                ActionDataRead.SumarMatrizGrupo(str(usuario),str(group_id),-1)
                ActionDataRead.documentar(usuario,str(group_id),"Sugerencia")
                ActionDataRead.I_sugerencia(usuario,id,group_id)
                PV = True
            if (conductas[8] > 0.20):
                ActionDataRead.SumarMatrizGrupo(usuario,group_id,-1)
                ActionDataRead.documentar(usuario,str(group_id),"Desacuerdo")
                ActionDataRead.I_desacuerdo(usuario,id,group_id,PV)
                PV = True
            if (conductas[6] > 0.15):
                ActionDataRead.SumarMatrizGrupo(usuario,group_id,-1)
                ActionDataRead.documentar(usuario,str(group_id),"pide opinion")
                ActionDataRead.I_pideOpinion(usuario,id,group_id,PV)
                PV = True
            if (conductas[5] > 0.25):
                ActionDataRead.SumarMatrizGrupo(usuario,group_id,-1)
                ActionDataRead.documentar(usuario,str(group_id),"pide informacion")
                ActionDataRead.I_pideInformacion(usuario,id,group_id,PV)
                PV = True
            if (conductas[3] < 0.10):
                ActionDataRead.SumarMatrizGrupo(usuario,group_id,-1)
                ActionDataRead.documentar(usuario,str(group_id),"da poca opinion")
                ActionDataRead.I_daPocaOpinion(usuario,id,group_id,PV)
                PV = True
            elif (conductas[3] > 0.25):
                ActionDataRead.SumarMatrizGrupo(usuario,group_id,-1)
                ActionDataRead.documentar(usuario,str(group_id),"da mucha opinion")
                ActionDataRead.I_daMuchaOpinion(usuario,id,group_id,PV)
                PV = True
            if (conductas[4] < 0.10):
                ActionDataRead.SumarMatrizGrupo(usuario,group_id,-1)
                ActionDataRead.documentar(usuario,str(group_id),"da poca informacion")
                ActionDataRead.I_daPocaInformacion(usuario,id,group_id,PV)
                PV = True
            elif (conductas[4] > 0.25):
                ActionDataRead.SumarMatrizGrupo(usuario,group_id,-1)
                ActionDataRead.documentar(usuario,str(group_id),"da mucha informacion")
                ActionDataRead.I_daMuchaInformacion(usuario,id,group_id,PV)                          
            datos.loc[(datos["Nombre"]==usuario) & (datos["IDGROUP"]==group_id),"Umbral"] = 20       
            datos.to_csv("C:\\Users\\Tobias\\ProyectoRasaV2\\DB\\Perfiles.csv", index=False)


class ActionMetaData(Action):
    def DB(intencion,usuario,group_id):
        datos = pd.read_csv("C:\\Users\\Tobias\\ProyectoRasaV2\\DB\\Perfiles.csv",header= 0)  

        if not(((datos["Nombre"]==usuario) & (datos["IDGROUP"]== group_id)).any()) :
            datos.loc[len(datos)]=[usuario,0,0,0,0,0,0,0,0,0,0,group_id,20]
        #print (datos.loc[(datos["Nombre"]==usuario) & (datos["IDGROUP"]==group_id),intencion])
        datos.loc[(datos["Nombre"]==usuario) & (datos["IDGROUP"]==group_id),intencion] = float(datos.loc[(datos["Nombre"]==usuario) & (datos["IDGROUP"]==group_id), intencion]) +1
        datos.loc[(datos["Nombre"]==usuario) & (datos["IDGROUP"]==group_id), "Total"] = float(datos.loc[(datos["Nombre"]==usuario) & (datos["IDGROUP"]==group_id), "Total"]) +1
        datos.to_csv("C:\\Users\\Tobias\\ProyectoRasaV2\\DB\\Perfiles.csv", index=False)
        #print(datos)    

    def name(self) -> Text:
        return "action_MetaData"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        intencion = tracker.get_intent_of_latest_message()
        input_data=tracker.latest_message
        #print(input_data["metadata"]["message"]["from"])
        user_info=input_data["metadata"]["message"]["from"]
        user_name=input_data["metadata"]["message"]["from"]["first_name"]
        group_id=input_data["metadata"]["message"]["chat"]["title"] 
        ActionMetaData.DB(str(intencion),str(user_name),str(group_id))    
         
        return  []    
