from fastapi import APIRouter, Depends
from fastapi import UploadFile, File, HTTPException
from io import StringIO
import csv
import uuid
from app.models import Batch, Product, Image
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db


router = APIRouter(tags=["Image Processors"])


def process_image(image_id):
    pass


@router.post("/upload")
async def upload_csv(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db)):
    if file.content_type != 'text/csv':
        raise HTTPException(
            status_code=400, detail="Invalid file type. Only CSV allowed.")

    content = await file.read()
    csv_file = StringIO(content.decode('utf-8'))
    reader = csv.reader(csv_file)

    headers = next(reader, None)

    if len(headers) != 3:
        raise HTTPException(status_code=400, detail="Invalid CSV format")

    batch_id = uuid.uuid4()

    batch = Batch(
        id=batch_id,
        status="processing"
    )   
    session.add(batch)

    image_ids = []
    for row in reader:
        serial_number = int(row[0])
        product_name = row[1]
        image_urls = row[2].split(',')

        product = Product(
            batch_id=batch_id,
            serial_number=serial_number,
            product_name=product_name,
            input_image_urls=image_urls
        )

        session.add(product)
        await session.flush()

        for idx, url in enumerate(image_urls):
            image = Image(
                product_id=product.id,
                input_url=url,
            )
            session.add(image)
            await session.flush()
            image_ids.append(image.id)

    for image_id in image_ids:
        print(image_id)
        pass
        # process_image.delay(image_id)

    return {"batch_id": str(batch_id)}


# @router.get("/status/{batch_id}")
# async def get_status(batch_id: str):
    try:
        batch_uuid = uuid.UUID(batch_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid batch ID")
    
    async with async_session() as session:
        batch = session.query(Batch).get(batch_uuid)
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")
        
        pending_images = session.query(Image).join(Product).filter(Product.batch_id == batch.id).filter(Image.status.in_(['pending', 'processing'])).count()
        if pending_images > 0:
            status = 'processing'
        else:
            failed_images = session.query(Image).join(Product).filter(Product.batch_id == batch.id).filter(Image.status == 'failed').count()
            if failed_images > 0:
                status = 'failed'
            else:
                status = 'completed'
        
        if status == 'completed':
            products = session.query(Product).filter_by(batch_id=batch.id).all()
            product_data = [
                {
                    "serial_number": p.serial_number,
                    "product_name": p.product_name,
                    "input_image_urls": p.input_image_urls,
                    "output_image_urls": p.output_image_urls
                } for p in products
            ]
            return {"status": status, "products": product_data}
        else:
            return {"status": status}