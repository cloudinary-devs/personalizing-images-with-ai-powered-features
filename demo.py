from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template
import cloudinary
from cloudinary import uploader, api

import os

app = Flask(__name__, static_url_path='/static')

@app.route("/", methods=['GET'])
def index():
    '''
    # Create the upload preset only once:
    cloudinary.api.create_upload_preset(
        name = "docs_computer_vision_demo",
        unsigned = True,  
        use_filename=True,
        tags="computer_vision_demo",
        colors= True,
        faces= True,
        categorization = "google_tagging", auto_tagging = 0.7,
        ocr = "adv_ocr",
        moderation = "aws_rek"
    )  


    # Upload overlays only once:  
    cloudinary.uploader.upload("https://res.cloudinary.com/demo/image/upload/v1572554533/iphone.png", public_id='iphone', unique_filename = False, overwrite=True)
    cloudinary.uploader.upload("https://res.cloudinary.com/demo/image/upload/v1532000565/sunglasses_emoji.png", public_id='sunglasses_emoji', unique_filename = False, overwrite=True) 
    '''
    
    cloudinary.api.delete_resources_by_tag("computer_vision_demo") 
    return render_template('index.html', failed_upload='')

@app.route("/output", methods=['POST'])
def output():
    assetList = cloudinary.api.resources_by_tag("computer_vision_demo")

    urls = []
    transformations = []
    messages = []
    titles = []
    identity = None
    identities = []
    for asset in assetList['resources']:
        public_id = asset["public_id"]
        details = cloudinary.api.resource(public_id, faces=True, colors=True)
        
        if details["moderation"][0]["status"] == "approved":
            public_ids=[]
            public_ids.append(public_id)
            print(public_id)
            url = details["secure_url"]
            urls.append(url)

            title = ' / '.join(data['tag'] for data in details["info"]["categorization"]["google_tagging"]["data"][:3])
            titles.append(title)

            message = ""
            message += f"This picture contains the phrase '{details['info']['ocr']['adv_ocr']['data'][0]['textAnnotations'][0]['description']}'." if "textAnnotations" in details["info"]["ocr"]["adv_ocr"]["data"][0] else "There aren't any words in this picture."
            message += "\n"

            faces = len(details["faces"])
            if faces == 0:
                message += "There aren't any faces in this picture."
            elif faces == 1:
                coordinates = ', '.join(str(coord) for coord in details["faces"][0])
                message += f"There is one face in this picture with coordinates: {coordinates}"
            else:
                message += f"There are {faces} faces in this picture with coordinates:\n"
                for coordinates in details["faces"]:
                    message += ', '.join(str(coord) for coord in coordinates) + '\n'

            message += "\n"
            message += f"The orientation is {'Landscape' if details['width'] / details['height'] > 1 else 'Portrait'}.\n\n"

            color1, color2 = details["colors"][0][0], details["colors"][1][0]
            message += f"The predominant colors are {color1} and {color2}."

            tcolor = '35px_solid_rgb:'+color2.replace("#", "")

            transformation = cloudinary.CloudinaryImage(details["public_id"]).build_url(transformation=[
                {'width': 600, 'height': 600, 'background': 'gen_fill:ignore-foreground_true', 'crop': 'pad'},
                {'overlay': 'sunglasses_emoji', 'width': 0.6, 'region_relative': True, 'gravity': 'faces', 'flags': 'layer_apply'},
                {'border': tcolor},
                {'quality': 'auto', 'fetch_format': 'auto'}
            ])
            transformations.append(transformation)
  
            messages.append(message)
            
            identity = None
            for x in details["info"]["categorization"]["google_tagging"]["data"]:
              if 'face' in x['tag'] or 'head' in x['tag'] or 'shirt' in x['tag'] or 'sweater' in x['tag'] or 'shoulder' in x['tag'] or 'sleeve' in x['tag'] or 'Face' in x['tag'] or 'Head' in x['tag'] or 'Shirt' in x['tag'] or 'Sweater' in x['tag'] or 'Shoulder' in x['tag'] or 'Sleeve' in x['tag']:
                identity = 1
                break
              elif 'shoe' in x['tag'] or 'boot' in x['tag'] or 'footwear' in x['tag'] or 'leg' in x['tag'] or 'Shoe' in x['tag'] or 'Boot' in x['tag'] or 'Footwear' in x['tag'] or 'Leg' in x['tag']:
                identity = 2   
                break
            identities.append(identity)
    return render_template('output.html', public_ids=public_ids, identities=identities, num=len(urls), urls=urls, titles=titles, transformations=transformations, messages=messages)

if __name__ == "__main__":
    app.run()
