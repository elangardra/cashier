import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("retail-dffbf-firebase-adminsdk-6ifc3-1e0cc7d14c.json")
firebase_app = firebase_admin.initialize_app(cred, { "databaseURL": "https://retail-dffbf-default-rtdb.asia-southeast1.firebasedatabase.app/" })
