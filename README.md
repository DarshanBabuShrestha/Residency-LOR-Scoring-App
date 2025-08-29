pip install -r requirements.txt


#run frontend

-cd frontend
-npm install
-npm run dev


#run backend:

-cd backend
-python -m uvicorn app:app --reload
