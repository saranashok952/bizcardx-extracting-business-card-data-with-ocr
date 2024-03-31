import streamlit as st
import easyocr
from PIL import Image
import re
import numpy as np
import pandas as pd
import sqlite3

# Function to perform OCR on the uploaded image
def perform_ocr(import_image):
    try:
        reader = easyocr.Reader(['en'])
        image = Image.open(import_image)
        image_array = np.array(image)
        result = reader.readtext(image_array)
        return result
    except Exception as e:
        st.error(f"Error occurred during OCR: {e}")
        return None

# Function to create SQLite connection and table
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        st.error(f"Error connecting to SQLite database: {e}")
    return conn

def create_table(conn):
    create_table_sql = """
        CREATE TABLE IF NOT EXISTS extracted_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            designation TEXT,
            company_name TEXT,
            contact TEXT,
            email TEXT,
            website TEXT,
            address TEXT,
            city TEXT,
            pincode TEXT,
            state TEXT
        );
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        st.error(f"Error creating table: {e}")

# Function to insert extracted data into SQLite
# Function to insert extracted data into SQLite
# Function to insert extracted data into SQLite
def insert_data(conn, data):
    sql = """
        INSERT INTO extracted_info (name, designation, company_name, contact, email, website, address, city, pincode, state)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    try:
        cur = conn.cursor()

        # Check if the entry already exists
        cur.execute("SELECT * FROM extracted_info WHERE name = ? AND designation = ?", (data[0], data[1]))
        existing_entry = cur.fetchone()

        if existing_entry:
            st.warning("Duplicate entry detected. Data not inserted.")
            return None
        else:
            cur.execute(sql, data)
            conn.commit()
            st.success("Data inserted into SQLite database successfully!")
            return cur.lastrowid

    except sqlite3.Error as e:
        st.error(f"Error inserting data into SQLite database: {e}")
        return None


# Function to extract relevant information from OCR results
def extracted_text(texts):
    extrd_dict = {
        "NAME": [],
        "DESIGNATION": [],
        "COMPANY_NAME": [],
        "CONTACT": [],
        "EMAIL": [],
        "WEBSITE": [],
        "ADDRESS": [],
        "CITY": [],
        "PINCODE": [],
        "STATE": []
    }

    extrd_dict["NAME"].append(texts[0])
    extrd_dict["DESIGNATION"].append(texts[1])

    for i in range(2, len(texts)):
        if texts[i].startswith("+") or (texts[i].replace("-", "").isdigit() and '-' in texts[i]):
            extrd_dict["CONTACT"].append(texts[i])
        elif "@" in texts[i] and ".com" in texts[i]:
            small = texts[i].lower()
            extrd_dict["EMAIL"].append(small)
        elif any(prefix in texts[i].lower() for prefix in ("www", "http", "https")) and ".com" in texts[i]:
            small = texts[i].lower()
            extrd_dict["WEBSITE"].append(small)
        elif "Tamil Nadu" in texts[i] or "TamilNadu" in texts[i]:
            extrd_dict["STATE"].append("TamilNadu")
        elif re.match(r'^\d{6}$', texts[i]):  # Match pin code with 6 digits
            extrd_dict["PINCODE"].append(texts[i])
        elif len(texts[i]) >= 6 and texts[i].isdigit():
            extrd_dict["PINCODE"].append(texts[i])
        elif re.findall("[a-zA-Z]{9} +[0-9]", texts[i]):
            extrd_dict["PINCODE"].append(texts[i][10:])
        elif re.search(r'St\.\s+(\w+)\s+TamilNadu', texts[i]):
            city = re.search(r'St\.\s+(\w+)\s+TamilNadu', texts[i]).group(1)
            extrd_dict["CITY"].append(city)
        elif re.match(r'^[A-Za-z]', texts[i]):
            extrd_dict["COMPANY_NAME"].append(texts[i])
            if extrd_dict["COMPANY_NAME"]:
              extrd_dict["COMPANY_NAME"] = [' '.join(extrd_dict["COMPANY_NAME"])]
        else:
            remove_colon = re.sub(r'[,;]', '', texts[i])
            extrd_dict["ADDRESS"].append(remove_colon)

    # Join contact information into a single string
    extrd_dict["CONTACT"] = [', '.join(extrd_dict["CONTACT"])]

    for key, value in extrd_dict.items():
        if len(value) == 0:
            extrd_dict[key] = ["NA"]

    return extrd_dict

def display_home():    

    st.markdown("<p class='big-font'>Extracting Business Card Data with OCR</p>", unsafe_allow_html=True)

def main():
    # Create a connection to SQLite database
    conn = create_connection("extracted_info.db")
    if conn is not None:
        # Create table if not exists
        create_table(conn)

    # Define the options for the main menu
    main_options = ("Home", "Upload & Extract", "Delete")

    # Use option menus for all sections
    with st.sidebar:
        select = st.selectbox("Main Menu", main_options)

    if select == "Home":
      col1, col2 = st.columns(2)
      with col1:
          st.markdown("#### :green[**Technologies Used :**] Python, easy OCR, Streamlit, SQLite3, Pandas.")

      with col2:
          st.markdown("#### :green[**Overview :**] In this streamlit web app you can upload an image of a business card and extract relevant information from it using easyOCR. You can view, modify or delete the extracted data in this app. This app would also allow users to save the extracted information into a database along with the Uploaded business card image. The database would be able to store multiple entries, each with its own business card image and extracted information.")

    elif select== "Upload & Extract":
        st.markdown("### Upload a Business Card")
        uploaded_card = st.file_uploader("Upload here", type=["png", "jpeg", "jpg"])

        if uploaded_card is not None:
            image = Image.open(uploaded_card)
            st.image(image, caption='Uploaded Business Card', use_column_width=True)

            # Perform OCR on the uploaded image
            result = perform_ocr(uploaded_card)

            if result:
                # Extract text from the OCR result
                text_result = [text[1] for text in result]
                st.success("### Data Extracted!")
                extracted_info = extracted_text(text_result)  
                df = pd.DataFrame(extracted_info)
                st.write("Extracted Information:")
                st.write(df)

                # Insert data into SQLite
                if conn is not None:
                    with conn:
                        data = (
                            extracted_info["NAME"][0],
                            extracted_info["DESIGNATION"][0],
                            extracted_info["COMPANY_NAME"][0],
                            extracted_info["CONTACT"][0],
                            extracted_info["EMAIL"][0],
                            extracted_info["WEBSITE"][0],
                            extracted_info["ADDRESS"][0],
                            extracted_info["CITY"][0],
                            extracted_info["PINCODE"][0],
                            extracted_info["STATE"][0]
                        )
                        insert_data(conn, data)
                        
                        # Query the database to retrieve inserted data
                        cursor = conn.cursor()
                        cursor.execute("SELECT * FROM extracted_info")
                        rows = cursor.fetchall()
                        if rows:
                            st.write("Data in SQLite Database:")
                            df_sqlite = pd.DataFrame(rows, columns=["ID", "Name", "Designation", "Company Name", "Contact", "Email", "Website", "Address", "City", "Pincode", "State"])
                            st.write(df_sqlite)

            else:
                st.error("Error occurred during OCR, please try again.")

    elif select == "Delete":
        st.title("Manage Extracted Data")
        st.sidebar.subheader("Options")
        
        # Check if there is data available for deletion
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM extracted_info")
            rows = cursor.fetchall()
            if rows:
                # Define options for deletion section
                delete_options = ("View Data", "Delete Entry")
                # Use option menu for selection
                selection = st.sidebar.selectbox("View Data or Delete Entry", delete_options)
            else:
                selection = "View Data"
        else:
            selection = "View Data"

        if selection == "View Data":
            st.subheader("View Extracted Data")
            if conn is not None:
                # Query the database to retrieve all data
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM extracted_info")
                rows = cursor.fetchall()
                if rows:
                    df_sqlite = pd.DataFrame(rows, columns=["ID", "Name", "Designation", "Company Name", "Contact", "Email", "Website", "Address", "City", "Pincode", "State"])
                    st.write(df_sqlite)
                else:
                    st.write("No data available in SQLite database.")

        elif selection == "Delete Entry":
            st.subheader("Delete Specific Entry")
            # Display dropdown menu to select entry for deletion
            if conn is not None:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM extracted_info")
                rows = cursor.fetchall()
                entries = [f"{row[0]} - {row[1]}" for row in rows]  # Display ID and Name for each entry
                selected_entry = st.selectbox("Select entry to delete", entries)

                if st.button("Delete"):
                    selected_id = int(selected_entry.split(" - ")[0])
                    cursor.execute("DELETE FROM extracted_info WHERE id=?", (selected_id,))
                    conn.commit()
                    st.success("Entry deleted successfully.")

if __name__ == "__main__":
    st.set_page_config(page_title="BizCardX: Extracting Business Card Data with OCR",
                      layout="wide",
                      initial_sidebar_state="expanded",
                      menu_items={'About': """# BizCardX: Extracting Business Card Data with OCR*!"""})
    st.markdown("<h1 style='text-align: center; color: white;'>BizCardX: Extracting Business Card Data with OCR</h1>",
                unsafe_allow_html=True)
