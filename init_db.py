import os
import sqlite3
import json
import ast
import pandas as pd

# Arabic translations
CATEGORY_AR = {
    'buy': 'للبيع',
    'rent': 'للإيجار',
    'commercial_buy': 'تجاري للبيع',
    'commercial_rent': 'تجاري للإيجار'
}

PROPERTY_TYPE_AR = {
    'Apartment': 'شقة',
    'Villa': 'فيلا مستقلة',
    'Duplex': 'دوبلكس',
    'Townhouse': 'تاون هاوس',
    'Penthouse': 'بنتهاوس',
    'Twin House': 'توين هاوس',
    'iVilla': 'آي فيلا',
    'Roof': 'روف',
    'Chalet': 'شاليه',
    'Palace': 'قصر',
    'Whole Building': 'عمارة بالكامل',
    'Bungalow': 'بانجلو',
    'Cabin': 'كابينة',
    'Hotel Apartment': 'شقة فندقية',
    'Full Floor': 'دور كامل',
    'Half Floor': 'نصف دور',
    'Shop': 'محل تجاري',
    'Office Space': 'مكتب إداري',
    'Retail': 'مساحة تجارية',
    'Show Room': 'معرض',
    'Clinic': 'عيادة طبية',
    'Restaurant': 'مطعم',
    'Cafeteria': 'كافيه',
    'Co-Working Space': 'مساحة عمل مشتركة',
    'Medical Facility': 'مركز طبي',
    'Staff Accommodation': 'سكن موظفين',
    'Bulk Sale Unit': 'وحدات بيع جملة',
    'Bulk Rent Unit': 'وحدات إيجار جملة'
}

REGION_AR = {
    'Cairo': 'القاهرة',
    'Giza': 'الجيزة',
    'Alexandria': 'الإسكندرية',
    'Red Sea': 'البحر الأحمر',
    'Qalyubia': 'القليوبية',
    'Suez': 'السويس',
    'North Coast': 'الساحل الشمالي',
    'South Sainai': 'جنوب سيناء',
    'Al Daqahlya': 'الدقهلية',
    'Matrouh': 'مطروح',
    'Sharqia': 'الشرقية',
    'Demyat': 'دمياط',
    'Al Fayum': 'الفيوم',
    'Al Gharbeya': 'الغربية',
    'Asyut': 'أسيوط',
    'Al Menya': 'المنيا',
    'El Esmailia': 'الإسماعيلية',
    'Al Menofeya': 'المنوفية'
}

CITY_AR = {
    'New Cairo City': 'القاهرة الجديدة',
    'Sheikh Zayed City': 'الشيخ زايد',
    '6 October City': 'مدينة 6 أكتوبر',
    'Hay El Maadi': 'المعادي',
    'Hurghada': 'الغردقة',
    'Hay Sharq': 'حي شرق (الإسكندرية)',
    'New Capital City': 'العاصمة الإدارية الجديدة',
    'Madinaty': 'مدينتي',
    'Mostakbal City - Future City': 'مدينة المستقبل',
    'Al Ain Al Sokhna': 'العين السخنة',
    'Heliopolis - Masr El Gedida': 'مصر الجديدة',
    'Nasr City': 'مدينة نصر',
    'El Nozha': 'النزهة',
    'Zamalek': 'الزمالك',
    'Shorouk City': 'مدينة الشروق',
    'Mohandessin': 'المهندسين',
    'Sidi Abdel Rahman': 'سيدي عبد الرحمن',
    'Ras Al Hekma': 'رأس الحكمة',
    'Mokattam': 'المقطم',
    'Hay Wasat': 'وسط الإسكندرية',
    'Al Alamein': 'العلمين الجديدة',
    'Qesm Marsa Matrouh': 'مرسى مطروح',
    'Dokki': 'الدقي',
    'New Heliopolis': 'هليوبوليس الجديدة',
    'Qesm Ad Dabaah': 'الضبعة',
    'El Gouna': 'الجونة',
    'Obour City': 'مدينة العبور',
    'Sharm El Sheikh': 'شرم الشيخ'
}

AMENITIES_MAP = {
    'CP': 'موقف سيارات مغطى',
    'BA': 'شرفة / بلكونة',
    'LB': 'بهو استقبال فاخر',
    'SE': 'أمن وحراسة 24/7',
    'SY': 'جيم وصالة رياضية',
    'BL': 'خزائن ملابس مدمجة',
    'AC': 'تكييف مركزي',
    'AN': 'شبكة إنترنت فايبر',
    'BK': 'أجهزة مطبخ متطورة',
    'SP': 'حمام سباحة',
    'SS': 'سبا وجاكوزي',
    'BW': 'مطبخ مجهز بالكامل',
    'WC': 'غرفة ملابس (دريسنج)',
    'ST': 'غرفة مكتب / دراسة',
    'PG': 'حديقة خاصة',
    'VW': 'إطلالة بانورامية مميزة',
    'CO': 'خدمة كونسيرج',
    'CR': 'منطقة ألعاب أطفال',
    'MR': 'غرفة خادمة',
    'DN': 'غرفة طعام'
}

# Curated high quality architectural and interior photos
IMAGE_POOLS = {
    'Apartment': [
        'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80'
    ],
    'Villa': [
        'https://images.unsplash.com/photo-1613977257363-707ba9348227?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=800&q=80'
    ],
    'Townhouse': [
        'https://images.unsplash.com/photo-1600565193348-f74bd3c7ccdf?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1588880331179-bc9b93a8cb5e?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80'
    ],
    'Chalet': [
        'https://images.unsplash.com/photo-1510798831971-661eb04b3739?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1499793983690-e29da59ef1c2?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=800&q=80'
    ],
    'Commercial': [
        'https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1497215728101-856f4ea42174?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=800&q=80'
    ]
}

def get_image_for_property(prop_type, cat, prop_id):
    if 'commercial' in cat or prop_type in ['Office Space', 'Shop', 'Retail', 'Clinic', 'Show Room', 'Co-Working Space']:
        pool = IMAGE_POOLS['Commercial']
    elif prop_type in ['Villa', 'Palace', 'Twin House', 'Whole Building']:
        pool = IMAGE_POOLS['Villa']
    elif prop_type in ['Townhouse', 'iVilla', 'Duplex']:
        pool = IMAGE_POOLS['Townhouse']
    elif prop_type in ['Chalet', 'Cabin', 'Bungalow']:
        pool = IMAGE_POOLS['Chalet']
    else:
        pool = IMAGE_POOLS['Apartment']
    return pool[prop_id % len(pool)]

def parse_amenities(amen_str):
    if not isinstance(amen_str, str) or not amen_str.strip():
        return []
    try:
        raw_list = ast.literal_eval(amen_str)
        if isinstance(raw_list, list):
            res = []
            for code in raw_list:
                if code in AMENITIES_MAP:
                    res.append(AMENITIES_MAP[code])
            return res
    except Exception:
        pass
    return []

def main():
    print("Reading cleaned_all_egypt.csv...")
    csv_path = 'cleaned_all_egypt.csv'
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found!")
        return

    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows.")

    db_path = 'properties.db'
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("Removed old properties.db")
        except Exception as e:
            print("Notice:", e)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE properties (
        id INTEGER PRIMARY KEY,
        title TEXT,
        price REAL,
        price_period TEXT,
        property_type TEXT,
        property_type_ar TEXT,
        category TEXT,
        category_ar TEXT,
        region TEXT,
        region_ar TEXT,
        city TEXT,
        city_ar TEXT,
        district TEXT,
        compound TEXT,
        bedrooms INTEGER,
        bathrooms INTEGER,
        size REAL,
        value_per_sqm REAL,
        latitude REAL,
        longitude REAL,
        distance_to_center_km REAL,
        amenities TEXT,
        share_url TEXT,
        image_url TEXT
    )
    ''')

    rows_to_insert = []
    print("Processing and translating property records...")

    for _, row in df.iterrows():
        p_id = int(row['id']) if pd.notnull(row['id']) else 0
        title = str(row['title']) if pd.notnull(row['title']) else 'عقار في مصر'
        price = float(row['price']) if pd.notnull(row['price']) else 0.0
        price_period = str(row['price_period']) if pd.notnull(row['price_period']) else ''
        p_type = str(row['property_type']) if pd.notnull(row['property_type']) else 'Apartment'
        p_type_ar = PROPERTY_TYPE_AR.get(p_type, p_type)
        category = str(row['category']) if pd.notnull(row['category']) else 'buy'
        category_ar = CATEGORY_AR.get(category, 'عقار')
        region = str(row['region']) if pd.notnull(row['region']) else 'Cairo'
        region_ar = REGION_AR.get(region, region)
        city = str(row['city']) if pd.notnull(row['city']) else ''
        city_ar = CITY_AR.get(city, city)
        district = str(row['district']) if pd.notnull(row['district']) else ''
        compound = str(row['compound']) if pd.notnull(row['compound']) else ''
        bedrooms = int(row['bedrooms']) if pd.notnull(row['bedrooms']) else 0
        bathrooms = int(row['bathrooms']) if pd.notnull(row['bathrooms']) else 0
        size = float(row['size']) if pd.notnull(row['size']) else 0.0
        val_sqm = float(row['value_per_sqm']) if pd.notnull(row['value_per_sqm']) else 0.0
        lat = float(row['latitude']) if pd.notnull(row['latitude']) else None
        lng = float(row['longitude']) if pd.notnull(row['longitude']) else None
        dist_km = float(row['distance_to_center_km']) if pd.notnull(row['distance_to_center_km']) else 0.0
        share_url = str(row['share_url']) if pd.notnull(row['share_url']) else ''

        amenities_list = parse_amenities(row.get('amenities', ''))
        amenities_json = json.dumps(amenities_list, ensure_ascii=False)

        img = get_image_for_property(p_type, category, p_id)

        rows_to_insert.append((
            p_id, title, price, price_period, p_type, p_type_ar,
            category, category_ar, region, region_ar, city, city_ar,
            district, compound, bedrooms, bathrooms, size, val_sqm,
            lat, lng, dist_km, amenities_json, share_url, img
        ))

    print(f"Inserting {len(rows_to_insert)} records into SQLite database...")
    cur.executemany('''
    INSERT OR REPLACE INTO properties (
        id, title, price, price_period, property_type, property_type_ar,
        category, category_ar, region, region_ar, city, city_ar,
        district, compound, bedrooms, bathrooms, size, value_per_sqm,
        latitude, longitude, distance_to_center_km, amenities, share_url, image_url
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', rows_to_insert)

    print("Building indexes for super fast search queries...")
    cur.execute('CREATE INDEX idx_category ON properties(category)')
    cur.execute('CREATE INDEX idx_prop_type ON properties(property_type)')
    cur.execute('CREATE INDEX idx_region ON properties(region)')
    cur.execute('CREATE INDEX idx_city ON properties(city)')
    cur.execute('CREATE INDEX idx_price ON properties(price)')
    cur.execute('CREATE INDEX idx_bedrooms ON properties(bedrooms)')
    cur.execute('CREATE INDEX idx_size ON properties(size)')

    conn.commit()
    conn.close()

    print("Database built successfully: properties.db")

if __name__ == '__main__':
    main()
