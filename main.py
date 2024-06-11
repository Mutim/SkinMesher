import time
import os
import itertools
import shutil
from concurrent.futures import ThreadPoolExecutor
from PIL import Image


def zip_and_send(finals_path):
    try:
        print(f'\nZipping files. Please Wait....')
        shutil.make_archive('complete_skins', 'zip', finals_path)
        print(f'\nSuccessfully zipped final images.')
    except Exception as err:
        print(f'An error has occurred while zipping: {err}')


def get_images(skin_path):
    image_dict = {}
    for part in os.listdir(skin_path):
        skins = os.path.join(skin_path, part)
        if os.path.isdir(skins):
            image_dict[part] = os.listdir(skins)
    return image_dict


def data_check(skin_path, finals_path):
    print('Performing Data Check on Files...')
    # Create /finals directory if not exists
    if not os.path.exists(finals_path):
        print(f'Finals Directory ( {finals_path} ) not found! Generating directory now....')
        os.makedirs(finals_path)
    # Verify that the parts directories are not empty
    for part in os.listdir(skin_path):
        part_path = os.path.join(skin_path, part)
        if not os.listdir(part_path):
            exit(f'{part_path} directory is empty!')


def image_iterator(skin_path, finals_path, portions):
    tasks = []
    combinations = itertools.product(
        portions['base_skin'],
        portions['under'],
        portions['eyes'],
        portions['hair']
    )
    for b, x, x1, x2 in combinations:
        file_name = os.path.join(finals_path, f"{b[:-4]}_{x[:-4]}_{x1[:-4]}_{x2[:-4]}.png")
        if not os.path.exists(file_name):
            tasks.append((b, x, x1, x2))
        else:
            print(f'Skipping {b[:-4]}, {x[:-4]}, {x1[:-4]}, {x2[:-4]}')
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(build_skin, skin_path, finals_path, *task) for task in tasks]
        for future in futures:
            future.result()


def build_skin(skin_path, finals_path, b, x, x1, x2):
    try:
        blank_image = Image.new('RGBA', (64, 64), (255, 255, 255, 0))
        # Part layers
        base_layer_image = Image.open(os.path.join(skin_path, 'base_skin', b)).convert('RGBA')
        under_image = Image.open(os.path.join(skin_path, 'under', x)).convert('RGBA')
        eyes_image = Image.open(os.path.join(skin_path, 'eyes', x1)).convert('RGBA')
        hair_image = Image.open(os.path.join(skin_path, 'hair', x2)).convert('RGBA')

        # Stitch Images
        initial_image = Image.alpha_composite(blank_image, base_layer_image)
        initial_image = Image.alpha_composite(initial_image, under_image)
        initial_image = Image.alpha_composite(initial_image, eyes_image)
        final_image = Image.alpha_composite(initial_image, hair_image)

        # Save the final image
        file_name = f"{b[:-4]}_{x[:-4]}_{x1[:-4]}_{x2[:-4]}.png"
        final_image.save(os.path.join(finals_path, file_name))
        print(f'Saved: {os.path.join(finals_path, file_name)}')
    except Exception as e:
        print(f'Error: {e}')


if __name__ == '__main__':
    t1 = time.time()
    main_directory = os.getcwd()
    skin_directory = os.path.join(main_directory, 'lib', 'skins')
    finals_directory = os.path.join(main_directory, 'finals')

    data_check(skin_directory, finals_directory)
    images = get_images(skin_directory)
    image_iterator(skin_directory, finals_directory, images)
    zip_and_send(finals_directory)
    length = time.time() - t1
    print(f'Finished! -- Operation took {int(length // 60)}:{int(length % 60):02} minutes')
