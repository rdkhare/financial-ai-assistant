# financial-ai-assistant
Finance AI assistant for visualizing expenses and managing them.

## How to Run the App
This project contains both a frontend (Next.js) and a backend (Flask). Follow these steps to set up and run the app locally:

### 1. Set Up the Backend
1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Set up a virtual environment:**
   - Create the virtual environment:
     ```bash
     python -m venv venv
     ```
   - Activate the virtual environment:
     - **macOS/Linux:**
       ```bash
       source venv/bin/activate
       ```
     - **Windows:**
       ```bash
       venv\Scripts\activate
       ```

3. **Install required libraries:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the backend server:**
   Make sure you are still in the virtual environment:
   ```bash
   python run.py
   ```

   The backend server will start on `http://127.0.0.1:5001/`.

### 2. Set Up the Frontend
1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Run the frontend server:**
   ```bash
   npm run dev
   ```

   The frontend server will start on `http://localhost:3000/`.

### 3. Access the App
- Open your browser and go to `http://localhost:3000` to access the app.

### Notes
- Ensure both the backend and frontend servers are running simultaneously for the app to work properly.
- If you encounter any issues, check the terminal logs for errors in either the backend or frontend servers.
- You will need to create and use your own Plaid Dev account

- Create a .env file in backend/ with variables:
    ```bash
    PLAID_CLIENT_ID = "path/to/your/plaid/client/id"
    PLAID_SECRET = "path/to/your/plaid/secretkey"
    PLAID_ENV = "sandbox"
    MONGO_URI = "mongodb_connectionstring"
    ```