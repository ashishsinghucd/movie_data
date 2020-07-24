import argparse
from datetime import datetime
import os

import requests
from configobj import ConfigObj
import pandas as pd
OMDB_API = "http://www.omdbapi.com/?i={imdb_movie_id}&apikey={api_key}"
MOVIE_DATA = []
"""
Download algo
year - should be greater than 1990
save the image_names as imdb_title.jpg
save the other info as csv file
"""


def send_request(imdb_id, threshold_year=1990):
    omdb_formatted_api = OMDB_API.format(imdb_movie_id=imdb_id, api_key=api_key)
    response = requests.get(omdb_formatted_api)
    response_json = response.json()
    if response.status_code != 200:
        print("Request failed with reponse: ", response_json)
        return
    MOVIE_DATA.append(response_json)
    year = int(response_json["Year"])
    if year < threshold_year:
        return
    image_url = response_json["Poster"]
    image_response = requests.get(image_url)

    filename = imdb_id + ".jpg"
    if image_response.status_code == 200:
        with open(movie_images_save_path + "/" + filename, 'wb') as f:
            f.write(image_response.content)


def iterate_movie_id(filepath):
    movie_id_df = pd.read_csv(filepath, dtype=str)
    movie_id_list = movie_id_df["imdbId"].tolist()
    movie_id_list = list(set(movie_id_list))
    print("Total unique movies id are: ", len(movie_id_list))
    # Daily requests are limited to 1000
    count = 950
    downloaded_files = 0
    for imdb_id in movie_id_list:
        if not count:
            return
        try:
            imdb_id = "tt" + imdb_id
            send_request(imdb_id)
        except Exception as e:
            print("Error downloading the data for movie: ", imdb_id, str(e))
        downloaded_files += 1
        if not downloaded_files % 100:
            print("Downloaded {} movies info".format(downloaded_files))
        count -= 1
    print("Downloaded {} movies info".format(downloaded_files))
    file_name = datetime.now().strftime("%Y-%m-%d")
    movie_data_df = pd.DataFrame(MOVIE_DATA)
    movie_data_df.to_csv(movie_data_save_path + "/" + file_name + ".csv", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="path of the api configs file")
    args = parser.parse_args()
    config = ConfigObj(args.config)
    api_key = config["API_KEY"]
    movie_id_path = config["MOVIE_ID_PATH"]
    output_path = config["OUTPUT_PATH"]
    movie_folder = "movie_details"
    movie_images_folder = "movie_images"
    movie_data_save_path = os.path.join(output_path, movie_folder)
    movie_images_save_path = os.path.join(output_path, movie_images_folder)
    if not os.path.exists(movie_data_save_path):
        os.makedirs(movie_data_save_path)
    if not os.path.exists(movie_images_save_path):
        os.makedirs(movie_images_save_path)
    iterate_movie_id(movie_id_path)
