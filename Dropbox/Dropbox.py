# Include the Dropbox SDK libraries
from dropbox import client, rest, session
 
# Get your app key and secret from the Dropbox developer website
APP_KEY = 'qvkwb9hpaggsnac'
APP_SECRET = 'jlv4jmek1t6j0j1'
 
# ACCESS_TYPE should be 'dropbox' or 'app_folder' as configured for your app
ACCESS_TYPE = 'app_folder'
 
sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
request_token = sess.obtain_request_token()
url = sess.build_authorize_url(request_token)
 
# Make the user sign in and authorize this token
print "url:", url
print "Please visit this website and press the 'Allow' button, then hit 'Enter' here."
raw_input()
 
# This will fail if the user didn't visit the above URL
access_token = sess.obtain_access_token(request_token)

 
#Print the token for future reference
print access_token.key
print access_token.secret


# We will use the OAuth token we generated already. The set_token API 
# accepts the oauth_token and oauth_token_secret as inputs.
sess.set_token(access_token.key,access_token.secret )
 
# Create an instance of the dropbox client for the session. This is
# all we need to perform other actions
client = client.DropboxClient(sess)
print "linked account:", client.account_info()['display_name']

# Let's upload a file
f = open('pruebasubida.txt','rb')
response = client.put_file('/pruebasubida.txt', f)
print "uploaded:", response['path']


#Metadata of full folder

#folder_metadata = client.metadata('/')
#print "metadata:", folder_metadata

#Metadata of a given file

#rev  = folder_metadata['contents'][1]['rev']
#path = folder_metadata['contents'][1]['path']
#print rev
#print path

#f, metadata = client.get_file_and_metadata(path,rev)


#Let's download a file(share link, the 
print client.share(response['path'])['url']

#quota_info/normal	The user's used quota outside of shared folders (bytes).
#quota_info/shared	The user's used quota in shared folders (bytes). If the user belongs to a team, this includes all usage contributed to the team's quota outside of the user's own used quota (bytes).
#quota_info/quota	The user's total quota allocation (bytes). If the user belongs to a team, the team's total quota allocation (bytes).
print client.account_info()['quota_info']


