# Startup Instructions for Engineering Equation Solver

This guide outlines the steps to set up and run the Engineering Equation Solver application, including both the Python backend and the React frontend.

## Prerequisites

Ensure you have the following installed on your system:
- **Python 3.8+**
- **Node.js 16+** and **npm**

## 1. Backend Setup (Python/FastAPI)

The backend handles the equation solving logic, unit conversions, and thermodynamic property lookups.

### Installation
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. (Optional but recommended) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Server
Start the FastAPI server using `uvicorn`:
```bash
uvicorn main:app --reload --port 8000
```
The backend API will be available at `http://localhost:8000`.
You can check the health status at `http://localhost:8000/health`.

## 2. Frontend Setup (React/Vite)

The frontend provides the user interface for inputting equations and viewing results.

### Installation
1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install the Node.js dependencies:
   ```bash
   npm install
   ```

### Running the Development Server
Start the Vite development server:
```bash
npm run dev
```
The web application will be accessible at `http://localhost:5173`.

## 3. Verification

1. Ensure the backend is running on port **8000**.
2. Ensure the frontend is running on port **5173**.
3. Open your browser to `http://localhost:5173`.
4. You should see the "Engineering Equation Solver" title and a status message indicating **"Backend Connected ✅"**.

## Troubleshooting

- **Backend fails to start**: Check for missing dependencies or syntax errors in the Python code. Ensure no other service is using port 8000.
- **Frontend cannot connect**: Ensure the backend is running *before* you try to interact with the frontend. Check the browser console (F12) for CORS or network errors.
