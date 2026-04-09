from background_task import background
from .models import CaseImage
from PIL import Image
from django.core.files.base import ContentFile
import io

@background(schedule=1)
def compress_case_image(case_image_id):
    """
    مهمة خلفية لضغط صورة حالة.
    """
    try:
        case_image = CaseImage.objects.get(id=case_image_id)
        
        original_image = Image.open(case_image.image)
        
        if original_image.mode in ("RGBA", "P"):
            original_image = original_image.convert("RGB")

        original_image.thumbnail((800, 800))
        
        thumb_io = io.BytesIO()
        original_image.save(thumb_io, 'JPEG', quality=70) 
        
        compressed_file = ContentFile(thumb_io.getvalue(), name=case_image.image.name)
        
        case_image.compressed_image = compressed_file
        case_image.save()
        
        print(f"Successfully compressed image for CaseImage {case_image_id}")

    except CaseImage.DoesNotExist:
        print(f"CaseImage with id {case_image_id} not found.")
    except Exception as e:
        print(f"An error occurred while compressing image {case_image_id}: {e}")
