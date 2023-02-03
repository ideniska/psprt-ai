from core.celery import app
from app.service import PhotoPreparation


@app.task
def process_photos(
    photo_size_country, file_path, file_name, session_key, uploaded_file_id
):
    service = PhotoPreparation(
        photo_size_country,
        file_path,
        file_name,
        session_key,
        uploaded_file_id,
    )
    service.make()
    return "completed"
