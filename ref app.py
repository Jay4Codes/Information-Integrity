import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_folium import folium_static
import folium
import pandas as pd
import requests
import time
from streamlit_pdf_viewer import pdf_viewer
import json
import fitz
import plotly.express as px
from annotated_text import annotated_text
from PIL import Image, ImageDraw

def main():

    st.set_page_config(
        page_title="SimPPL", layout="wide", initial_sidebar_state="auto", page_icon="📄"
    )

    st.image("icon.png")
    st.title("SimPPL")
    st.subheader("Welcome to SimPPL")
    with st.expander("About this app", expanded=False):
        st.write(   
            "Intelligent"
        )

    with st.sidebar:
        st.image("icon.png")
        st.title("SimPPL")
        selected_page = option_menu(
            None,
            ["Upload Document", "Document Summary", "Document Viewer", "Document Data", "Provider Data"],
            icons=["cloud-upload", "file-earmark-bar-graph", "file-earmark-text", "database-fill-up", "map"],
            menu_icon="cast",
            default_index=0,
        )

    if selected_page == "Upload Document":
        st.markdown("##### Upload PDF file")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

        home_col1, home_col2 = st.columns(2)
        with home_col1:
            preview = st.button(label="Preview")
            if preview:
                if uploaded_file:
                    with open(f"pdfs/{uploaded_file.name}", "wb") as f:
                        f.write(uploaded_file.getbuffer())
                        pdf_viewer(
                            input=f"pdfs/{uploaded_file.name}",
                            width=400,
                            height=600,
                            pages_vertical_spacing=1,
                            annotation_outline_size=1,
                        )
                else:
                    st.warning(
                        """Kindly upload a PDF file""",
                        icon="⚠️",
                    )

        with home_col2:
            submitted = st.button(label="Submit")
            if submitted:
                if uploaded_file:
                    pdf_file = fitz.open(f"pdfs/{uploaded_file.name}")
                    for i in range(pdf_file.page_count):
                        page = pdf_file.load_page(i)
                        pix = page.get_pixmap()
                        pix.pil_save(f"pages/{uploaded_file.name.split('.')[0]}_{i}.png")

                    parse_response = requests.post(parse_doc_url, files={"file": open(f"pdfs/{uploaded_file.name}", "rb")})
                    parse_requestId = parse_response.json()["requestId"]
                    request_status = "Processing"
                    
                    with st.spinner("Processing..."):
                        while request_status != "Done":                                  
                            response = requests.get(data_fetch_url, params={"requestId": parse_requestId},
                                                    files={"file": open(f"pdfs/{uploaded_file.name}", "rb")})
                            if response.status_code == 200:
                                request_status = response.json()["status"]
                                
                            time.sleep(5)  
                        
                        with open("response.json", "w") as f:
                            f.write(json.dumps(response.json()["data"]))
                        
                    st.success("File submitted successfully")
                
                else:
                    st.warning(
                        """Kindly upload a PDF file""",
                        icon="⚠️",
                    )          

    elif selected_page == "Document Summary":
        st.markdown("##### Document Summary")
        response = json.loads(open('./response.json', 'r').read())
        if response:
            summary_df = pd.DataFrame(columns=["Page No", "Document Type", "Handwritten Lines", "Printed Lines", "Document Category"])
            for index, obj in enumerate(response): 
                summary_df = pd.concat(
                    [
                        summary_df,
                        pd.DataFrame(
                            {
                                "Page No":  obj["img_page_no"],
                                "Document Type": "Handwritten" if obj["lines"]["handwritten"] >= 10 else "Printed",
                                "Handwritten Lines": obj["lines"]["handwritten"],
                                "Printed Lines": obj["lines"]["printed"],
                                "Document Category": obj["document_category"]["category"]
                            }
                            , index=[index+1]
                        ),
                    ]
                )

            # st.data_editor(summary_df, hide_index=True)
            
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                fig = px.pie(summary_df, names="Document Type", title="Document Type Distribution", hole=0.3)
                fig.update_traces(textinfo="value", textposition="inside", textfont_size=18)
                
                st.plotly_chart(fig, use_container_width=True)

            with chart_col2:
                fig = px.bar(summary_df, x="Document Category", y="Handwritten Lines", title="Handwritten Lines Distribution")
                st.plotly_chart(fig, use_container_width=True)


    elif selected_page == "Document Viewer":
        st.markdown("##### Document Processing")

        response = json.loads(open('./response.json', 'r').read())
        if response:
            process_df = pd.DataFrame(columns=["Page No", "Page", "Processed Page", 
                                               "Cropped", "Angle Rotated", "QR Code", "Bar Code",
                                               "Logo", "Signature", "Stamp", "CheckBox"])
            
            processes =["All"]
            no_of_croped = 0
            no_of_angle_rotated = 0
            logos = 0
            qr_codes = 0
            bar_codes = 0
            signatures = 0
            stamps = 0
            checkboxes = 0

            for obj in response:
                if obj["croped"]:
                    no_of_croped += 1
                if obj["angle"]['value'] != 0:
                    no_of_angle_rotated += 1
                if obj["img_objects"]["logo"]["found"]:
                    logos += 1
                if obj["img_objects"]["qrCode"]["found"]:
                    qr_codes += 1
                if obj["img_objects"]["barCode"]["found"]:
                    bar_codes += 1
                if obj["img_objects"]["signature"]["found"]:
                    signatures += 1
                if obj["img_objects"]["stamp"]["found"]:
                    stamps += 1
                if obj["img_objects"]["checkedItem"]["found"]:
                    checkboxes += 1
                    
            if no_of_croped > 0:
                processes.append("Cropped")
            if no_of_angle_rotated > 0:
                processes.append("Angle Rotated")
            if logos > 0:
                processes.append("Logo")
            if qr_codes > 0:
                processes.append("QR Code")
            if bar_codes > 0:
                processes.append("Bar Code")
            if signatures > 0:
                processes.append("Signature")
            if stamps > 0:
                processes.append("Stamp")
            if checkboxes > 0:
                processes.append("CheckBox")

            process_col1, process_col2 = st.columns(2)
            with process_col1:
                selected_process = st.selectbox("Select Process", processes, index=0)

            with process_col2:
                if selected_process == "Cropped" and no_of_croped > 0:
                    min_value = 1
                    max_value = no_of_croped
                elif selected_process == "Angle Rotated" and no_of_angle_rotated > 0:
                    min_value = 1
                    max_value = no_of_angle_rotated
                elif selected_process == "Logo" and logos > 0:
                    min_value = 1
                    max_value = logos
                elif selected_process == "QR Code" and qr_codes > 0:
                    min_value = 1
                    max_value = qr_codes
                elif selected_process == "Bar Code" and bar_codes > 0:
                    min_value = 1
                    max_value = bar_codes
                elif selected_process == "Signature" and signatures > 0:
                    min_value = 1
                    max_value = signatures
                elif selected_process == "Stamp" and stamps > 0:
                    min_value = 1
                    max_value = stamps
                elif selected_process == "CheckBox" and checkboxes > 0:
                    min_value = 1
                    max_value = checkboxes
                else:
                    min_value = 1
                    max_value = len(response)
                    
                page_no = st.number_input("Page No", min_value=min_value, max_value=max_value, value=1)

            for index, obj in enumerate(response):
                process_df = pd.concat(
                    [
                        process_df,
                        pd.DataFrame(
                            {
                                "Page No":  obj["img_page_no"],
                                "Page": f"pages/{obj['file_name'][:-4]}_{obj['img_page_no']-1}.png".replace('â€¯', ' '),
                                "Processed Page": obj["file_url"].replace(' ', '%20').replace('â€¯', '%E2%80%AF'),
                                "Cropped": obj["croped"],
                                "Angle Rotated": obj["angle"]['value'],
                                "QR Code": obj["img_objects"]["qrCode"]["found"],
                                "Bar Code": obj["img_objects"]["barCode"]["found"],
                                "Logo": obj["img_objects"]["logo"]["found"],
                                "Signature": obj["img_objects"]["signature"]["found"],
                                "Stamp": obj["img_objects"]["stamp"]["found"],
                                "CheckBox": obj["img_objects"]["checkedItem"]["found"]
                            }
                            , index=[index+1]
                        ),
                    ]
                )

            filtered_df = process_df.copy()

            if selected_process == "Cropped":
                filtered_df = filtered_df[filtered_df["Cropped"] == True]
            if selected_process == "Angle Rotated":
                filtered_df = filtered_df[filtered_df["Angle Rotated"] != 0]
            if selected_process == "Logo":
                filtered_df = filtered_df[filtered_df["Logo"] == True]
            if selected_process == "QR Code":
                filtered_df = filtered_df[filtered_df["QR Code"] == True]
            if selected_process == "Bar Code":
                filtered_df = filtered_df[filtered_df["Bar Code"] == True]
            if selected_process == "Signature":
                filtered_df = filtered_df[filtered_df["Signature"] == True]
            if selected_process == "Stamp":
                filtered_df = filtered_df[filtered_df["Stamp"] == True]
            if selected_process == "CheckBox":
                filtered_df = filtered_df[filtered_df["CheckBox"] == True]

            viewer_col1, viewer_col2 = st.columns(2)

            with viewer_col1:
                st.image(filtered_df["Page"].iloc[page_no-1], caption="Original Page", use_column_width=True)
            
            with viewer_col2:
                if selected_process == "Logo":
                    img = Image.open(filtered_df["Page"].iloc[page_no-1])
                    logo = response[filtered_df["Page No"].iloc[page_no-1]-1]["img_objects"]["logo"]["loc"][0]
                    draw = ImageDraw.Draw(img)
                    draw.rectangle(logo, outline="red", width=5)
                    st.image(img, caption="Logo", use_column_width=True)
                elif selected_process == "QR Code":
                    img = Image.open(filtered_df["Page"].iloc[page_no-1])
                    qrCode = response[filtered_df["Page No"].iloc[page_no-1]-1]["img_objects"]["qrCode"]["loc"][0]
                    draw = ImageDraw.Draw(img)
                    draw.rectangle(qrCode, outline="red", width=5)
                    st.image(img, caption="QR Code", use_column_width=True)
                elif selected_process == "Bar Code":
                    img = Image.open(filtered_df["Page"].iloc[page_no-1])
                    barCode = response[filtered_df["Page No"].iloc[page_no-1]-1]["img_objects"]["barCode"]["loc"][0]
                    draw = ImageDraw.Draw(img)
                    draw.rectangle(barCode, outline="red", width=5)
                    st.image(img, caption="Bar Code", use_column_width=True)
                elif selected_process == "Signature":
                    img = Image.open(filtered_df["Page"].iloc[page_no-1])
                    signature = response[filtered_df["Page No"].iloc[page_no-1]-1]["img_objects"]["signature"]["loc"][0]
                    draw = ImageDraw.Draw(img)
                    draw.rectangle(signature, outline="red", width=5)
                    st.image(img, caption="Signature", use_column_width=True)
                elif selected_process == "Stamp":
                    img = Image.open(filtered_df["Page"].iloc[page_no-1])
                    stamp = response[filtered_df["Page No"].iloc[page_no-1]-1]["img_objects"]["stamp"]["loc"][0]
                    draw = ImageDraw.Draw(img)
                    draw.rectangle(stamp, outline="red", width=5)
                    st.image(img, caption="Stamp", use_column_width=True)
                elif selected_process == "CheckBox":
                    img = Image.open(filtered_df["Page"].iloc[page_no-1])
                    checkBox = response[filtered_df["Page No"].iloc[page_no-1]-1]["img_objects"]["checkedItem"]["loc"][0]
                    draw = ImageDraw.Draw(img)
                    draw.rectangle(checkBox, outline="red", width=5)
                    st.image(img, caption="CheckBox", use_column_width=True)
                else:
                    st.image(filtered_df["Processed Page"].iloc[page_no-1], caption="Processed Page", use_column_width=True)
                    

    elif selected_page == "Document Data":
        st.markdown("##### Document Data")

        response = json.loads(open('./response.json', 'r').read())
        if response:

            data_filter_col1, data_filter_col2 = st.columns(2)

            with data_filter_col1:
                doc = st.selectbox("Select Document", ["Cheque", "Invoice", "DischargeCard", 
                                                    "PreAuthForm1", "PreAuthForm2", "PreAuthForm3", "PreAuthForm4", "PreAuthForm5", "PreAuthForm6"])
                
                doc_pages = [obj for obj in response if obj["document_category"]["category"] == doc]
            
            if len(doc_pages) > 0:

                data_page_no = 0
                view_raw_text = False
                view_image = False
                view_data = False
                document_mapper = {
                    "date":{
                        "Invoice": "invoice_date",
                        "DischargeCard": "date_of_discharge"
                    },
                    "addtional_table": {
                        "Invoice": "bill_items",
                        "DischargeCard": "medicines"
                    }
                }
                
                document_df = pd.DataFrame(columns=["Image Name", "Page Number", "Document Category", "Date", "View Image", "View Data"])
                
                
                for index, doc_obj in enumerate(doc_pages):
                    if doc_obj["document_category"]["category"] in document_mapper["date"]:
                        document_df = pd.concat(
                            [
                                document_df,
                                pd.DataFrame(
                                    {
                                        "Image Name": doc_obj["img_name"].replace('â€¯', ' '),
                                        "Page Number": doc_obj["img_page_no"],
                                        "Document Category": doc_obj["document_category"]["category"],
                                        "Date": [doc_obj["fields"]['tags'][
                                            document_mapper["date"][
                                                doc_obj["document_category"]["category"] 
                                            ]]],
                                        "View Image": view_image,
                                        "View Data": view_data,
                                    }
                                    , index=[index+1]
                                )
                            ]
                        )
                    else:
                        document_df = pd.concat(
                            [
                                document_df,
                                pd.DataFrame(
                                    {
                                        "Image Name": doc_obj["img_name"].replace('â€¯', ' '),
                                        "Page Number": doc_obj["img_page_no"],
                                        "Document Category": doc_obj["document_category"]["category"],
                                        "Date": ["Not Available"],
                                        "View Image": view_image,
                                        "View Data": view_data,
                                    }
                                    , index=[index+1]
                                )
                            ]
                        )
                    
                document_df = document_df.sort_values(by="Date", ascending=False)
                edited_df = st.data_editor(document_df, hide_index=True, use_container_width=True, 
                                           disabled=["Image Name", "Page Number", "Document Category", 
                                                     "Date"])
                
                for index, row in edited_df.iterrows():
                    if row["View Image"] or row["View Data"]:
                        data_page_no = index
                        view_raw_text = True
                        if row["View Image"]:
                            view_image = True
                        if row["View Data"]:
                            view_data = True
                
                if 'raw_text' in doc_pages[data_page_no-1]:
                    raw_text = doc_pages[data_page_no-1]['raw_text']
                    annotated_text_list = []
                    for word in raw_text.split():
                        annotated_text_list.append(word)

                fields_df = pd.DataFrame(columns=["Field", "Value"])
                
                if "fields" in doc_pages[data_page_no-1] and "tags" in doc_pages[data_page_no-1]["fields"]:
                    for key, value in doc_pages[data_page_no-1]["fields"]['tags'].items():
                        if key != "bill_items" and key != "medicines":
                            if type(value) == list:                                    
                                for wrd in ', '.join(value).split():
                                    if wrd in annotated_text_list:
                                        annotated_text_list[annotated_text_list.index(wrd)] = (wrd, key)
                                        
                                fields_df = pd.concat(
                                    [
                                        fields_df,
                                        pd.DataFrame(
                                            {
                                                "Field": key,
                                                "Value": ', '.join(value)
                                            }
                                            , index=[0]
                                        )
                                    ]
                                )
                            else:
                                for wrd in str(value).split():
                                    if wrd in annotated_text_list:
                                        annotated_text_list[annotated_text_list.index(wrd)] = (wrd, key)
                                    
                                fields_df = pd.concat(
                                    [
                                        fields_df,
                                        pd.DataFrame(
                                            {
                                                "Field": key,
                                                "Value": value
                                            }
                                            , index=[0]
                                        )
                                    ]
                                )

                if doc_pages[data_page_no-1]["document_category"]["category"] in document_mapper["addtional_table"] and document_mapper["addtional_table"][
                    doc_pages[data_page_no-1]["document_category"]["category"]
                    ] in doc_pages[data_page_no-1]["fields"]['tags']:
                    
                    additional_df = pd.DataFrame(doc_pages[data_page_no-1]["fields"]['tags'][document_mapper["addtional_table"][doc_pages[data_page_no-1]["document_category"]["category"]]])

                    for item in doc_pages[data_page_no-1]["fields"]['tags'][
                        document_mapper["addtional_table"][
                            doc_pages[data_page_no-1]["document_category"]["category"]
                            ]
                        ]:
                        
                        for key, value in item.items():
                            for wrd in str(value).split():
                                if wrd in annotated_text_list:
                                    annotated_text_list[annotated_text_list.index(wrd)] = (wrd, key)
                        
                    additional_df = pd.DataFrame(doc_pages[data_page_no-1]["fields"]['tags'][
                        document_mapper["addtional_table"][doc_pages
                                                           [data_page_no-1]["document_category"]["category"]
                                                        ]
                        ])

                data_viewer_col1, data_viewer_col2 = st.columns(2)

                with data_viewer_col1:
                    if view_image:
                        st.write("##### Original Page")
                        st.image(doc_pages[data_page_no-1]["file_url"].replace(' ', '%20').replace('â€¯', '%E2%80%AF'), caption="Processed Page", use_column_width=True)

                for i in range(len(annotated_text_list)):
                    if type(annotated_text_list[i]) == tuple:
                        annotated_text_list[i] = ('  ' + annotated_text_list[i][0] + '  ', annotated_text_list[i][1])
                    else:
                        annotated_text_list[i] = ('  ' + annotated_text_list[i] + '  ')

                if view_raw_text:
                    with st.expander("View Document Text", expanded=False):
                        st.write("##### Document Text")
                        annotated_text(annotated_text_list)

                with data_viewer_col2:
                    if view_data:
                        
                        st.write("##### Document Data")
                        if "fields" in doc_pages[data_page_no-1] and "tags" in doc_pages[data_page_no-1]["fields"] and doc_pages[data_page_no-1]["fields"]["tags"]:
                            st.data_editor(fields_df, hide_index=True, use_container_width=True)
                        else:
                            st.warning(
                                """No data available for the selected document category""",
                                icon="⚠️",
                            )

                        if doc_pages[data_page_no-1]["document_category"]["category"] in document_mapper["addtional_table"]:
                            st.write("##### " + document_mapper["addtional_table"]
                                        [doc_pages[data_page_no-1]["document_category"]["category"]])
                            st.data_editor(additional_df, hide_index=True, use_container_width=True)

            else:
                st.warning(
                    """No data available for the selected document category""",
                    icon="⚠️",
                )
                
    
    elif selected_page == "Provider Data":
        st.markdown("##### Provider Locations")

        response = json.loads(open('./response.json', 'r').read())
        if response:   
        
            folium_map = folium.Map(location=[20, 77], zoom_start=4)
            
            provider_df = pd.DataFrame(columns=["Provider Name", "Latitude", "Longitude"])
            
            for map_index, obj in enumerate(response):
                if obj["document_category"]["category"] == "Invoice" and "address_details" in obj and "geoCode" in obj["address_details"]:
                    name = obj["fields"]["tags"]["provider_name"]
                    lat, long = obj["address_details"]["geoCode"]
                
                    provider_df = pd.concat(
                        [
                            provider_df,
                            pd.DataFrame(
                                {
                                    "Provider Name": name,
                                    "Latitude": lat,
                                    "Longitude": long
                                },
                                index=[map_index+1]
                            ),
                        ]
                    )

            for index, row in provider_df.iterrows():
                folium.Marker(
                    location=[row["Latitude"], row["Longitude"]],
                    popup=row["Provider Name"],
                    icon=folium.Icon(color="green", icon="info-sign"),
                ).add_to(folium_map)

            folium_static(folium_map)


if __name__ == "__main__":
    main()