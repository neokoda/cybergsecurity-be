from datetime import datetime
from sqlalchemy.orm import Session
from models.document_reference import DocumentReference

def seed_document_references(db: Session):
    references_data = [
        {
            "title": "Standar Keamanan IT",
            "description": "Dokumen standar keamanan IT perusahaan",
            "file_path": "/documents/references/security_standards.pdf",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "title": "Template Kontrak Pengadaan",
            "description": "Template standar untuk kontrak pengadaan barang dan jasa",
            "file_path": "/documents/references/procurement_template.docx",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "title": "Pedoman Kemitraan",
            "description": "Pedoman dan prosedur untuk kemitraan strategis",
            "file_path": "/documents/references/partnership_guidelines.pdf",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "title": "Regulasi Logistik",
            "description": "Regulasi dan compliance untuk layanan logistik",
            "file_path": "/documents/references/logistics_regulation.pdf",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "title": "Standar Pelabuhan Digital",
            "description": "Standar dan spesifikasi untuk layanan pelabuhan digital",
            "file_path": "/documents/references/digital_port_standards.pdf",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "title": "Kebijakan Data Privacy",
            "description": "Kebijakan perlindungan data dan privacy",
            "file_path": "/documents/references/data_privacy_policy.pdf",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]
    
    for ref_data in references_data:
        reference = DocumentReference(**ref_data)
        db.add(reference)
    
    db.commit()
    print("Document references seeded successfully")