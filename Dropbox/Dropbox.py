# Include the Dropbox SDK libraries
from dropbox import client, rest, session
from flask import Flask, request, render_template
import os
import json
import httplib2

app = Flask(__name__)
# Get your app key and secret from the Dropbox developer website
APP_KEY = 'qvkwb9hpaggsnac'
APP_SECRET = 'jlv4jmek1t6j0j1'
 
# ACCESS_TYPE should be 'dropbox' or 'app_folder' as configured for your app
ACCESS_TYPE = 'app_folder'
 
sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
request_token = sess.obtain_request_token()


# Para configurar Dropbox (autorizar).
@app.route("/dropboxconfig")
def DropboxAutentication():
	url_autentication = sess.build_authorize_url(request_token)
	return render_template('autentication.html',url=url_autentication)

@app.route("/upload")
def uploadFile():
	return render_template('upload.html')
	
@app.route('/dropboxlist')
def dropboxList():
	return render_template('dropboxlist.html')





########################################################################

@app.route("/get_dropbox_auth", methods=['GET'])
def getDropboxAuth():
	url_autorizacion = sess.build_authorize_url(request_token)
	return json.dumps('{\'url\': \'' + url_autorizacion + '\'}')
 
 
@app.route("/dropboxauthcode")
def dropboxAuth():
	access_token = sess.obtain_access_token(request_token)
	sess.set_token(access_token.key,access_token.secret )
	Client = client.DropboxClient(sess)
	return json.dumps('{\'token_key\':\'' + access_token.key + ',\token_secret\':\'' + access_token.secret +',\client\':\'{\client_name\':\'' + Client.account_info()['display_name'] + '\'}' '\'}')
@app.route("/get_client")
def getclient():
	Client = client.DropboxClient(sess)
	return json.dumps('{\client_name\':\'' + Client.account_info()['display_name'] + '\'}')
	

@app.route('/upload_to_dropbox', methods=['POST'])
def savePostFile():
		
	#Obtenemos el nombre del fichero, que pondremos temporalmente en
	#nuestra carpeta uploads/.
	file = request.files['file']
	file.save(os.path.join('uploads/', file.filename))
	# Let's upload a file
	
	f = open(file.save,'rb')
	response = client.put_file(file.save, f)
	

@app.route("/get_dropbox_list",methods=['GET'])
def getDropboxList():
	
	Client = client.DropboxClient(sess)
	folder_metadata = Client.metadata('/')
	respuesta = []
	
	#  - Devuelve: JSON = [{
#                         'id': file.id,
#                         'filename': file.title,
#                         'link': file.alternateLink,
#                         'size': file.size (bytes)
#                      }];
	for elemento in folder_metadata['contents']:
		respuesta.extend([{
			'id': elemento['path'],
			'filename': elemento['path'].replace('/',''),
			'link': Client.share(elemento['path'])['url'],
			'size':long(elemento['size'].replace('bytes',''))
		}])
	return json.dumps(respuesta)	

		


@app.route("/get_quote")
def getDropboxquote():
	
	Client = client.DropboxClient(sess)
	return json.dumps('{\'Used\':\'' + str(Client.account_info()['quota_info']['normal']) + ',\Total\':\'' + str(Client.account_info()['quota_info']['quota']) + '\'}')


if __name__ == "__main__":
	app.run(debug=True)


