# Restaurant-Management-System

A web-based Restaurant Management System developed using **Flask**, **MySQL**, **HTML**, and **CSS**. It allows users to view menu categories (Veg, Non-Veg, Snacks, Beverages), add items to a cart, and place orders efficiently.

## Features

- User sign-up and login
- Menu browsing (veg, non-veg, snacks, beverages)
- Add-to-cart functionality
- Order storage and management

---

## Tech Stack

- **Frontend**: HTML, CSS
- **Backend**: Python (Flask)
- **Database**: MySQL
- **Tools**: VS Code, Git, GitHub

---

## Project Structure

Restaurant-Management-System/
│
├── static/
│ └── images/
├── templates/
│ └── *.html
├── app.py
├── restaurant_db.sql
└── README.md


## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/RAnanyagit/Restaurant-Management-System.git
   cd Restaurant-Management-System
Set up a virtual environment (optional but recommended):

bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate
Install required packages:

bash
Copy
Edit
pip install flask mysql-connector-python
Import the restaurant_db.sql into your MySQL database.

Run the app:

bash
Copy
Edit
python app.py
Open http://127.0.0.1:5000 in your browser.
