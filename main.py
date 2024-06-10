import time
from concurrent.futures import ThreadPoolExecutor
import os
import itertools
import shutil

from PIL import Image


skin_path = r'.\lib\skins'


def zip_and_send():
    try:
        print(f'\nZipping files. Please Wait....')
        shutil.make_archive('complete_skins', 'zip', r'.\finals')
        print(f'\nSuccessfully zipped final images.')
    # Send to discord
    except Exception as err:
        print(f'An error has occurred while zipping: {err}')


def get_images() -> dict:
    image_dict = {}

    for part in os.listdir(skin_path):
        skins = os.path.join(skin_path, part)
        if os.path.isdir(skins):
            path = os.path.normpath(skins)
            image_dict[path.split(os.sep)[-1]] = os.listdir(skins)

    return image_dict


def data_check():
    print('Performing Data Check on Files...')

    # Create /finals directory if not exists
    if not os.path.exists(r'.\finals'):
        os.makedirs(r'.\finals')

    # Verify that the parts directories are not empty
    for part in os.listdir(skin_path):
        if not len(os.listdir(f'{skin_path}\\{part}')) > 0:
            exit(fr'{skin_path}\{part} directory is empty!')


def image_iterator(portions):
    tasks = []
    combinations = itertools.product(
        portions['base_skin'],
        portions['under'],
        portions['eyes'],
        portions['hair']
    )

    for b, x, x1, x2 in combinations:
        file_name = fr'.\final\{b[:-4]}_{x[:-4]}_{x1[:-4]}_{x2[:-4]}.png'
        if not os.path.exists(file_name):
            tasks.append((b, x, x1, x2))
        else:
            print(f'Skipping {b[:-4]}, {x[:-4]}, {x1[:-4]}, {x2[:-4]}')

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(build_skin, *task) for task in tasks]
        for future in futures:
            future.result()


def build_skin(b, x, x1, x2):
    try:
        base_path = r'.\lib\skins'
        final_path = r'.\finals'
        blank_image = Image.new('RGBA', (64, 64), (255, 255, 255, 0))

        # Part layers
        base_layer_image = Image.open(fr'{base_path}\base_skin\{b}').convert('RGBA')
        under_image = Image.open(fr'{base_path}\under\{x}').convert('RGBA')
        eyes_image = Image.open(fr'{base_path}\eyes\{x1}').convert('RGBA')
        hair_image = Image.open(fr'{base_path}\hair\{x2}').convert('RGBA')

        # Stitch Images
        initial_image = Image.alpha_composite(blank_image, base_layer_image)
        initial_image = Image.alpha_composite(initial_image, under_image)
        initial_image = Image.alpha_composite(initial_image, eyes_image)
        final_image = Image.alpha_composite(initial_image, hair_image)

        final_image.save(fr'{final_path}\{b[:-4]}_{x[:-4]}_{x1[:-4]}_{x2[:-4]}.png')
        print(f'Saved: {final_path}\\{b[:-4]}_{x[:-4]}_{x1[:-4]}_{x2[:-4]}.png')

    except Exception as e:
        print(f'Error: {e}')


if __name__ == '__main__':
    t1 = time.time()
    
    data_check()
    images = get_images()
    image_iterator(images)
    zip_and_send()

    length = time.time() - t1
    print(f'Finished! -- Operation took {int(length // 60)}:{int(length % 60):02} minutes')

