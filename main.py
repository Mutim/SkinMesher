from concurrent.futures import ThreadPoolExecutor
import os
import itertools
import shutil

from PIL import Image


skin_path = r'lib\skins'


def zip_and_send():
    shutil.make_archive('base_pieces', 'zip', '\\lib\\skins')
    # Send to discord


def get_images() -> dict:
    image_dict = {}

    for part in os.listdir(skin_path):
        skins = os.path.join(skin_path, part)
        if os.path.isdir(skins):
            image_dict[skins.split('\\')[-1]] = os.listdir(skins)

    return image_dict


def data_check():
    print('Performing Data Check on Files...')
    for part in os.listdir(skin_path):
        if not len(os.listdir(f'{skin_path}\\{part}')) > 0:
            exit(f'{skin_path}\\{part} directory is empty!')


def image_iterator(portions):
    tasks = []
    combinations = itertools.product(
        portions['base_skin'],
        portions['lower_body'],
        portions['upper_body'],
        portions['eyes'],
        portions['hair']
    )

    for b, x, x1, x2, x3 in combinations:
        file_name = fr'.\final\{b[:-4]}_{x[:-4]}_{x1[:-4]}_{x2[:-4]}_{x3[:-4]}.png'
        if not os.path.exists(file_name):
            tasks.append((b, x, x1, x2, x3))
        else:
            print(f'Skipping {b[:-4]}, {x[:-4]}, {x1[:-4]}, {x2[:-4]}, {x3[:-4]}')

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(build_skin, *task) for task in tasks]
        for future in futures:
            future.result()


def build_skin(b, x, x1, x2, x3):
    try:
        base_path = r'.\\lib\\skins'
        final_path = r'.\\finals'
        blank_image = Image.new('RGBA', (64, 64), (255, 255, 255, 0))

        # Part layers
        base_layer_image = Image.open(f'{base_path}\\base_skin\\{b}').convert('RGBA')
        lower_body_image = Image.open(f'{base_path}\\lower_body\\{x}').convert('RGBA')
        upper_body_image = Image.open(f'{base_path}\\upper_body\\{x1}').convert('RGBA')
        eyes_image = Image.open(f'{base_path}\\eyes\\{x2}').convert('RGBA')
        hair_image = Image.open(f'{base_path}\\hair\\{x3}').convert('RGBA')

        # Stitch Images
        initial_image = Image.alpha_composite(blank_image, base_layer_image)
        initial_image = Image.alpha_composite(initial_image, lower_body_image)
        initial_image = Image.alpha_composite(initial_image, upper_body_image)
        initial_image = Image.alpha_composite(initial_image, eyes_image)
        final_image = Image.alpha_composite(initial_image, hair_image)

        final_image.save(f'{final_path}\\{b[:-4]}_{x[:-4]}_{x1[:-4]}_{x2[:-4]}_{x3[:-4]}.png')
        print(f'Saved: {final_path}\\{b[:-4]}_{x[:-4]}_{x1[:-4]}_{x2[:-4]}_{x3[:-4]}.png')

    except Exception as e:
        print(f'Error: {e}')


if __name__ == '__main__':
    # Create /finals directory if not exists
    if not os.path.exists(r'.\finals'):
        os.makedirs(r'.\finals')

    zip_and_send()
    data_check()

    images = get_images()
    image_iterator(images)

