___autor___ = 'Jackson Goulart'

import requests
import time
import datetime
import pyodbc
import re
import configparser


conf = configparser.ConfigParser()
conf.read('sets.ini')
datasource = conf['datasource']['odbc']
msgsend = conf['msg']['padrao']
msgsabado =  conf['msg']['sabado']
# data = conf['data']['dia']
commandquery = conf['commandquery']['query']
usuario = conf['user']['usuario']
senha =conf['user']['senha']
# numero = conf['numero']['n']
msgenvio = ''


def timesClock():
    day = time.strftime('%d %m %Y')
    hours = time.strftime('%H %M %S')
    return day, hours


def tratamentoNumero(numero):

    if re.findall('/', numero):
        spt = numero.split('/')
        numero = spt[1]

    elif re.findall('([a-zA-Z]+)', numero):
        patter = re.findall('([a-zA-Z]+)', numero)
        spt = numero.split(patter[0])
        numero = spt[1]

    rx = re.sub('[ -]', '', numero)

    if len(rx) == 8:
        rx = rx[:0] + '669' + rx[0:]

    elif len(rx) == 9:
        rx = rx[:0] + '66' + rx[0:]

    elif len(rx) == 10:
        rx = rx[0:2] + '9' + rx[2:]
    else:
        rx
    return rx


day, hours = timesClock()


def readDb():
    try:
        conn = pyodbc.connect(datasource)
        cursor = conn.cursor()
        print('Conneted')

        cursor.execute(commandquery)
        listadados = []

        while True:
            row = cursor.fetchone()
            if not row:
                break
            listadados.append([format(row.data, '%d %m %Y'), tratamentoNumero(row.numero)])
            print(format(row.data, '%d %m %Y'), ' ', tratamentoNumero(row.numero))
        return listadados
    except pyodbc.InterfaceError:
        print('Verifique a conexão cursor não pode ser executado ...')


def envioconsulta(numero,msg):
    url = "https://ws.smsdigital.com.br/sms/envio"
    # print(numero)
    header = {
        'destinatarios': [numero],
        'mensagem': msg,
        'flash': 'True'
    }
    try:

        send = requests.post(url, auth=(usuario, senha), json=header)
        if send.status_code == 200:
            status = "\n" + send.reason + "\n" + send.text + "\n" + "day %s hours %s " % (day, hours)
            print(status)
            log = open('envios.log', 'a')
            log.write(status)
            log.close()
    except ConnectionError:
        send


def resposta(sequencia):
    # resposta
    url = "https://ws.smsdigital.com.br/sms/resposta"

    header = {
        'sequencias': sequencia
    }

    receved = requests.post(url, auth=(usuario, senha), json=header)

    print(receved.reason, "\n", receved.text)


def monitor():

    amanha = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%d %m %Y')
    msgenvio = msgsend

    if datetime.date.today().weekday() == 5:
       amanha = (datetime.date.today() + datetime.timedelta(days=2)).strftime('%d %m %Y')
       msgenvio = msgsabado

    # amanha = str(int(day[0:2]) + 1) + day[2:]

    # if len(amanha) == 9:
    #     amanha = amanha[:0]+'0'+amanha[0:]

    print("hoje ", day, " ", hours)
    print('Hoje + 1 = amanha ', amanha)

    for consulta in readDb():

        if consulta[0:][0] == amanha:
            # envioconsulta(consulta[0:][0])
            print('Data da consulta consulta ', consulta[0:][0])
            # print('Numero para envio ',  tratamentoNumero(consulta[0:][1]))
            print('Numero para envio ', consulta[0:][1])
            envioconsulta(consulta[0:][1],msgenvio)
        else:
            print('sem consultas marcadas', consulta[0:][0])
    return True



if __name__ == '__main__':

    while monitor != True:
        monitor()
        print('Envios ok ...')
        time.sleep(2)
        break


