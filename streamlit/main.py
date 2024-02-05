import json

import streamlit as st
import base64
import requests
from streamlit_lottie import st_lottie
# from streamlit import SessionState
import os
import streamlit as st
# import whisper_client as wc
# import pyaudio
import wave
# import whisper_client

# wc = whisper_client.Client()

from api_utils import get_grammer_corrected_text, product_name_generator, \
    ad_from_product_description, generate_image, get_s3_object_url, generate_html, read_html_template_from_s3, \
    download_html, write_logs_to_cloudwatch, write_html_file

bucket_name = os.environ.get("SOURCE_BUCKET")





with open('config.json', 'r') as f:
    config = json.load(f)
image_dir = config['dir']['image']
if 'image' not in st.session_state:
    st.session_state.image = None
if "ad" not in st.session_state:
    st.session_state.ad = None
if "image_path" not in st.session_state:
    st.session_state.image_path = None

def load_lottiefile(filepath:str):
    with open(filepath,"r") as f:
        return json.load(f)
def load_lottieurl(url:str):
    r = requests.get(url)
    if r.status_code !=200:
        return None
    return r.json()

# audio_product_desc = ""
def main():

    # global audio_product_desc
    # st.markdown(
    #         "<h3 style='text-align: center'><span style='color: #2A76BE;'>AdVantage</span></h3>",
    #         unsafe_allow_html=True)
    #
    # # Create a button to record audio
    # if st.button("Record Audio"):
    #     # Record audio for 5 seconds
    #     record_audio("recording.wav", 5)
    #     st.success("Audio recorded successfully!")
    #
    #     # Transcribe audio using Whisper API
    #     audio_file = open("recording.wav", "rb")
    #     response = wc.transcribe(audio_file, "en-US")
    #     audio_product_desc = response["transcription"]
    product_description = st.text_input("product_description")
    dec,img = st.columns([2,1])
    # if audio_product_desc is not None:
    #     product_description = audio_product_desc
    with dec:
        grammer_corrected_description = get_grammer_corrected_text(product_description)
        adjective = st.text_input("Describe your product in a word or two separated by comma ','")



        if st.button("Get Product Name!"):
            write_logs_to_cloudwatch(f"product description: {product_description}",
                                     "advantage_logs")
            # st.markdown(f"{grammer_corrected_description}-------corrected")
            generated_product_name = product_name_generator(grammer_corrected_description,adjective)
            st.markdown(f"{generated_product_name}")
        target_customer = st.text_input("Who is your target customer")
        write_logs_to_cloudwatch(f"Target Customer: {target_customer}",
                                 "advantage_logs")


        # Add a button to generate the ad
        if st.button("Get Ad!"):
            ad_from_product_desc = ad_from_product_description(target_customer,grammer_corrected_description)

            st.session_state.ad = ad_from_product_desc
            # st.markdown(f"{grammer_corrected_description} ------> grammer corrected")
            write_logs_to_cloudwatch(f"Generated Add: {ad_from_product_desc}",
                                     "advantage_logs")
            with st.expander("Ad"):
                st.write(f"{ad_from_product_desc}")

    with img:
        lottie_audio = load_lottieurl("https://assets10.lottiefiles.com/private_files/lf30_i0cTdc.json")
        st_lottie(
            lottie_audio,
            speed=1,
            reverse=False,
            loop=True,
            height="450px",
            width=None,
            key=None,
        )
    st.markdown("---------------------------------------------------------------------------------------------------------")

    # Add button to generate image
    chosen_title = st.text_input("Choose a title")

    button_clicked = st.button("Generate Image")

    # If button is clicked, generate and display image
    if button_clicked:
        # Display spinner while image is being generated
        with st.spinner("Generating image..."):
            advert_image,image_path = generate_image(grammer_corrected_description,chosen_title)
            st.session_state.image_path = image_path

            # st.session_state.image_path = f"/Users/bhargavi/PycharmProjects/StreamAdvertise-GPT-Powered-Small-Business-Promotion/streamlit/{image_path}"

        # If image is generated successfully, display it
        if advert_image is not None:
            st.image(advert_image, caption='Advertisement Image', use_column_width=True)
            st.session_state.image = advert_image


        # If image generation fails, display error message
        else:
            st.error("Failed to generate image")



    # col1,col2 = st.columns([1,1])
    # with col1:
    #     if st.button("Generate link to download image"):
    #         if st.session_state.image is not None:  # check if an image has been generated
    #             st.image(st.session_state.image, caption='Advertisement Image', use_column_width=True)
    #         url = get_s3_object_url(f"{chosen_title}.png")
    #         with st.expander("Expand for url"):
    #             st.write(url)
        # html_content = generate_html(chosen_title, product_description, image_dir)
        # with open(f"templates/{chosen_title}.html", "w") as f:
        #     # Write some HTML content to the file
        #     f.write(html_content)
    # with col2:
    st.markdown("---------------------------------------------------------------------------------------------------------")
    st.markdown(
        "<h3 style='text-align: center'><span style='color: #2A76BE;'>Get started with a website for your product</span></h3>",
        unsafe_allow_html=True)
    lottie_audio = load_lottieurl("https://assets6.lottiefiles.com/packages/lf20_hi95bvmx/WebdesignBg.json")
    st_lottie(
        lottie_audio,
        speed=1,
        reverse=False,
        loop=True,
        height="450px",
        width=None,
        key=None,
    )
    st.markdown(st.session_state.image_path)

    c1,c2,c3 = st.columns([1,1,1])
    with c1:

        if st.button('Download my website'):
            html_content = generate_html(chosen_title, st.session_state.ad, st.session_state.image_path)
            # st.markdown(html_content)
            html_filename = f"{chosen_title}.html"
            write_html_file(html_content, html_filename)
            with open(html_filename, 'rb') as file:
                html_bytes = file.read()
            st.download_button(label='Download HTML file', data=html_bytes, file_name='generated_html.html',
                               mime='text/html')

    with c3:
        if st.button('Download HTML Code'):
            href = download_html(chosen_title, bucket_name, "generated_html_code", "txt")
            write_logs_to_cloudwatch(f"THtml code generated for {product_description}",
                                     "advantage_logs")

            st.markdown(href, unsafe_allow_html=True)
    #
    # if st.button("Get html code from api"):
    #     image_url = get_s3_object_url(f"{chosen_title}.png")
    #     # image_url = f"generated_images/{chosen_title}.png"
    #     st.markdown(f"{image_url} ------> image url")
    #     st.markdown(f'{chosen_title.replace("_"," ")} ------> title')
    #     st.markdown(f"{grammer_corrected_description} ------> grammar corrected")
    #
    #     code = generate_html(image_url,chosen_title.replace("_"," "),grammer_corrected_description)
    #     st.markdown(code)


if __name__ == "__main__":
    main()