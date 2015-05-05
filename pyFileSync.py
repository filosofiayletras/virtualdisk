#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Flask libraries
from flask import *

#Google Drive
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow, Credentials

#Dropbox
from dropbox import client, rest, session

#Utilities
import os
import httplib2
import json

app = Flask(__name__)

########################################################################
#                            DRIVE CONFIG                              #
########################################################################
#Claves de autorización de la API
DRIVE_CLIENT_ID     = '210795029530-u3sseqbnj7meedot38fbmbkoee3gof5t.apps.googleusercontent.com'
DRIVE_CLIENT_SECRET = 'jI93TZc4-WrCJLQGb5sHG2p_'
#Pedir autorización de acceso a Google Drive
DRIVE_OAUTH_SCOPE   = 'https://www.googleapis.com/auth/drive'
#URL de redirección. Se pone 'urn:ietf:wg:oauth:2.0:oob' para aplicaciones instaladas (como es el caso)
DRIVE_REDIRECT_URI  = 'urn:ietf:wg:oauth:2.0:oob'

#OAuth2 para drive. Global
oadrive = OAuth2WebServerFlow(DRIVE_CLIENT_ID, DRIVE_CLIENT_SECRET, DRIVE_OAUTH_SCOPE, redirect_uri=DRIVE_REDIRECT_URI)
#Credenciales y servicio de drive. Globales.
drivecredentials = None
drive_service    = None


########################################################################
#                           DROPBOX CONFIG                             #
########################################################################

#Dropbox API keys
DROPBOX_APP_KEY = 'qvkwb9hpaggsnac'
DROPBOX_APP_SECRET = 'jlv4jmek1t6j0j1'
DROPBOX_ACCESS_TYPE = 'app_folder'

#Sesión Dropbox. Globales.
dropbox_sess = session.DropboxSession(DROPBOX_APP_KEY, DROPBOX_APP_SECRET, DROPBOX_ACCESS_TYPE)
dropbox_request_token = dropbox_sess.obtain_request_token()
dropbox_client = None


########################################################################
#                           WEB GLOBAL                                 #
########################################################################
@app.route("/")
def home():
	return render_template('upload.html')
	
@app.route('/list')
def Total_List():
	return render_template('list.html')
	
	
########################################################################
#                            WEB DRIVE                                 #
########################################################################

# Para configurar drive (autorizar).
@app.route("/driveconfig")
def driveConfig():
	url_autorizacion = oadrive.step1_get_authorize_url()
	return render_template('auth_drive.html', url=url_autorizacion)

@app.route("/driveupload")
def uploadDriveFile():
	return render_template('driveupload.html')

	
@app.route('/drivelist')
def driveList():
	return render_template('drivelist.html')
	

########################################################################
#                           WEB DROPBOX                                #
########################################################################

# Para configurar Dropbox (autorizar).
@app.route("/dropboxconfig")
def DropboxAutentication():
	global dropbox_request_token
	dropbox_request_token = dropbox_sess.obtain_request_token()
	url_autentication = dropbox_sess.build_authorize_url(dropbox_request_token)
	return render_template('auth_dropbox.html', url=url_autentication)

@app.route("/dropboxupload")
def uploadDropboxFile():
	return render_template('dropboxupload.html')
	
@app.route('/dropboxlist')
def dropboxList():
	return render_template('dropboxlist.html')


########################################################################
##                           GLOBAL API                                #
########################################################################
@app.route("/automatic_upload", methods=['POST'])
def automaticUpload():
	drive_quota = json.loads(getDriveQuota())	
	dropbox_quota = json.loads(getDropboxQuota())
	
	drive_libre = drive_quota['total'] - drive_quota['used']
	dropbox_libre = dropbox_quota['total'] - dropbox_quota['used']
	
	if (drive_libre > dropbox_libre):
		func = uploadToDrive
	else:
		func = uploadToDropbox
	
	return func()
	

## Obtener lista de ficheros de ambos servicios.
#  - GET
#  - Devuelve: JSON = [{
#                         'id': path,
#                         'filename': path (without /)
#                         'link': path.url,
#                         'size': size (bytes)
#                      }];
##
@app.route("/get_list")
def getlist():
	dropbox_list=json.loads(getDropboxList())
	drive_list=json.loads(getDriveList())
	return json.dumps(dropbox_list + drive_list), 200
	




########################################################################
##                            DRIVE API                                #
########################################################################

## Obtener URL para autorizar.
#  - GET
#  - Devuelve: JSON = { 'url': url_autorizacion };
##
@app.route("/get_drive_auth", methods=['GET'])
def getDriveAuth():
	url_autorizacion = oadrive.step1_get_authorize_url()
	return json.dumps('{\'url\': \'' + url_autorizacion + '\'}')

## Recibir código de autorización.
#  - POST
#     - authcode -> Código de autorización
#  - Devuelve: 200 OK
##
@app.route("/save_drive_auth", methods=['POST'])
def driveAuth():
	credentials = oadrive.step2_exchange(request.form['authcode'])
	
	driveauthfile = open('drivecredentials.txt', 'w')
	driveauthfile.write(credentials.to_json())
	driveauthfile.close()
	
	return '{\'status\': \'ok\'}', 200

## Obtener cuotas de Drive.
#  - GET
#  - Devuelve {'used': long, 'total': long}
##
@app.route("/get_drive_quota", methods=['GET'])
def getDriveQuota():
	global drivecredentials
	global drive_service
	
	if (drive_service is None):
		if (drivecredentials is None):
			driveauthfile = open('drivecredentials.txt', 'r')
			drivecredentials = Credentials.new_from_json(driveauthfile.read())
			driveauthfile.close()

		http = httplib2.Http()
		http = drivecredentials.authorize(http)
		drive_service = build('drive', 'v2', http=http)
	
	about = drive_service.about().get().execute()
	
	return json.dumps({'used': long(about['quotaBytesUsed']), 'total': long(about['quotaBytesTotal'])})

## Subir fichero a Drive.
#  - POST
#     - file -> Flujo de bytes del fichero
#  - Devuelve: 200 OK
##
@app.route('/upload_to_drive', methods=['POST'])
def uploadToDrive():
	global drivecredentials
	global drive_service
	
	#Obtenemos el nombre del fichero, que pondremos temporalmente en
	#nuestra carpeta uploads/.
	file = request.files['file']
	file.save(os.path.join('uploads/', file.filename))
	
	#Nos autenticamos, si no lo hemos hecho ya
	if (drive_service is None):
		if (drivecredentials is None):
			driveauthfile = open('drivecredentials.txt', 'r')
			drivecredentials = Credentials.new_from_json(driveauthfile.read())
			driveauthfile.close()

		http = httplib2.Http()
		http = drivecredentials.authorize(http)
		drive_service = build('drive', 'v2', http=http)

	#Creamos el cuerpo del mensaje. Le pasamos la ruta al fichero.
	print file.content_type
	media_body = MediaFileUpload('uploads/' + file.filename, mimetype=file.content_type, resumable=True)
	
	#Propiedades del fichero a subir.
	body = {
		'title': file.filename,
		'mimeType': file.content_type
	}

	#Realizamos la subida
	drive_service.files().insert(body=body, media_body=media_body, convert=False).execute()
	
	#Borramos el temporal
	os.remove(os.path.join('uploads/', file.filename))
	
	return '', 200


## Obtener lista de ficheros de Drive.
#  - GET
#  - Devuelve: JSON = [{
#                         'id': file.id,
#                         'filename': file.title,
#                         'link': file.alternateLink,
#                         'size': file.size (bytes)
#                      }];
##
@app.route("/get_drive_list", methods=["GET"])
def getDriveList():
	global drivecredentials
	global drive_service
	
	if (drive_service is None):
		if (drivecredentials is None):
			driveauthfile = open('drivecredentials.txt', 'r')
			drivecredentials = Credentials.new_from_json(driveauthfile.read())
			driveauthfile.close()

		http = httplib2.Http()
		http = drivecredentials.authorize(http)
		drive_service = build('drive', 'v2', http=http)
	
	#Variable donde almacenaremos todos los ficheros listados
	resultados = []
	page_token = None
	siguiente_pagina = True
	while siguiente_pagina:
		parametros = {}
		
		#Comprobar si hay otra pagina
		if page_token:
			parametros['pageToken'] = page_token
		
		#Ejecutamos la consulta
		files = drive_service.files().list(**parametros).execute()
	
		#Concatenamos los resultados con los de la página anterior
		resultados.extend(files['items'])
		
		#Guardamos el token de la página siguiente
		page_token = files.get('nextPageToken')
		
		#Comprobamos si hay que continuar
		if not page_token:
			siguiente_pagina = False

	
	#Procesamos los resultados, almacenando la información relevante
	respuesta = []
	for elemento in resultados:
		respuesta.extend([{
			'id': elemento['id'],
			'filename': elemento['title'],
			'link': elemento['alternateLink'],
			'size': elemento['fileSize']
		}])
      
	return json.dumps(respuesta)	


########################################################################
##                            DROPBOX API                              #
########################################################################

## Obtener URL para autorizar.
#  - GET
#  - Devuelve: JSON = { 'url': url_autorizacion };
##
@app.route("/get_dropbox_auth", methods=['GET'])
def getDropboxAuth():
	global dropbox_sess
	global dropbox_request_token
	
	dropbox_request_token = dropbox_sess.obtain_request_token()
	url_autorizacion = dropbox_sess.build_authorize_url(request_token)
	return json.dumps('{\'url\': \'' + url_autorizacion + '\'}')

## Recibir código de autorización.
#  - POST
#     - authcode -> Código de autorización
#  - Devuelve: 200 OK
##
@app.route("/save_dropbox_auth")
def dropboxAuth():
	global dropbox_sess
	global dropbox_client
	global dropbox_request_token
	access_token = dropbox_sess.obtain_access_token(dropbox_request_token)
	
	dropboxauthfile = open('dropboxcredentials.txt', 'w')
	dropboxauthfile.write("%s;%s" % (access_token.key, access_token.secret))
	dropboxauthfile.close()
	
	dropbox_sess.set_token(access_token.key, access_token.secret)
	dropbox_client = client.DropboxClient(dropbox_sess)
	
	return '{\'status\': \'ok\'}', 200

## Subir fichero a Dropbox.
#  - POST
#     - file -> Flujo de bytes del fichero
#  - Devuelve: 200 OK
##
@app.route('/upload_to_dropbox', methods=['POST'])
def uploadToDropbox():
	global dropbox_sess
	global dropbox_client
	
	if (dropbox_client is None):
		dropboxauthfile = open('dropboxcredentials.txt', 'r')
		token_key, token_secret = dropboxauthfile.read().split(';')
		dropboxauthfile.close()
		
		dropbox_sess.set_token(token_key, token_secret)
		dropbox_client = client.DropboxClient(dropbox_sess)
	
	#Obtenemos el nombre del fichero, que pondremos temporalmente en
	#nuestra carpeta uploads/.
	file = request.files['file']
	
	#Subir fichero
	response = dropbox_client.put_file('/' + file.filename, file)
	
	return '', 200
	

## Obtener lista de ficheros de Dropbox.
#  - GET
#  - Devuelve: JSON = [{
#                         'id': path,
#                         'filename': path (without /)
#                         'link': path.url,
#                         'size': size (bytes)
#                      }];
##
@app.route("/get_dropbox_list",methods=['GET'])
def getDropboxList():
	global dropbox_sess
	global dropbox_client
	
	if (dropbox_client is None):
		dropboxauthfile = open('dropboxcredentials.txt', 'r')
		token_key, token_secret = dropboxauthfile.read().split(';')
		dropboxauthfile.close()
		
		dropbox_sess.set_token(token_key, token_secret)
		dropbox_client = client.DropboxClient(dropbox_sess)

	folder_metadata = dropbox_client.metadata('/')
	respuesta = []

	for elemento in folder_metadata['contents']:
		if elemento['size'].find('bytes') != -1:
			elemento['size'] = elemento['size'].replace('bytes','')
			elemento['size'] = long(float(elemento['size']))
		elif elemento['size'].find('KB') !=-1:
			elemento['size'] = elemento['size'].replace('KB','')
			elemento['size'] = long(float(elemento['size'])*1024)
		elif elemento['size'].find('MB') !=-1:
			elemento['size'] = elemento['size'].replace('MB','')
			elemento['size'] = long(float(elemento['size'])*1048576)
		elif elemento['size'].find('GB') !=-1:
			elemento['size'] = elemento['size'].replace('MB','')
			elemento['size'] = long(float(elemento['size'])*1073741824)
		
		
		respuesta.extend([{
			'id': elemento['path'],
			'filename': elemento['path'].replace('/',''),
			'link': dropbox_client.share(elemento['path'])['url'],
			'size': elemento['size']
		}])
	
	return json.dumps(respuesta)

## Obtener cuotas de Dropbox.
#  - GET
#  - Devuelve {'used': long, 'total': long}
##
@app.route("/get_dropbox_quota")
def getDropboxQuota():
	global dropbox_sess
	global dropbox_client
	
	if (dropbox_client is None):
		dropboxauthfile = open('dropboxcredentials.txt', 'r')
		token_key, token_secret = dropboxauthfile.read().split(';')
		dropboxauthfile.close()
		
		dropbox_sess.set_token(token_key, token_secret)
		dropbox_client = client.DropboxClient(dropbox_sess)
		
	return json.dumps({'used': dropbox_client.account_info()['quota_info']['normal'], 'total' : dropbox_client.account_info()['quota_info']['quota']}) 


if __name__ == "__main__":
	app.run(debug=True)
