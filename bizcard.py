


import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re
import io
import sqlite3

#image_import
def image_to_text(path):
  input_img= Image.open(path)

  #convert image to array
  image_arr= np.array(input_img)

  reader= easyocr.Reader(['en'])
  text=reader.readtext(image_arr,detail= 0)

  return text,input_img

#_extract_text
def extracted_text(texts):

  extracted_dict = {"NAME":[],"DESIGNATION":[],"COMPANY_NAME":[],"CONTACT":[],"EMAIL":[],
                  "WEBSITE":[],"ADDRESS":[],"PINCODE":[]}

  extracted_dict["NAME"].append(texts[0])
  extracted_dict["DESIGNATION"].append(texts[1])

  for i in range(2,len(texts)):

    if texts[i].startswith("+") or (texts[i].replace("-","").isdigit() and '-' in texts[i]):
      extracted_dict["CONTACT"].append(texts[i])

    elif "@" in texts[i] and ".com" in texts[i]:
      small =texts[i].lower()
      extracted_dict["EMAIL"].append(small)

    elif "WWW" in texts[i] or "www" in texts[i] or "Www" in texts[i] or "wWw" in texts[i] or "wwW" in texts[i]:
      small = texts[i].lower()
      extracted_dict["WEBSITE"].append(small)

    elif "Tamil Nadu" in texts[i]  or "TamilNadu" in texts[i] or texts[i].isdigit():
      extracted_dict["PINCODE"].append(texts[i])

    elif re.match(r'^[A-Za-z]',texts[i]):
      extracted_dict["COMPANY_NAME"].append(texts[i])

    else:
      remove_colon = re.sub(r'[,;]', '', texts[i])
      extracted_dict["ADDRESS"].append(remove_colon)

  for key,value in extracted_dict.items():
    if len(value)>0:
        concadenate = ' '.join(value)
        extracted_dict[key] = [concadenate]
    else:
        value = 'NA'
        extracted_dict[key] = [value]

  return extracted_dict

#streamlit_part
st.set_page_config(layout= "wide")
st.markdown("<h1 style='text-align: center; color: #FF7F50;'>BizCardX : Extracting Business Card Data with OCR</h1>", unsafe_allow_html=True)
st.markdown("##")

select = option_menu(
    menu_title = None,
    options = ["Home", "Upload", "Preview", "Modify", "Delete"],
    icons =["house","cloud-upload","card-text","pencil-square","trash"],
    default_index=0,
    orientation="horizontal",
    styles={"container": {"padding": "0!important", "background-color": " #7FD8BE","size":"cover", "width": "200"},
        "icon": {"color": "black", "font-size": "25px"},

        "nav-link": {"font-size": "25px", "text-align": "center", "margin": "-2px", "--hover-color": " #FCEFEF"},
        "nav-link-selected": {"background-color": "#FF7F50",  "font-family": "YourFontFamily"}})

if select == "Home":
  col1, col2 = st.columns(2)
  with col1:
    st.markdown("#### :green[**Technologies Used :**] Python, easy OCR, Streamlit, SQLite3, Numpy, Pandas.")

  with col2:
    st.markdown("#### :green[**Overview :**] In this streamlit web app you can upload an image of a business card and extract relevant information from it using easyOCR. You can view, modify or delete the extracted data in this app. This app would also allow users to save the extracted information into a database along with the Uploaded business card image. The database would be able to store multiple entries, each with its own business card image and extracted information.")

if select == "Upload":
  col1,col2,col3= st.columns(3)
  with col2:
    st.markdown('<h2 style="text-align: center; color: #FF7F50;">Extracting texts from business card</h2>', unsafe_allow_html=True)
    st.markdown("<hr style='border: 2.5px solid #7FD8BE;'>", unsafe_allow_html=True)

  img = st.file_uploader("**Upload the image.**", type=["png","jpg","jpeg"])

  if img is not None:
    st.image(img, width=600)

    text_image, input_img = image_to_text(img)
    text_dict = extracted_text(text_image)

    if text_dict:
      col1,col2,col3 = st.columns(3)
      with col2:
        st.success(" Text is Successfully Extracted", icon="✅")

    df= pd.DataFrame(text_dict)
    st.dataframe(df)

    col1,col2,col3 = st.columns(3)
    with col2:
      button_clicked = st.button("Store the Retrieved Text in the Database.", use_container_width=True)
      if button_clicked:

          mydb = sqlite3.connect("bizcardx.db")
          cursor = mydb.cursor()

          #Table creation and insertion
          create_table_query = '''
                  CREATE TABLE IF NOT EXISTS bixcard_details (
                      NAME varchar(225) PRIMARY KEY,
                      DESIGNATION varchar(225),
                      COMPANY_NAME varchar(225),
                      CONTACT varchar(225),
                      EMAIL text,
                      WEBSITE text,
                      ADDRESS text,
                      PINCODE varchar(225)
                  )'''

          cursor.execute(create_table_query)
          for row in df.values.tolist():
              try:
                  cursor.execute("INSERT INTO bixcard_details(NAME, DESIGNATION, COMPANY_NAME, CONTACT, EMAIL, WEBSITE, ADDRESS, PINCODE) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", row)
                  mydb.commit()
              except sqlite3.IntegrityError:
                  st.warning(" Details already exist in the database", icon="⚠️")
              else:
                  st.success(" Data stored successfully in SQLite database", icon="✅")

if select == "Preview":

  st.markdown('<h2 style="text-align: center; color: #FF7F50;">Business card datas in database</h2>', unsafe_allow_html=True)
  st.markdown("<hr style='border: 2.5px solid #7FD8BE;'>", unsafe_allow_html=True)

  mydb = sqlite3.connect("bizcardx.db")
  cursor = mydb.cursor()

  select_query = "select * from bixcard_details"

  cursor.execute(select_query)
  table = cursor.fetchall()
  mydb.commit()

  table_df = pd.DataFrame(table, columns=("NAME","DESIGNATION","COMPANY_NAME","CONTACT","EMAIL",
                                        "WEBSITE","ADDRESS","PINCODE"))
  st.write(table_df)

if select == "Modify":
  col1,col2,col3= st.columns(3)
  with col2:
    st.markdown('<h2 style="text-align: center; color: #FF7F50;">Modify the Data in Database</h2>', unsafe_allow_html=True)
    st.markdown("<hr style='border: 2.5px solid #7FD8BE;'>", unsafe_allow_html=True)
    st.markdown('<h3 style="text-align: center; color: #FF7F50;">Database-Storage of Business Card Information</h3>', unsafe_allow_html=True)

  mydb = sqlite3.connect("bizcardx.db")
  cursor = mydb.cursor()

  select_query = "select * from bixcard_details"

  cursor.execute(select_query)
  table = cursor.fetchall()
  mydb.commit()

  table_df = pd.DataFrame(table, columns=("NAME","DESIGNATION","COMPANY_NAME","CONTACT","EMAIL",
                                        "WEBSITE","ADDRESS","PINCODE"))
  st.dataframe(table_df)

  st.write("")
  st.markdown('<h4 style="text-align: center; color: #FF7F50;">Modify the Data</h4>', unsafe_allow_html=True)

  col1,col2,col3 = st.columns(3)
  with col1:
      select_name = st.selectbox("**Select the Name to mofidy their Bizcard details**", table_df["NAME"])

  new_df = table_df[table_df["NAME"] == select_name]

  st.write("")

  col1, col2 = st.columns(2)
  with col1:
    modify_name = st.text_input("Name", new_df["NAME"].iloc[0])
    modify_desig = st.text_input("Designation", new_df["DESIGNATION"].iloc[0])
    modify_company = st.text_input("Company_Name", new_df["COMPANY_NAME"].iloc[0])
    modify_contact = st.text_input("Contact", new_df["CONTACT"].iloc[0])
  with col2:
    modify_email = st.text_input("Email", new_df["EMAIL"].iloc[0])
    modify_web = st.text_input("Website", new_df["WEBSITE"].iloc[0])
    modify_address = st.text_input("Address", new_df["ADDRESS"].iloc[0])
    modify_pincode = st.text_input("Pincode", new_df["PINCODE"].iloc[0])

  st.write("")
  st.write("")

  col1,col2,col3 = st.columns(3)
  with col2:
      button3 = st.button("Modify", use_container_width=True)

  if button3:
      conn = sqlite3.connect('bizcardx.db')
      cursor = conn.cursor()

      update_query = '''
              UPDATE bixcard_details
              SET NAME=?, DESIGNATION=?, COMPANY_NAME=?, CONTACT=?,
                  EMAIL=?, WEBSITE=?, ADDRESS=?, PINCODE=?
              WHERE NAME=?
      '''

      values = (modify_name, modify_desig, modify_company, modify_contact,
                modify_email, modify_web, modify_address, modify_pincode,
                select_name)

      cursor.execute(update_query, values)
      conn.commit()

      query = "select * from bixcard_details"
      cursor.execute(query)

      table = cursor.fetchall()
      conn.commit()

      df6 = pd.DataFrame(table, columns=["NAME", "DESIGNATION", "COMPANY_NAME", "CONTACT",
                                          "EMAIL", "WEBSITE", "ADDRESS", "PINCODE"])

      st.dataframe(df6)

      st.success(" Successfully Modified", icon="✅")

if select == "Delete":
  st.markdown('<h2 style="text-align: center; color: #FF7F50;">Delete the data from the Database.</h2>', unsafe_allow_html=True)
  st.markdown("<hr style='border: 2.5px solid #7FD8BE;'>", unsafe_allow_html=True)
  st.markdown('<h4 style="text-align: center; color: #FF7F50;">Select the Data</h4>', unsafe_allow_html=True)

  conn = sqlite3.connect('bizcardx.db')
  cursor = conn.cursor()

  col1,col2= st.columns(2)
  with col1:
    cursor.execute("SELECT NAME FROM bixcard_details")
    conn.commit()
    table1= cursor.fetchall()

    names=[]

    for i in table1:
      names.append(i[0])

    name_select= st.selectbox("Select the Name",options= names)

  with col2:
    cursor.execute(f"SELECT DESIGNATION FROM bixcard_details WHERE NAME ='{name_select}'")
    conn.commit()
    table2= cursor.fetchall()

    designations= []

    for j in table2:
      designations.append(j[0])

    designation_select= st.selectbox("Select the Designation", options= designations)

  if name_select and designation_select:
    st.markdown('<h4 style="text-align: center; color: #FF7F50;">Delete the infomation from the Database</h4>', unsafe_allow_html=True)
    col1,col2,col3= st.columns(3)
    with col2:
      st.write("")
      st.write(f"Selected Name : {name_select}")
      st.write("")
      st.write(f"Selected Designation : {designation_select}")
      st.write("")
      st.write("")

    col1,col2,col3= st.columns(3)
    with col2:
      remove= st.button("Yes",use_container_width= True)
      if remove:
        conn.execute(f"DELETE FROM bixcard_details WHERE NAME ='{name_select}' AND DESIGNATION = '{designation_select}'")
        conn.commit()

        st.success(" Successfully Deleted", icon="✅")
