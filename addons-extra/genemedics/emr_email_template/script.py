import xmlrpclib
import psycopg2
username = 'mehtanaitik23@gmail.com'
password = 'a'
dbname = 'genemedics_1_feb'
server = 'localhost'
port = '8069'

res = {}
sock_common = xmlrpclib.ServerProxy ('http://' + server + ':' + port + ' /xmlrpc/2/common')
uid = sock_common.login(dbname, username, password)
sock = xmlrpclib.ServerProxy('http://' + server + ':' + port + '/xmlrpc/2/object', allow_none=True)
con = psycopg2.connect(database='genemedics_1_feb', user='postgres', port=5432, host='localhost', password='serpentcs')
labs_due_rec = sock.execute(dbname, uid, password, 'crm.lead', 'send_labs_due', patient_name, address, patient_email, lab_due_date, panel_type, reason)
cur = con.cursor()