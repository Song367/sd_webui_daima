import datetime
import json
from io import BytesIO

import requests

import base64
from PIL import Image

ip = "127.0.0.1"

port = 7861


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
        base64_data = base64.b64encode(image_data).decode("utf-8")
        return base64_data


def save_base64_image(base64_data, output_path):
    image_data = base64.b64decode(base64_data)
    image = Image.open(BytesIO(image_data))
    image.save(output_path)


import os


def list_files_in_directory(directory_path):
    file_list = []
    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)
        if os.path.isfile(item_path):
            file_list.append(item_path)
    return file_list


if __name__ == "__main__":
    # target_directory = r"outputs/txt2img-images/2023-08-15"  # 替换为你的目标目录路径
    # output_directory = r"outputs/new_output"
    target_directory = input("请输入图片所在目录: ")  # 替换为你的目标目录路径
    output_directory = input("请指定图片保存目录: ")
    steps = input("迭代次数 默认25: ").replace(" ", "")
    width = input("生成图片的宽度 默认512: ").replace(" ", "")
    height = input("生成图片的高度 默认512: ").replace(" ", "")

    files = list_files_in_directory(target_directory)
    for file in files:
        print(file)
        # path = target_directory + "/" + file

        url = f"http://{ip}:{port}/sdapi/v1/interrogate"

        data = {
            "image": image_to_base64(file)
        }
        res = requests.post(url, json=data)
        if res:
            info = json.loads(res.content)

            print(info["caption"])

            txt2Img = {
                "prompt": info["caption"],
                "steps": int(steps) if steps != "" else 25,
                "width": int(width) if width != "" else 512,
                "height": int(height) if height != "" else 512
            }
            timg_res = requests.post(f"http://{ip}:{port}/sdapi/v1/txt2img", json=txt2Img)
            if timg_res:
                two_info = json.loads(timg_res.content)
                if len(info["caption"]) > 50:
                    info["caption"] = info["caption"][:50]
                filename = info["caption"].replace(" ", "_").replace(",", "_") + datetime.datetime.now().strftime(
                    "%H_%M_%S") + ".png"
                new_directory = output_directory + "/" + filename
                for i in two_info["images"]:
                    save_base64_image(i, output_path=new_directory)
