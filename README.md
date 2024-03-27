# bizcardx-extracting-business-card-data-with-ocr
This project aims to develop a Streamlit application that facilitates the extraction of relevant information from business card images using easyOCR. The extracted information, including the company name, card holder name, designation, contact details, and address, is then displayed in the graphical user interface (GUI). Additionally, users have the option to save the extracted information along with the uploaded business card image into a database, enabling multiple entries management.

# Features
Upload business card images for information extraction.
Extract relevant information using easyOCR.
Display extracted information in a clean and organized GUI.
Save extracted information and corresponding business card images into a database.
Read, update, and delete entries through the Streamlit UI.

# Technologies Used
Python
Streamlit
easyOCR
SQLite (or MySQL for database management)

# Usage
Upload a business card image using the provided interface.
Wait for the information extraction process to complete.
View the extracted information displayed on the GUI.
Optionally, save the extracted information along with the uploaded image into the database.
Perform read, update, and delete operations on the database entries as needed.

# Application Architecture
The application follows a modular architecture, with separate components for image processing, OCR, GUI development, and database management. This design ensures scalability, maintainability, and extensibility of the application.
