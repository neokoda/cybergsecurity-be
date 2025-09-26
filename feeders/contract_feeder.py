from datetime import datetime
from sqlalchemy.orm import Session
from models.contract import Contract
from models.enums import JenisKontrakEnum
from models.user import User

def seed_contracts(db: Session):
    users = db.query(User).all()
    
    contracts_data = [
        {
            "title": "Sistem Manajemen Dokumen Digital",
            "description": "Pengembangan sistem manajemen dokumen digital untuk meningkatkan efisiensi operasional",
            "jenis_kontrak": JenisKontrakEnum.LAYANAN_TEKNOLOGI_INFORMASI,
            "created_by": users[0].uuid,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "title": "Pengadaan Server dan Infrastructure",
            "description": "Pengadaan server dan infrastruktur IT untuk mendukung operasional perusahaan",
            "jenis_kontrak": JenisKontrakEnum.PENGADAAN_BARANG_JASA,
            "created_by": users[1].uuid,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "title": "Kerjasama Strategis Regional",
            "description": "Kemitraan strategis dengan partner regional untuk ekspansi bisnis",
            "jenis_kontrak": JenisKontrakEnum.KEMITRAAN_GLOBAL,
            "created_by": users[0].uuid,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "title": "Optimasi Rantai Pasok",
            "description": "Integrasi sistem logistik untuk optimasi rantai pasok",
            "jenis_kontrak": JenisKontrakEnum.INTEGRASI_LOGISTIK,
            "created_by": users[2].uuid,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "title": "Platform Pelabuhan Digital",
            "description": "Pengembangan platform digital untuk layanan kepelabuhan",
            "jenis_kontrak": JenisKontrakEnum.JASA_KEPELABUHAN_DIGITAL,
            "created_by": users[1].uuid,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]
    
    for contract_data in contracts_data:
        contract = Contract(**contract_data)
        db.add(contract)
    
    db.commit()
    print("Contracts seeded successfully")