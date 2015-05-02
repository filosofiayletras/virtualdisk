#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import *
import os
import httplib2
import json
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow, Credentials

app = Flask(__name__)

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
#                                WEB                                   #
########################################################################

# Para configurar drive (autorizar).
@app.route("/driveconfig")
def driveConfig():
	url_autorizacion = oadrive.step1_get_authorize_url()
	return render_template('auth_drive.html', url=url_autorizacion)

@app.route("/upload")
def uploadFile():
	return render_template('upload.html')

	
@app.route('/drivelist')
def driveList():
	return render_template('drivelist.html')




########################################################################
##                               API                                   #
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
@app.route("/driveauthcode", methods=['POST'])
def driveAuth():
	credentials = oadrive.step2_exchange(request.form['authcode'])
	
	driveauthfile = open('drivecredentials.txt', 'w')
	driveauthfile.write(credentials.to_json())
	driveauthfile.close()
	
	return '', 200

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
#     - filename -> Nombre que se le quiere dar al fichero al subirlo
#     - file     -> Ruta al fichero
#  - Devuelve: 200 OK
##
@app.route('/upload_to_drive', methods=['POST'])
def savePostFile():
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
		'title': request.form['filename'],
		'mimeType': file.content_type
	}

	#Realizamos la subida
	drive_service.files().insert(body=body, media_body=media_body, convert=False).execute()
	
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
	

if __name__ == "__main__":
	app.run(debug=True)
