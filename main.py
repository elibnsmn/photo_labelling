# By: Eli Bensimon

import base64  # used for encoding image data
import json  # used for final output formatting
import os  # used to navigate through operating system directories (to find the images)

from openai import OpenAI  # used for, well, OpenAI

image_folder = "images"
results = {}  # Dictionary to store final results
output_file = "image_labels.json"  # Output file (which will be automatically created if non-existent when writing is attempted)
client = OpenAI()

prompt = "Provide a valid JSON output. Please tell me whether the photo captures a restaurant menu, receipt, or something similar that contains a dish name. If so, please also list all the dish names in the photo using English. The output should be in dictionary format {“menu_photo”: “yes”/”no”, “receipt_photo”: “yes”/”no”, “dish_names”: [dishname1, dishname2, …] } and saved in JSON file"


# Taken directly from OpenAI documentation - encoding images in base64 so they are "readable"
def encode_image(image_path):
    with open(f"{image_folder}/{image_path}", "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# Formatting the query for each image (used as a function, as there are multiple images to analyze)
def query(b64_image, filename):

    # Creating a response
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},  # Specifying a JSON output
        messages=[
            {
                "role": "user",
                # The content for this query has multiple parts (2), as both an image and text prompt is being sent - hence the "type" differentiatior
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"},
                    },
                ],
            }
        ],
    )

    result = response.choices[0].message.content
    # print(result)

    # Creating a new dictionary entry with the <Key, Value> pair as <Image filename, Queried response>
    results[filename] = result

    try:
        parsed_result = json.loads(result)  # Convert JSON string to dictionary
        results[filename] = parsed_result  # Store the dictionary instead of string
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON for {filename}: {e}")
        results[filename] = {"error": "Invalid JSON response"}

    # print(json.dumps(parsed_result, indent=4))


for filename in os.listdir(image_folder):
    if filename.endswith(
        ".jpg"
    ):  # Can specify more file extensions as well, I just chose to use solely .jpg as all test images were .jpg
        try:
            base64_image = encode_image(filename)  # Encode image in base64
            query(base64_image, filename)
        except Exception as e:
            print(f"Error processing {filename}\nError:{e}")


# Dumping the dictionary of results into the output file (which is created if non-existent)
with open(output_file, "w") as f:
    json.dump(results, f, indent=4)
