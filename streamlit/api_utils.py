import base64
import os
import random
import boto3
import openai
import requests
from dotenv import load_dotenv
from PIL import Image

load_dotenv()
openai.api_key = os.environ.get("OPEN_API_ACCESS_KEY")

def get_grammer_corrected_text(input_text):
  response = openai.Completion.create(
    model="gpt-3.5-turbo-instruct",
    prompt=f"Correct this to standard English:\n\n{input_text}",
    temperature=0,
    max_tokens=200,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0
  )

  # Extract the generated text from the API response
  grammer_corrected_text = response.choices[0].text
  return grammer_corrected_text


def keyword_generator(input_text):
  response = openai.Completion.create(
    model="gpt-3.5-turbo-instruct",
    prompt=f"Extract keywords from this text:\n\n{input_text}",
    temperature=0.5,
    max_tokens=200,
    top_p=1.0,
    frequency_penalty=0.8,
    presence_penalty=0.0
  )
  keywords = response.choices[0].text
  return keywords

def product_name_generator(product_description,adjectives):
  response = openai.Completion.create(
    model="gpt-3.5-turbo-instruct",
    prompt=f"Product description: {product_description}\nSeed words: {adjectives}\nProduct names:",
    temperature=0.8,
    max_tokens=60,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0
  )
  products_names = response.choices[0].text
  return products_names


def get_answers1():
  responses = []
  questions = ["Can you summarize what the speaker said?", "What was the main point of the conversation?", "Was there anything surprising or unexpected in the conversation?"]
  for q in questions:
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "system", "content": "You are filling out a questionnaire."},
        {"role": "user", "content": q}
      ]
    )
    answer = response.choices[0].text.strip()
    responses.append(answer)

  return responses


#-----------------------------------------------------------------------------------

# Define function to generate ad based on user input

def ad_from_product_description(target_audience,product_description):
  response = openai.Completion.create(
    model="gpt-3.5-turbo-instruct",
    prompt=f"Write a creative ad for the following product to run on Facebook aimed at {target_audience}:\n\nProduct: {product_description}",
    temperature=0.5,
    max_tokens=100,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0
  )
  ad = response.choices[0].text.strip()
  return ad
#-----------------------------------------------------------------------------------

# List of possible background types
backgrounds = ["white", "black", "gray", "blue", "red", "green", "yellow", "wooden", "marble", "brick"]

# List of possible lighting types
lighting = ["bright", "dim", "warm", "cool", "natural", "artificial"]

# List of possible object types
objects = ["plants", "books", "electronics", "decorative items", "furniture", "kitchenware"]

# List of possible angles
angles = ["front", "back", "side", "top", "bottom"]

# List of possible color schemes
colors = ["monochromatic", "analogous", "complementary", "triadic", "neutral", "pastel", "bright", "dark"]

# List of possible image sizes
sizes = ["small", "medium", "large", "extra-large"]

# List of possible resolutions
resolutions = ["low", "medium", "high"]


def random_background():
    """Return a random background type."""
    return random.choice(backgrounds)


def random_lighting():
    """Return a random lighting type."""
    return random.choice(lighting)


def random_number():
    """Return a random number of objects."""
    return random.randint(1, 5)


def random_objects():
    """Return a random object type."""
    return random.choice(objects)


def random_angle():
    """Return a random angle."""
    return random.choice(angles)


def random_color():
    """Return a random color scheme."""
    return random.choice(colors)


def random_size():
    """Return a random image size."""
    return random.choice(sizes)


def random_resolution():
    """Return a random image resolution."""
    return random.choice(resolutions)



def generate_image(product_description, chosen_title):
    try:
        # Generate the image using DALL·E
        response = openai.Image.create(
            prompt=f"Create an advertisement image of a product with the following description: {product_description}. "
                   f"The product should be placed on a {random_background()} background and should have a {random_lighting()} lighting. "
                   f"The image should also include {random_number()} {random_objects()} in the background to provide context. "
                   f"The product should be shown in {random_angle()} angle and should have a {random_color()} color scheme. "
                   f"The image should be {random_size()} in size and should have a {random_resolution()} resolution."
                   f"Do not include any text in advert image or include the exact {chosen_title}",
            n=1,
            size="1024x1024",
            response_format="url"
        )

        # Get the image URL from the API response
        image_url = response['data'][0]['url']

        # Download the image and save it to a file
        image_data = requests.get(image_url).content
        # Create directory if it doesn't exist
        if not os.path.exists('generated_images'):
            os.makedirs('generated_images')

        image_path = f"generated_images/{chosen_title}.png"
        with open(image_path, "wb") as f:
            f.write(image_data)

        # Open the image using PIL
        image = Image.open(image_path)

        # Return both the image and its path
        return image, image_path

    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return None, None

#---------------------------------


# # Define the HTML template with placeholders for the product title and description
# if st.button("generate_html"):
"""
take title, product description and image directory as inputs
and consumes html template from s3 bucket which can be modified if required
and adds our product details to it, then uploads to a dir inour s3 bucket
"""


def generate_html(chosen_title, ad_from_api, image_path):
    html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{chosen_title}</title>
        </head>
        <body>
            <h1>{chosen_title}</h1>
            <p>{ad_from_api}</p>
            <img src="{image_path}" alt="Product Image">
        </body>
        </html>
        """
    return html_content
#-----------------------------------------
def write_html_file(html_content, filename):
    # Write the HTML content to a new HTML file
    with open(filename, 'w') as file:
        file.write(html_content)

"""
gets .html file from s3 bucket and reads the content and create a hyper link to return 
"""
def download_html(chosen_title, bucket_name,folder,file_extension):
    # Download the HTML file from S3
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=f'{folder}/{chosen_title}.{file_extension}')
    html_contents = response['Body'].read().decode('utf-8')

    # Create a download link for the HTML file
    b64 = base64.b64encode(html_contents.encode()).decode()
    href = f'<a href="data:file/html;base64,{b64}" download="{chosen_title}.{file_extension}">Download file</a>'

    return href
#----------------------------------------------------------------------------
def send_file_to_s3(file_path, s3_bucket, s3_key):
    """
    Uploads a file to S3

    :param file_path: Path to the file to upload
    :param s3_bucket: Name of the S3 bucket to upload the file to
    :param s3_key: Key to use when storing the file in S3
    """
    with open(file_path, 'rb') as f:
        s3_object = s3_resource.Object(s3_bucket, s3_key)
        s3_object.upload_fileobj(f)
#-----------------------------------------------------------------------------------

# def get_my_s3_url(filename):
#     static_url = f"https://{bucket_name}.s3.amazonaws.com"
#     filename_alone = filename.split("/")[-1]
#     generated_url = f"{static_url}/generated_images/{filename}"
#     return generated_url
s3_client = boto3.client('s3',region_name = 'us-east-1',aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),aws_secret_access_key = os.environ.get('AWS_SECRET_KEY'))

def get_s3_object_url( object_name):
    s3 = boto3.client('s3')
    expiration = 3600  # Link expiration time in seconds (1 hour in this case)

    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': f"generated_images/{object_name}"},
        ExpiresIn=expiration
    )

    return url

#-----------------------------------------------------------------------------------

def read_html_template_from_s3(filename):
    file_key = f'template/{filename}.txt'

    response = s3.get_object(Bucket=bucket_name, Key=file_key)

    text = response['Body'].read().decode('utf-8')

    return text

#------------------------------------------------------------------------------------
def get_answers():
  responses = []
  questions = ["Can you summarize what the speaker said?",
               "What was the main point of the conversation?",
               "Was there anything surprising or unexpected in the conversation?"]

  # transcript = "Speaker 1: Hi, how are you?\nSpeaker 2: I'm good, thanks for asking. How about you?\nSpeaker 1: I'm doing well, thanks. So, what brings you here today?"
  transcript = "on the work, scraping on the data science, whatever you're web scraping for, you can focus on that. They have a success rate of average 99.2% and the residential proxies offer, as I said, 100 million plus legit IPs from 195 countries. You can also take a look at their quick start. You can use this with curl with a command line tool on Linux on Windows. You can use it for PHP and probably most interesting for you guys, you can use it with Python as well. You can look at the tutorial here to see how it's done. You can specify a server. You can also specify the country, the city. You can do all this manually and these are legitimate IP addresses, reliable service. The company is very reliable. If you go to Reddit and you look for best proxy server."
  for q in questions:
    response = openai.Completion.create(
      engine="text-davinci-002",
      prompt=f"{transcript}\nQ: {q}\nA:",
      max_tokens=1024,
      n=1,
      stop=None,
      temperature=0.7,
    )

    answer = response.choices[0].text.strip()
    responses.append(answer)

  return responses


#-----------------------------------------------------------------
"""
writing logs to cloudwatch
"""

## commented the loggin part as the s3 bucket is full at the last moment
def write_logs_to_cloudwatch(message: str, log_stream):
    # s3_logs.put_log_events(
    #     logGroupName = "model_as_a_service",
    #     logStreamName = log_stream,
    #     logEvents = [
    #         {
    #             'timestamp' : int(time.time() * 1e3),
    #             'message' : message
    #         }
    #     ]
    # )
    return


#------------------------------------------------------

# def transcribe_audio_file(ti):
#     audio_file_path = ti.xcom_pull(task_ids="get_latest_audio_file", key="file_path")
#     print(f'audio_file_path is {audio_file_path}')
#     sound = AudioSegment.from_file(audio_file_path)
#     split_time = 1 * 60 * 1000  # 1 minute to milliseconds
#     sound_parts = make_chunks(sound, split_time)
#     # text_file_path = f'/tmp/translated_text.txt'
#     text_file_path = f'{loc}translated_text.txt'
#     print(f'Output to be saved in : {text_file_path}')
#     with open(text_file_path, 'a+') as f:
#         for i, part in enumerate(sound_parts):
#             # file_name = f"/tmp/audio{i}.wav"
#             file_name = f"{loc}audio{i}.wav"
#             print(f'Splitting file : {file_name}')
#             part.export(file_name, format='wav')
#             model_id = 'whisper-1'
#             with open(file_name, 'rb') as audio_file:
#                 translation = openai.Audio.translate(
#                     api_key=openai.api_key,
#                     model=model_id,
#                     file=audio_file,
#                     response_format='text'
#                 )
#
#             # Save the translated and transcribed text to text file
#             f.write(translation)


            #-------------------
# def record_audio(filename, duration):
#     CHUNK = 1024
#     FORMAT = pyaudio.paInt16
#     CHANNELS = 1
#     RATE = 44100
#     p = pyaudio.PyAudio()
#
#     stream = p.open(format=FORMAT,
#                     channels=CHANNELS,
#                     rate=RATE,
#                     input=True,
#                     frames_per_buffer=CHUNK)
#
#     frames = []
#
#     for i in range(0, int(RATE / CHUNK * duration)):
#         data = stream.read(CHUNK)
#         frames.append(data)
#
#     stream.stop_stream()
#     stream.close()
#     p.terminate()
#
#     wf = wave.open(filename, 'wb')
#     wf.setnchannels(CHANNELS)
#     wf.setsampwidth(p.get_sample_size(FORMAT))
#     wf.setframerate(RATE)
#     wf.writeframes(b''.join(frames))
#     wf.close()
