
# encoding: utf-8
# TRABAJO IA 2014
# Autores: Alejandro Arciniega Fernández y Alfonso Yáñez Herrera

import xml.etree.ElementTree as ET
from io import StringIO, BytesIO
from xml.dom import minidom
import math
import types

""" Selección de modo de ejecución """

#Inicio para indicar si se quiere usar el modo traza o el normal
Traza = False
mode = int(input("Seleccione modo de ejecución: 1) Traza  2) Normal \n "))
if mode == 1:
    Traza = True

""" Clases definidas por el usario """

class Variable():
    
    # Clase para definir las variables aleatorias del dominio
    def __init__(self, name, states):
    # name es el nombre de la variable
    # states son los valores que puede tomar la variable, en nuestro caso T(True) y F(False)
        self.name = name
        self.states = list()
    
    def __str__(self):
        return str(self.name)

	
class Nodo():
    #Clase para identificar a las variables
    def __init__(self,var):
        self.var = var
   
    def hijos(self,aristas):
    # Método para obtener todos los hijos de una variable, a partir de sus aristas
      res = []
      for elem in aristas:
            if elem.antecesor == self.var.name:
                res.append(elem.child)  
      return res

    def __str__(self):
        return self.var.name
    

class Arista():
    # Clase para conectar los nodos, mediante el antecesor(Padre) y child(Hijo)
    def __init__(self, antecesor, child):
        self.antecesor = antecesor
        self.child = child

class Table():
    #Con la clase tabla presentamos las probabilidades de cada nodo
    def __init__(self, variable, varEvidencia, prob):   
        # variable es la variable a la que pertenece la tabla, por ejemplo, tabla(E), E seria la variable
        # varEvidencia se usa para indicar las dependencias de la tabla
        self.variable = variable
        self.probabilities = list()
        for elem in prob:
            self.probabilities.append(float(elem))
        self.varEvidencia = varEvidencia
       
class Red():
    # Nuestra red formada por nodos y aristas
    def __init__(self,nodos,aristas):
        self.nodos = nodos
        self.aristas = aristas

""""""""""""""""""""""""""""""

""" Carga de archivo XMLBIF """

def creaRedDesdeArchivo(xml):
    print('Cargando archivo: '+ str(xml))
    nodos = []
    aristas = []
    # Usaremos el módulo xml.etree.ElementTree de Python para parsear el archivo xml
    tree = ET.ElementTree(file=xml)
    root = tree.getroot()
    variables = []
    tables = []
    count = 0
	
    for elem in root:
        for hijos in elem:
            
            if 'VARIABLE' in hijos.tag:
                # Miramos si aparece variable en las tags
                name = ''
                outcomes = []
                for other in hijos:
                    # Miramos las etiquetas de cada variable para obtener sus valores
                    if 'NAME' in other.tag:
                        name = other.text
                        # Guardamos el nombre
                    if 'OUTCOME' in other.tag:
                        outcomes.append(other.text)
                        # Guardamos las salidas de la variable
                variables.append(Variable(name,outcomes))

            if 'DEFINITION' in hijos.tag:
                variable = ''
                varEvidencia = []
                probs = []
                for other in hijos:
                    # Buscamos en los valores de las tablas
                    if 'FOR' in other.tag:
                        # Valor de variable
                        variable = other.text
                    if 'GIVEN' in other.tag:
                        # Valor/es de varEvidencia
                        varEvidencia.append(other.text)
                    if 'TABLE' in other.tag:
                        # Probabilidades de la tabla
                        probs.append(other.text)

                tables.append(Table(variable, varEvidencia, probs[0].split(' ')))
                # Añadimos la tabla nueva, incluyendo un separador para cada probabilidad

    for var in variables:
        # Creamos los nodos a partir de las variables obtenidas
        nodos.append(Nodo(var))
    for table in tables:
        # Para las aristas nos basamos en los GIVEN del xml
        for given in table.varEvidencia:
            aristas.append(Arista(given, table.variable))


    print('Final de la lectura del archivo XMLBIF')

    return nodos,aristas,tables

def getRedyTablas(xml):
    nodos,aristas,tables = creaRedDesdeArchivo(xml)
    red = Red(nodos,aristas)
    return red, tables
""""""""""""""""""""""""""

# Métodos Auxiliares

def consulta(elem,x):
    # Comprueba si la variable es de consulta, comparándola con la pasada por comandos
    aux=False 
    if elem.var.name == x:
        aux=True
    return aux

def evidencia(elem,e):
    # Comprueba si la variable es de evidencia, comparándola con la/s pasadas por comandos
    aux=False
    if elem.var.name in e:
        aux=True
    return aux

def espadreDe(elem,variable,aristas,e):
    # Comprobar si el elemento es padre de la variable perteneciente a la red
    padres=elem.hijos(aristas)
    res=False
    for elem in padres:
        if Traza:
            print("Su hijo es: ",elem)
        if variable in padres:
            res=True
    for elem in e:
        # Comprobamos si dentro de los hijos, alguna variable pertenece a las de evidencia
        if elem in padres:
            res=True
    return res

def compruebaEvi(eviAux):
    # Comprobamos si la variable de evidencia es verdadera o falsa,
    # si la variable es verdadera, devolvera true, en otro caso devolvera falso
    res=False
    for elem in eviAux:
        if "-" in elem:
            res=True
            if Traza:
                print("Es negativa!")
            break
    return res


def multiplicaFactor(factor1,factor2):
    # Obtención de las probabilidades de ambos factores
    ext=factor1.probabilities
    aux=factor2.probabilities
    if Traza:
        print("Ext",len(ext),ext)
        print("Aux",len(aux),aux)
    # Obtención de sus puntos medios
    l2 = int(len(aux)/2)
    l1 = int(len(ext)/2)
    res = []
    # Si la longitud de ambos es la misma se multiplican tal cual
    if len(ext)== len(aux):
        if Traza:
            print("Caso longitud igual")
        for n in range(len(ext)):
            if Traza:
                print("Valor de n",n)
            res.append(ext[n] * aux[n])
            if Traza:
                print("Añadido:",ext[n] * aux[n])
    # Si el primero es menor que el segundo, tenemos como posibilidades:
    # O que el pequeño tenga 4 o 2 elementos, y el grande 4 o 8
    elif len(ext)< len(aux):
        if Traza:
            print("Caso ext menor que aux")
        # Si el primero tiene 2 y el segundo tiene 8, dividimos el grande en 4
        # partes, tomando los valores de 2 en 2(positivo negativo)
        if len(ext) == 2 and len(aux)==8:
            l3=int(l2/2)
            given21=aux[0:(l3)] #De (0,1)
            given22=aux[l3:(l2)] #De (2,3)
            given23=aux[l2:l2+2] #De (4,5)
            given24=aux[(l2+2)::] #De (6,7)
            if Traza:
                print("given21",given21)
                print("given22",given22)
                print("given23",given23)
                print("given24",given24)
            for n in range(len(ext)):
            # Una vez tomados, multiplicamos los primeros con los primeros y los
            # segundos con los segundos y añadimos el resultado a una lista
                if Traza:
                    print("Valor de n",n)
                res.append(ext[n] * given21[n])
                res.append(ext[n] * given22[n])
                res.append(ext[n] * given23[n])
                res.append(ext[n] * given24[n])
                if Traza:
                    print("Añadido 1: ",ext[n] * given21[n])
                    print("Añadido 2: ",ext[n] * given22[n])
                    print("Añadido 3: ",ext[n] * given23[n])
                    print("Añadido 4: ",ext[n] * given24[n])
        else:
        # En otro caso, al hacer una sola división en dos, basta para poder realizar
        # la multiplicación entre los factores de la misma forma que en el caso anterior
            given21 = aux[0:l2]
            given22 = aux[l2::]
            if Traza:
                print("factor21",given21)
                print("factor22",given22)
            for n in range(len(ext)):
                if Traza:
                    print("Valor de n",n)
                res.append(ext[n] * given21[n])
                res.append(ext[n] * given22[n])
                if Traza:
                    print("Añadido 1: ",ext[n] * given21[n])
                    print("Añadido 2: ",ext[n] * given22[n])
    elif len(ext)> len(aux):
    # Si ahora el primero es mayor que el segundo, pasa lo mismo que en el anterior
    # pero aplicando la división segun el tamaño al otro factor
        if Traza:
            print("Caso ext mayor que aux")
        if len(aux)==2 and len(ext)==8:
            l3=int(l1/2)
            given21=ext[0:(l3)]
            given22=ext[l3:(l1)]
            given23=ext[l1:l1+2]
            given24=ext[(l1+2)::]
            if Traza:
                print("given21",given21)
                print("given22",given22)
                print("given23",given23)
                print("given24",given24)
            for n in range(len(aux)):
                if Traza:
                    print("Valor de n",n)
                res.append(aux[n] * given21[n])
                res.append(aux[n] * given22[n])
                res.append(aux[n] * given23[n])
                res.append(aux[n] * given24[n])
                if Traza:
                    print("Añadido 1: ",aux[n] * given21[n])
                    print("Añadido 2: ",aux[n] * given22[n])
                    print("Añadido 3: ",aux[n] * given23[n])
                    print("Añadido 4: ",aux[n] * given24[n])  
        else:
        #En otro caso, con una división sirve como en el caso anterior
            given11 = ext[0:l1]
            given12 = ext[l1::]
            if Traza:
                print("factor21",given11)
                print("factor22",given12)
            for n in range(len(aux)):
                if Traza:
                    print("Valor de n",n)
                res.append(aux[n] * given11[n])
                res.append(aux[n] * given12[n])
                if Traza:
                    print("Añadido 1: ",aux[n] * given11[n])
                    print("Añadido 2: ",aux[n] * given12[n])
    if Traza:
        print("res",res)
    return res

def padres(elem,aristas):
    # Método para obtener los padres de una variable, a partir de todas las relaciones(aristas) 
    aux=[]
    for res in aristas:
        if res.child==elem:
            aux.append(res.antecesor)
    return aux

def agrupar(factor1,factor2):
    # Método para agrupar un factor con el factor de VAR
    elem=[]
    aux=factor2.probabilities
    if len(factor1) == len(aux):
        for n in range(len(factor1)):
            elem.append(factor1[n] + aux[n])
    elif len(factor1)>len(aux):
        if Traza:
            print("Reduciendo")
        reducido=reducir(factor1)
        reducido1=reducido
        if len(reducido)>len(aux):
            reducido1=reducir(reducido)
        for n in range(len(reducido1)):
            elem.append(reducido1[n]+aux[n])
    if Traza:
        print("Resultado agrupado: ",elem)
    return elem

def eliminairrelevantes(X,e,red,tables):
    eliminadas= []
    listapadres= []
    if Traza:
        print("Tamaño de la red antes de eliminar las variables irrelevantes: ",len(red.nodos))
    for elem in red.nodos:
        # Comprobamos si es de consulta
        aux = consulta(elem,X)
        # Comprobamos si es de evidencia
        aux1 = evidencia(elem,e)
        # Comprobamos si es padre de la variable de consulta o alguna de las de evidencia
        aux2 = espadreDe(elem,X,red.aristas,e)
        if aux2==False:
            if aux==False and aux1==False:
                # Si no es padre de ninguna y ni de consulta ni evidencia, la eliminamos
                if Traza:
                    print("Eliminando variable..",elem)
                eliminadas.append(elem)
                red.nodos.remove(elem)
        elif aux2==True:
            # Si es padre, no se elimina
            if Traza:
                print("Es padre de una variable de consulta o de evidencia")          
        else:
            if Traza:
                print("No se elimina la variable")
        if elem in red.nodos:
            # Obtenemos los padres de las variables que quedan en la red
            padres1 = padres(elem.var.name, red.aristas)
            if Traza:
                print("Padres: ",padres1)
            for elem1 in padres1:
                if elem1 not in listapadres:
                    listapadres.append(elem1)
       
    for elem2 in eliminadas:# Si alguno de los padres se encuentra eliminado, se vuelve a añadir a la red
      
        if elem2.var.name in listapadres:
            if Traza:
                print("Añadida variable ",elem2," de nuevo")
            eliminadas.remove(elem2)
            red.nodos.append(elem2)
    if Traza:
        print("Tamaño de la red tras la elimiación de las variables irrelevantes: ",len(red.nodos))
    return eliminadas

    
def obtenerFactores(tables,consulta,evidencias):
    factors = []
    # Iteración sobre tablas
    for table in tables:
        if Traza:
            print('Obteniendo Factor de ' + table.variable + ' dado ' + str(table.varEvidencia))
        # Probabilidades de la tabla en la que estamos
        subs = table.probabilities[0::]
        # Si la tabla es de una de las variables que tenemos como evidencia
        if table.variable in evidencias: 
            ind = evidencias.index(table.variable)
            # Obtenemos el índice
            # Luego, calculamos 2^ind, que nos servira para el desplazamiento entre posiciones
            l = int(math.pow(2, ind))
            # Comprobamos si hay alguna variable negativa dentro de las evidencias
            if compruebaEvi(evidencias):
                # Si la hay, obtenemos únicamente sus valores negativos, ya que es una variable de evidencia
                subs = subs[l-1::l]
                # Avanzamos de l en l elementos, es decir, de 2 en 2, empezando desde el segundo elemento
                # De esta forma cogemos los valores negativos únicamente
                if Traza:
                    print(' Cogiendo valores negativos de ' + table.variable + ' dado ' + str(table.varEvidencia))
                    print(subs)
            else:
                # En caso contrario, cogemos sólo los positivos. Para ello avanzmos de l en l nuevamente(2 en 2),
                # pero empezamos en el primer elemento de la lista en lugar de en el segundo
                subs = subs[0::l]
                if Traza:
                    print('Cogiendo valores positivos de' + table.variable + ' dado ' + str(table.varEvidencia))
                    print(subs)
        # Ahora miramos las evidencias de cada tabla
        for evi in table.varEvidencia:
            # Volvemos a calcular 2^ind, pero esta vez se le suma 1, para un correcto desplazamiento
            index = table.varEvidencia.index(evi)
            n = int(math.pow(2, index+1))
            # Si evi es una evidencia, y ademas existe alguna evidencia negativa
            if evi in evidencias and  compruebaEvi(evidencias):
                if Traza:
                    #Cogemos sus valores negativos de la misma forma que el caso anterior
                    print(' Cogiendo valores negativos de' + table.variable + ' dado ' + evi)
                subs = subs[n-1::n] 
                if Traza:
                    print(' n en get factors vale: ', n)
                    print(subs)
            # Caso de que está en evidencias, pero es positiva
            elif evi in evidencias:
                subs = subs[0::n] 
                # Sólo cogemos los valores positivos de la misma manera que el apartado anterior
                if Traza:
                    print(' Cogiendo valores positivos de' + table.variable + ' dado ' + evi)
                    print(subs)
        factors.append(Table(table.variable, table.varEvidencia, subs))
        # Añadimos la nueva tabla(Factor) a la lista    
    return factors


def buscarFactores(var,factores):
# Búsqueda de factores en los que aparece la variable para eliminar
    lista=[]
    numero=len(factores)
    lista1=factores[0:numero]
    if Traza:
        print("Variable con la que buscamos: ",var.var.name)
    for elem in lista1:
        if var.var.name in elem.varEvidencia:
            # Si aparece como evidencia se añade
            lista.append(elem)
            if Traza:
                print(var.var.name,"Aparece como evidencia")
        elif var.var.name == elem.variable:
            # Si aparece como consulta se añade
            lista.append(elem)
            if Traza:
                print(var.var.name,"Aparece como consulta")
    return lista


def sacarFactores(factores,aparece):
    # Método que elimina los factores de la lista de factores
    feliminado=[]
    if Traza:
        print("Aparece: ",aparece)
        print("Factores antes: ",len(factores))
    for elem in factores:
        for elem1 in aparece:
        # Iteramos en ambas listas y eliminamos de factores los elementos de aparece
        # de esta forma eliminamos todos los factores en los que aparece la variable con la que iteramos
            if elem == elem1:
                factores.remove(elem)
                feliminado.append(elem)
    if Traza:
        print("Eliminados: ",len(feliminado))
        print("Factores después: ",len(factores))
    return feliminado


def eliminaTablasIrrelevantes(tablas,eliminadas,e):
    # Método para eliminar las tablas de las variables eliminadas de la red
    factoreseliminados=[]
  
    for elem in eliminadas:
        
        for elem1 in tablas:
           
            # Si la variable eliminada es variable o varEvidencia de una tabla
            # esta se elimina y se añade a una lista de tablas eliminadas
            if elem.var.name == elem1.variable:
           
                factoreseliminados.append(elem1)
         
                tablas.remove(elem1)
    if Traza:
        print("Factores eliminados: ")
    for elem in factoreseliminados:
        if Traza:
            print("Factor: ",elem.variable)
    if Traza:
        print(len(tablas),"restantes")
    return factoreseliminados


def reducir(res):
    # En caso de que un factor tenga mas de 2 elementos, se suman entre ellos
    # para reducirlos a 2 elementos
    aux=[]
    mitad=int(res.__len__()/2)
    mitad1=res[0:mitad]
    mitad2=res[mitad::]
    for elem in range(mitad):
        aux.append(mitad1[elem] + mitad2[elem])
    return aux

def normalizar(factores):
   # Normaliza el factor obtenido
    if Traza:
        print("Factores: ",factores)
    # Si hay mas de 2 factores, se multiplican dentro de un for
    if len(factores)>2:
        for i in range(len(factores)):
         
            if i > len(factores):
                break
            else:
                final=multiplicaFactor(factores[0],factores[i])
    # Si hay 2 factores, se multiplican entre ellos
    elif len(factores)>1:
        final=multiplicaFactor(factores[0],factores[1])
    else:
    # Si es solo uno, se obtienen sus probabilidades
        final=factores.probabilities
    lista=[]
    if Traza:
        print("Tamaño factores: ",len(factores))
       
        print("Final: ",final)
    # Si el factor único restante tiene mas de 2 elementos, se reducen a la mitad
    if len(final)>2:
     
        final1=reducir(final)
       
        res=final1[0]
        aux=final1[1]
        # Si sigue teniendo más de 2, se vuelve a reducir
        if len(final1)>2:
            final2=reducir(final1)
          
            res=final2[0]
            aux=final2[1]
    else:
    # En otro caso, obtenemos los dos elementos y normalizamos
        res=final[0]
        aux=final[1]
   
    if Traza:
        print("Res",res)
        print("Aux",aux)
    suma=res+aux
    lista.append(res/suma)
    lista.append(aux/suma)
    return lista

def obtenerVar(feliminado):
    # Método para obtener las variables involucradas en los factores que se van a eliminar
    # en la multiplicación. Las variables obtenidas formarán parte del nuevo factor
    res=[]
    # Miramos por un lado en las variables(Variable perteneciente de la tabla)
    # y por otro lado a las varEvidencia de cada una( Las variable de las que depende la tabla)
    res=[]
    for elem in feliminado:
        for elem1 in elem.varEvidencia:
            if elem.variable not in res:
                res.append(elem.variable)
            elif elem1 not in res:
                res.append(elem1)
  
    return res

def obtenFactor(var,tables):
    # Devuelve el factor de la variable que se le pasa en la cabecera, mirando en todos los factores existentes
    if Traza:
        print("Variable a comprobar: ",var)
        print(len(tables))
    for elem in tables:
        if Traza:
            print("consulta: ",elem.variable)
            print("evidencia/s: ",elem.varEvidencia)
            print("probabilidades: ",elem.probabilities)
        if elem.variable == var.var.name or var.var.name in elem.varEvidencia:
            return elem
            if Traza:
                print("LLega")
        else:
            if Traza: 
                print("No encuentra factor con: ",var.var.name)
    
###########################

""" Eliminación de Variables """

def ev(X,e,red,tables):
    # X: variable de consulta
    # e variable de evidencia
    normalizado=0
    # En primer lugar, eliminar las variables irrelevantes
    factores1=obtenerFactores(tables,X,e)
    eliminadas=eliminairrelevantes(X,e,red,tables)
    if Traza:
        print("Variables eliminadas,")
    for elem in eliminadas:
        if Traza:
            print(elem.var.name)
            print('Los nodos de la red despues de eliminar son: ')
    for elem in red.nodos:
        if Traza:
            print(elem.var.name)
    # Obtener factores
    if Traza:
        print("Obteniendo factores...")
    factoreseliminados=eliminaTablasIrrelevantes(tables,eliminadas,e)
    factores=obtenerFactores(tables,X,e)
    if Traza:
        print("Los factores originales son: ")
    for elem in factores:
        if Traza:
            print('Factor de: ' + elem.variable)
            print(elem.probabilities)
    aparece=[]
    feliminado=[]
    res=[]
    red1=red.nodos
    # Comprobamos cada variable
    for var in red1:
        if Traza:
            print(var.var.name,"¿Consulta o no?")
        if consulta(var,X)==True:
            # Si es de consulta
            if Traza:
                print("Consulta: ")
            # Obtenemos todos los factores donde aparece la variable var
            aparece=buscarFactores(var,factores)
            # Sacamos esos factores y los guardamos en una lista auxiliar
            feliminado=sacarFactores(factores,aparece)
            if Traza:
                print("Factores consulta: ",factores)
            for elem in factores1:
                if Traza:
                    print('Factor de: ',elem)
                    print(elem.probabilities)
            if Traza:
                print("Eliminados: ",feliminado)
                print("Multiplicacion: ")
            # Obtenemos las variables de los factores eliminados para montar el nuevo factor
            evi=obtenerVar(feliminado)
            # Si tenemos más de un factor, los multiplicamos entre ellos
            if len(feliminado)>1:
                for n in range(feliminado.__len__()):
                    res= multiplicaFactor(feliminado[0],feliminado[n])
                    if Traza:
                        print("Factor a añadir: ",res)
            # Añadimos nuevo factor a la lista de factores
                    factores.append(Table(var, evi, res))
            elif len(feliminado)==0:
            # Este es el caso de que no exista ningún factor donde aparezca Var
                if Traza:
                    print("No se ha eliminado ningun factor")
            else:
                # El otro caso, es que solo se obtenga un factor, entonces obtenemos el
                # factor donde Var es variable(No sea evidencias de la tabla)
                factormulti=obtenFactor(var,tables)
           
                res=multiplicaFactor(feliminado[0],factormulti)
                if Traza:
                    print("Factor a añadir: ",res)
                factores.append(Table(var, evi, res))
        else:
            # Caso de que no sea de consulta
            if Traza:
                print("No es de consulta")
            # Obtenemos todos los factores donde aparece la variable var
            aparece=buscarFactores(var,factores)
            # Sacamos esos factores y los guardamos en una lista auxiliar
            feliminado=sacarFactores(factores,aparece)
            # Obtenemos las variables dependientes para el nuevo factor
            evi=obtenerVar(feliminado)
            for elem in factores:
                if Traza:
                    print('Factor de: ', elem)
                    print(elem.probabilities)
             
            # Si hay más de un factor, multiplicación normal        
            if len(feliminado)>1:
                for n in range(feliminado.__len__()):
                    res= multiplicaFactor(feliminado[0],feliminado[n])
                # Agrupamos por var, para ello obtenemos su factor y multiplicamos
                factorpadre=obtenFactor(var,factores1)
                if Traza:
                    print("Factor padre: ",factorpadre.probabilities)
                factoragrupado=agrupar(res,factorpadre)
                if Traza:
                    print("Factor a añadir: ",factoragrupado)
                # Añadimos nuevo factor
                factores.append(Table(var, evi, factoragrupado))
            elif len(feliminado)==0:
                # Caso no encuentre factor
                if Traza:
                    print("No se ha eliminado ningún factor")
            else:
                # Solo hay un factor, por lo que obtenemos el factor de table
                factormulti=obtenFactor(var,tables)
                res=multiplicaFactor(feliminado[0],factormulti)
                if Traza:
                    print("Factor a añadir: ",res)
                factores.append(Table(var, evi, res))
        if Traza:
            print("Factores actuales: ",len(factores))
        for elem in factores:
            if Traza:
                print(elem)
                print(elem.probabilities)
    # Como paso final, normalizamos el/los factor/es restante/s despues de comprobar
    # todos los nodos de la red
    normalizado=normalizar(factores)	
    return normalizado

""""""""""""""""""""
def insertardatos():
    res=input('Escribe la variable de consulta: ')
    aux=input('Introduzca la/s variable/s de evidencia (use - para negar una variable): ')
    aux1=aux.split(' ')
    
    return res,aux1

def compruebaDatos(listanombres,consulta,evidencias):
    # Método para comprobar que las variables introducidas son correctas
    res=False
    listanegativa=[]
    for elem in listanombres:
        listanegativa.append("-"+elem)
    if consulta not in listanombres or elem in listanegativa:
        print("Error introduciendo la variable de consulta")
    else:
        res=True
    for elem in evidencias:
        if elem in listanombres or elem in listanegativa:
            res=True
        else:
            res=False
            print("Error introduciendo la/s variable/s de evidencia")
    return res

def ejecutar():
    # Carga del xml y creación de la red
    listanombres=[]
    red, tables = getRedyTablas('RedAsia.xml')
   
    print('Los nodos de la red son los siguientes:')
    for elem in red.nodos:
        print(elem.var.name)
        listanombres.append(elem.var.name)
    print('Las aristas de la red son las siguientes: ')
    for elem in red.aristas:
        print(elem.antecesor + ' -> ' + elem.child)

    for elem in tables:
        print('Tabla de probabilidad de: ' + elem.variable)
        print(elem.probabilities)

    consulta,evidencias= insertardatos()
    if compruebaDatos(listanombres,consulta,evidencias):
        if Traza:
            print('Datos: ',consulta,evidencias)
        resultado=ev(consulta,evidencias,red,tables)
        print("Resultado normalizado: ",resultado)
    else:
        print("Error introduciendo variables")

   
ejecutar()
