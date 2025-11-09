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
    Extract text from image using Tesseract OCR.

    Args:
        image_path: Path to image file.
        logger: Logger instance.

    Returns:
        Extracted text.
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
    Get OCR confidence score for an image.

    Args:
        image_path: Path to image file.
        logger: Logger instance.

    Returns:
        Confidence score (0-100).
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
    Preprocess image to improve OCR accuracy.

    Args:
        image_path: Path to input image.
        output_path: Path for preprocessed image.

    Returns:
        Path to preprocessed image.
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
