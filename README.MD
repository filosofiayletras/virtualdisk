INTRODUCCIÓN.

VIRTUALDISKSD es un API implementado en Python (2.7) que viene a resolver una situación provocada por la oferta de almacenamiento gratuito en la nube. El hecho de registrarse en varios servicios gratuitos nos aporta una gran capacidad de almacenamiento, pero nos obliga a llevar un control de qué ficheros subimos y dónde los subimos, encontrándonos en ocasiones con situaciones en las que tenemos un servicio prácticamente en desuso y otro al borde del colapso. VIRTUALDISKSD nace con la finalidad de ofrecer un servicio centralizado de almacenamiento en la nube.

FUNCIONES QUE PROVEE API VIRTUALDISKSD: 

home(): No recibe ningún parámetro y devuelve el fichero html que será el index de del servicio web de VIRTUALDISKSD.
Total_List(): No recibe ningún parámetro y devuelve un html que será el encargado de mostrar por pantalla la lista con todos los elementos almacenados en la nube.
driveConfig(): No recibe ningún parámetro y devuelve un html para autentificarte en el servicio de Google Drive.
uploadDriveFile(): No recibe ningún parámetro y devuelve un html que sirve para subir un fichero al servicio Google Drive.
driveList(): No recibe ningún parámetro y devuelve un html que contiene una lista con los ficheros alojados únicamente en Google Drive.
DropboxAutentication():No recibe ningún parámetro y devuelve un html para autentificarte en el servicio de Dropbox.
uploadDropboxFile():No recibe ningún parámetro y devuelve un html que sirve para subir un fichero al servicio Dropbox.
dropboxList():No recibe ningún parámetro y devuelve un html que contiene una lista con los ficheros alojados únicamente en Dropbox.
automaticUpload(): Compara que servicio tiene mayor capacidad y realiza la subida a de un fichero a este.
getlist(): Obtiene los json de todos los servicios y los junta en uno, mostrando la informacion en la web.
getDriveAuth(): Obtiene la url de autorización y la devuelve con un json.
driveAuth(): Recibe el código de la autorización y lo guarda en un fichero de texto.
getDriveQuota(): Devuelve un json con información sobre el espacio de Google Drive como la capacidad total o el espacio usado.
uploadToDrive(): Método para subir un archivo a Google Drive, devuelve el código 200 si todo es correcto.
getDriveList(): Método para obtener un json con los archivos alojados en Google Drive.
removeDriveFile(): Elimina un archivo de Google Drive, devuelve un código 200 para indicar que todo ha sido correcto.

getDropboxAuth(): Devuelve un json con la url de la autorización.
dropboxAuth(): Guarda la autorización en un fichero de texto.
uploadToDropbox(): Método usado para subir un fichero a Dropbox, devuelve el código 200 si todo es correcto.
getDropboxList():Método para obtener un json con los archivos alojados Dropbox.
getDropboxQuota():Devuelve un json con información sobre el espacio de Dropbox como la capacidad total o el espacio usado.
removeDropboxFile():Elimina un archivo de Dropbox, devuelve un código 200 para indicar que todo ha sido correcto.
Persistencia con JSON: En nuestra aplicación, hacemos uso de dos ficheros que contienen JSON, con la finalidad de almacenar los credenciales de autorización para las APIs de Google Drive y Dropbox. Estos ficheros son creados una vez que se generan los credenciales, y se mantienen mientras que sean válidos o el usuario no genere unos nuevos. En futuras versiones, convendrá guardar los credenciales en una base de datos, para mejorar el mantenimiento, seguridad y escalabilidad.


