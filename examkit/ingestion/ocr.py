"""
OCR utilities using Tesseract.
"""

import logging
from pathlib import Path

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


def extract_text_with_ocr(image_path: Path, logger: logging.Logger) -> str:
    """
    Extracts text from the image at the given path using Tesseract OCR.
    
    Returns:
        Extracted text from the image, or an empty string if Tesseract is unavailable or OCR fails.
    """
    if not TESSERACT_AVAILABLE:
        logger.warning("Tesseract not available, OCR skipped")
        return ""

    try:
        # Open image
        image = Image.open(image_path)

        # Run OCR
        text = pytesseract.image_to_string(image)

        logger.debug(f"OCR extracted {len(text)} characters from {image_path.name}")
        return text

    except Exception as e:
        logger.error(f"OCR failed for {image_path}: {e}")
        return ""


def get_ocr_confidence(image_path: Path, logger: logging.Logger) -> float:
    """
    Compute the average OCR confidence for the given image.
    
    Parameters:
        image_path (Path): Path to the image file to analyze.
    
    Returns:
        float: Average confidence score between 0 and 100. Returns 0.0 if OCR is unavailable, no valid confidences are found, or an error occurs.
    """
    if not TESSERACT_AVAILABLE:
        return 0.0

    try:
        image = Image.open(image_path)
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

        # Calculate average confidence
        confidences = [int(conf) for conf in data['conf'] if conf != '-1']
        if confidences:
            return sum(confidences) / len(confidences)
        return 0.0

    except Exception as e:
        logger.error(f"Failed to get OCR confidence for {image_path}: {e}")
        return 0.0


def preprocess_image_for_ocr(image_path: Path, output_path: Path) -> Path:
    """
    Prepare an image for OCR by converting it to grayscale, boosting contrast, and applying sharpening.
    
    If TESSERACT_AVAILABLE is False, the function returns the original input path without modifying or creating a file.
    
    Parameters:
        image_path (Path): Path to the input image file.
        output_path (Path): Destination path for the preprocessed image.
    
    Returns:
        Path: Path to the preprocessed image, or the original `image_path` if OCR is unavailable.
    """
    if not TESSERACT_AVAILABLE:
        return image_path

    from PIL import ImageEnhance, ImageFilter

    # Open and convert to grayscale
    image = Image.open(image_path).convert('L')

    # Enhance contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)

    # Sharpen
    image = image.filter(ImageFilter.SHARPEN)

    # Save preprocessed image
    image.save(output_path)
    return output_path