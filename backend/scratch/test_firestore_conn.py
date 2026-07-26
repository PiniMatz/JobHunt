import firebase_admin
from firebase_admin import credentials, firestore

def main():
    print("Testing Firebase Firestore connection to project 'jobhunt2-4ee1f'...")
    try:
        if not firebase_admin._apps:
            firebase_admin.initialize_app(options={'projectId': 'jobhunt2-4ee1f'})
            
        db = firestore.client()
        print("Connected to Firestore client!")
        
        # Try reading settings collection
        doc_ref = db.collection('settings').document('config')
        doc = doc_ref.get()
        if doc.exists:
            print("Settings doc found:", doc.to_dict())
        else:
            print("Settings doc does not exist yet. Writing default settings...")
            default_settings = {
                "cv_markdown": "",
                "api_key": "",
                "locations": ["Netanya"],
                "threshold": 70,
                "must_have_keywords": ["Product Manager", "Product Owner", "PM"],
                "exclusion_keywords": ["Junior", "Intern", "Student"]
            }
            doc_ref.set(default_settings)
            print("Default settings document created successfully in Firestore!")
            
    except Exception as e:
        print(f"Firestore connection error: {e}")

if __name__ == '__main__':
    main()
