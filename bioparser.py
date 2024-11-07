import os
from typing import List

import fitz
from pymupdf import Rect, Page
import logging

# Пожалуйста, не убирайте r
SOURCE_PATH = r"C:\Users\Dubok\Downloads\Lektsia_1_2024_Virusologia.pdf"
OUTPUT_DIR = r""

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pivo")


def find_suitable_rects(page: Page) -> List[Rect]:
    """
    Функция поиска прямоугольников указывающих на новые страницы.

    :param page: Объект страницы, представляющий страницу, на которой выполняется поиск прямоугольников.
    :type page: Page
    :return: Список, содержащий максимальную высоту, максимальную ширину и список прямоугольников.
    :rtype: List[Rect]
    """
    page_drawings = page.get_drawings()
    maxw, maxh = 0, 0
    rects = []
    for page_drawing in page_drawings:
        for item in page_drawing["items"]:
            if (
                isinstance(item[1], Rect)
                and item[0] == "re"
                and page_drawing["color"] == (0, 0, 0)
            ):
                rect = item[1]
                if rect.width - maxw > 2 and rect.height - maxh > 2:
                    maxw = rect.width
                    maxh = rect.height
                    rects = [rect]
                elif -0.5 < rect.width - maxw < 0.5 and -0.5 < rect.height - maxh < 0.5:
                    rects.append(rect)
        logger.debug(f"Найдено {len(rects)} прямоугольников.")

    return rects

def main(pdf_path: str, output_dir: str) -> None:
    """
    Главная функция для обработки PDF файла, извлечения блоков внутри прямоугольников
    и сохранения их на новых страницах в новый PDF файл.

    :param pdf_path: Путь к исходному PDF файлу.
    :type pdf_path: str
    :param output_dir: Директория для сохранения итогового PDF.
    :type output_dir: str
    """
    logger.info(f"Открытие исходного PDF файла: {pdf_path}")

    doc = fitz.open(pdf_path)
    new_pdf = fitz.open()

    if output_dir.strip() == "":
        logger.warning(
            f"Сохранение в текущую директорию."
        )
        output_dir = "./"
    elif not os.path.exists(output_dir):
        logger.warning(
            f"Директория {output_dir} не существует, будет использована текущая директория."
        )
        output_dir = "./"

    for page_num, page in enumerate(doc.pages()):
        logger.info(f"Обрабатываем страницу {page_num + 1}")
        process_page(doc, new_pdf, page, page_num)

    output_file = os.path.join(output_dir, f"block.pdf")
    new_pdf.save(output_file, garbage=1)
    new_pdf.close()
    doc.close()

    logger.info(
        f"Все блоки внутри прямоугольников успешно сохранены как отдельные страницы в {output_file}"
    )

def process_page(
    doc: fitz.open, new_pdf: fitz.open, page: Page, page_num: int
) -> None:
    """
    Обрабатывает страницу, находит прямоугольники и копирует содержимое
    внутри каждого прямоугольника в новый PDF документ.

    :param doc: Исходный PDF документ.
    :type doc: Document
    :param new_pdf: Новый PDF документ, в который будут добавляться страницы.
    :type new_pdf: Document
    :param page: Страница из исходного PDF документа.
    :type page: Page
    :param page_num: Номер страницы в исходном PDF.
    :type page_num: int
    """
    rects = find_suitable_rects(page)

    for rect in rects:
        new_page = new_pdf.new_page(width=rect.width, height=rect.height)
        logger.debug(f"Добавляем страницу с прямоугольником: {rect}")
        new_page.show_pdf_page(
            Rect(0, 0, rect.width, rect.height), doc, page_num, clip=rect
        )

if __name__ == "__main__":
    main(SOURCE_PATH, OUTPUT_DIR)
