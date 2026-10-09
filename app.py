import os
import sqlite3
import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'properties.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_leads_table():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS property_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            budget REAL,
            preferred_city TEXT,
            property_type TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

try:
    init_leads_table()
except Exception as e:
    print("Notice initializing leads table:", e)

# Curated high-resolution room gallery sets with Arabic descriptions
GALLERY_DATA = {
    'Apartment': [
        [
            {'title': 'غرفة المعيشة والاستقبال', 'url': 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80'},
            {'title': 'غرفة النوم الرئيسية (ماستر)', 'url': 'https://images.unsplash.com/photo-1595526114035-0d45ed16cfbf?auto=format&fit=crop&w=1200&q=80'},
            {'title': 'المطبخ المجهز بالكامل', 'url': 'https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=1200&q=80'},
            {'title': 'الحمام المودرن والتشطيبات', 'url': 'https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=1200&q=80'},
            {'title': 'الشرفة والإطلالة المفتوحة', 'url': 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1200&q=80'},
            {'title': 'الواجهة المعمارية ومدخل العمارة', 'url': 'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=1200&q=80'}
        ],
        [
            {'title': 'صالون استقبال فاخر', 'url': 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=1200&q=80'},
            {'title': 'غرفة نوم عصرية مضاءة', 'url': 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=1200&q=80'},
            {'title': 'مطبخ مفتوح نظام أمريكي', 'url': 'https://images.unsplash.com/photo-1507089947368-19c1da9775ae?auto=format&fit=crop&w=1200&q=80'},
            {'title': 'حمام الضيوف الفاخر', 'url': 'https://images.unsplash.com/photo-1620626011761-996317b8d101?auto=format&fit=crop&w=1200&q=80'},
            {'title': 'إطلالة البحيرة والحديقة', 'url': 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=1200&q=80'}
        ]
    ],
    'Villa': [
        [
            {'title': 'الواجهة الخارجية والحديقة والمسبح', 'url': 'https://images.unsplash.com/photo-1613977257363-707ba9348227?auto=format&fit=crop&w=1200&q=80'},
            {'title': 'الريسبشن الملكي والبهو المفتوح', 'url': 'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1200&q=80'},
            {'title': 'جناح النوم الماستر الفاخر', 'url': 'https://images.unsplash.com/photo-1616594039964-ae9021a400a0?auto=format&fit=crop&w=1200&q=80'},
            {'title': 'المطبخ الإيطالي المتكامل', 'url': 'https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=1200&q=80'},
            {'title': 'الحديقة الخاصة واللاندسكيب', 'url': 'https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=1200&q=80'},
            {'title': 'حمام الجاكوزي الماستر', 'url': 'https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=1200&q=80'}
        ]
    ],
    'Townhouse': [
        [
            {'title': 'الواجهة الخارجية للتاون هاوس', 'url': 'https://images.unsplash.com/photo-1600565193348-f74bd3c7ccdf?auto=format&fit=crop&w=1200&q=80'},
            {'title': 'غرفة المعيشة والاستقبال', 'url': 'https://images.unsplash.com/photo-1588880331179-bc9b93a8cb5e?auto=format&fit=crop&w=1200&q=80'},
            {'title': 'غرفة النوم الرئيسية', 'url': 'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=1200&q=80'},
            {'title': 'مطبخ عالي الجودة', 'url': 'https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=1200&q=80'},
            {'title': 'الحديقة الخلفية والتراس', 'url': 'https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=1200&q=80'}
        ]
    ],
    'Chalet': [
        [
            {'title': 'إطلالة البحر المباشرة والشاطئ', 'url': 'https://images.unsplash.com/photo-1510798831971-661eb04b3739?auto=format&fit=crop&w=1200&q=80'},
            {'title': 'تراس الشاليه والجلسة الخارجية', 'url': 'https://images.unsplash.com/photo-1499793983690-e29da59ef1c2?auto=format&fit=crop&w=1200&q=80'},
            {'title': 'صالة الاسترخاء الصيفية', 'url': 'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=1200&q=80'},
            {'title': 'غرفة النوم بإطلالة على المسبح', 'url': 'https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=1200&q=80'},
            {'title': 'حمامات سباحة المنتجع الفندقي', 'url': 'https://images.unsplash.com/photo-1576013551627-0cc20b96c2a7?auto=format&fit=crop&w=1200&q=80'}
        ]
    ],
    'Commercial': [
        [
            {'title': 'مساحة العمل المفتوحة والتشطيب الفاخر', 'url': 'https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=1200&q=80'},
            {'title': 'غرفة الاجتماعات وقاعة المؤتمرات', 'url': 'https://images.unsplash.com/photo-1497215728101-856f4ea42174?auto=format&fit=crop&w=1200&q=80'},
            {'title': 'بهو الاستقبال الفاخر', 'url': 'https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=1200&q=80'},
            {'title': 'الواجهة الزجاجية للمول أو المبنى الإداري', 'url': 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1200&q=80'}
        ]
    ]
}

def get_property_gallery(prop_type, category, prop_id):
    if 'commercial' in category or prop_type in ['Office Space', 'Shop', 'Retail', 'Clinic', 'Show Room', 'Co-Working Space']:
        sets = GALLERY_DATA['Commercial']
    elif prop_type in ['Villa', 'Palace', 'Twin House', 'Whole Building']:
        sets = GALLERY_DATA['Villa']
    elif prop_type in ['Townhouse', 'iVilla', 'Duplex']:
        sets = GALLERY_DATA['Townhouse']
    elif prop_type in ['Chalet', 'Cabin', 'Bungalow']:
        sets = GALLERY_DATA['Chalet']
    else:
        sets = GALLERY_DATA['Apartment']

    selected_set = sets[prop_id % len(sets)]
    return selected_set

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/properties')
def get_properties():
    q = request.args.get('q', '').strip()
    category = request.args.get('category', 'all').strip()
    property_type = request.args.get('property_type', 'all').strip()
    region = request.args.get('region', 'all').strip()
    city = request.args.get('city', 'all').strip()
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    bedrooms = request.args.get('bedrooms', 'all').strip()
    min_size = request.args.get('min_size', type=float)
    max_size = request.args.get('max_size', type=float)
    sort = request.args.get('sort', 'newest').strip()
    page = max(1, request.args.get('page', 1, type=int))
    limit = min(60, max(6, request.args.get('limit', 24, type=int)))
    offset = (page - 1) * limit

    conditions = []
    params = []

    if q:
        search_kw = f"%{q}%"
        conditions.append("(title LIKE ? OR compound LIKE ? OR district LIKE ? OR city LIKE ? OR city_ar LIKE ? OR property_type_ar LIKE ?)")
        params.extend([search_kw, search_kw, search_kw, search_kw, search_kw, search_kw])

    if category and category != 'all':
        conditions.append("category = ?")
        params.append(category)

    if property_type and property_type != 'all':
        conditions.append("property_type = ?")
        params.append(property_type)

    if region and region != 'all':
        conditions.append("region = ?")
        params.append(region)

    if city and city != 'all':
        conditions.append("city = ?")
        params.append(city)

    if min_price is not None and min_price > 0:
        conditions.append("price >= ?")
        params.append(min_price)

    if max_price is not None and max_price > 0:
        conditions.append("price <= ?")
        params.append(max_price)

    if bedrooms and bedrooms != 'all':
        if bedrooms == '5+':
            conditions.append("bedrooms >= 5")
        else:
            try:
                b_num = int(bedrooms)
                conditions.append("bedrooms = ?")
                params.append(b_num)
            except ValueError:
                pass

    if min_size is not None and min_size > 0:
        conditions.append("size >= ?")
        params.append(min_size)

    if max_size is not None and max_size > 0:
        conditions.append("size <= ?")
        params.append(max_size)

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    order_clause = "ORDER BY id DESC"
    if sort == 'price_asc':
        order_clause = "ORDER BY price ASC"
    elif sort == 'price_desc':
        order_clause = "ORDER BY price DESC"
    elif sort == 'size_desc':
        order_clause = "ORDER BY size DESC"
    elif sort == 'size_asc':
        order_clause = "ORDER BY size ASC"
    elif sort == 'sqm_asc':
        order_clause = "ORDER BY value_per_sqm ASC"

    conn = get_db()
    cur = conn.cursor()

    count_query = f"SELECT COUNT(*) FROM properties {where_clause}"
    cur.execute(count_query, params)
    total = cur.fetchone()[0]

    data_query = f"""
        SELECT id, title, price, price_period, property_type, property_type_ar,
               category, category_ar, region, region_ar, city, city_ar,
               district, compound, bedrooms, bathrooms, size, value_per_sqm,
               latitude, longitude, distance_to_center_km, amenities, share_url, image_url
        FROM properties
        {where_clause}
        {order_clause}
        LIMIT ? OFFSET ?
    """
    cur.execute(data_query, params + [limit, offset])
    rows = cur.fetchall()

    properties = []
    for r in rows:
        amenities_val = []
        if r['amenities']:
            try:
                amenities_val = json.loads(r['amenities'])
            except Exception:
                amenities_val = []

        properties.append({
            'id': r['id'],
            'title': r['title'],
            'price': r['price'],
            'price_period': r['price_period'],
            'property_type': r['property_type'],
            'property_type_ar': r['property_type_ar'],
            'category': r['category'],
            'category_ar': r['category_ar'],
            'region': r['region'],
            'region_ar': r['region_ar'],
            'city': r['city'],
            'city_ar': r['city_ar'],
            'district': r['district'],
            'compound': r['compound'],
            'bedrooms': r['bedrooms'],
            'bathrooms': r['bathrooms'],
            'size': r['size'],
            'value_per_sqm': r['value_per_sqm'],
            'latitude': r['latitude'],
            'longitude': r['longitude'],
            'distance_to_center_km': r['distance_to_center_km'],
            'amenities': amenities_val,
            'share_url': r['share_url'],
            'image_url': r['image_url']
        })

    conn.close()

    total_pages = (total + limit - 1) // limit if total > 0 else 1

    return jsonify({
        'total': total,
        'page': page,
        'limit': limit,
        'total_pages': total_pages,
        'properties': properties
    })

@app.route('/api/property/<int:prop_id>')
def get_property(prop_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM properties WHERE id = ?
    """, (prop_id,))
    row = cur.fetchone()

    if not row:
        conn.close()
        return jsonify({'error': 'Property not found'}), 404

    amenities_val = []
    if row['amenities']:
        try:
            amenities_val = json.loads(row['amenities'])
        except Exception:
            amenities_val = []

    prop = dict(row)
    prop['amenities'] = amenities_val

    # Find similar properties in same city and category
    cur.execute("""
        SELECT id, title, price, price_period, property_type_ar, city_ar, bedrooms, size, image_url
        FROM properties
        WHERE city = ? AND category = ? AND id != ?
        LIMIT 4
    """, (row['city'], row['category'], prop_id))
    similars = [dict(s) for s in cur.fetchall()]

    conn.close()
    return jsonify({
        'property': prop,
        'similar': similars
    })

@app.route('/api/map_properties')
def get_map_properties():
    # Return coordinates for up to 300 properties with lat/lng
    category = request.args.get('category', 'all').strip()
    city = request.args.get('city', 'all').strip()

    conditions = ["latitude IS NOT NULL", "longitude IS NOT NULL", "latitude != 0", "longitude != 0"]
    params = []

    if category and category != 'all':
        conditions.append("category = ?")
        params.append(category)

    if city and city != 'all':
        conditions.append("city = ?")
        params.append(city)

    where_clause = "WHERE " + " AND ".join(conditions)

    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"""
        SELECT id, title, price, price_period, property_type_ar, category_ar,
               city_ar, compound, bedrooms, size, latitude, longitude, image_url
        FROM properties
        {where_clause}
        ORDER BY id DESC
        LIMIT 250
    """, params)

    rows = cur.fetchall()
    conn.close()

    return jsonify([dict(r) for r in rows])

@app.route('/api/filters')
def get_filters():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT category, category_ar, COUNT(*) as count 
        FROM properties 
        GROUP BY category 
        ORDER BY count DESC
    """)
    categories = [dict(r) for r in cur.fetchall()]

    cur.execute("""
        SELECT property_type, property_type_ar, COUNT(*) as count 
        FROM properties 
        GROUP BY property_type 
        ORDER BY count DESC
    """)
    property_types = [dict(r) for r in cur.fetchall()]

    cur.execute("""
        SELECT region, region_ar, COUNT(*) as count 
        FROM properties 
        GROUP BY region 
        ORDER BY count DESC
    """)
    regions = [dict(r) for r in cur.fetchall()]

    cur.execute("""
        SELECT city, city_ar, region, COUNT(*) as count 
        FROM properties 
        WHERE city IS NOT NULL AND city != ''
        GROUP BY city 
        ORDER BY count DESC 
        LIMIT 30
    """)
    cities = [dict(r) for r in cur.fetchall()]

    conn.close()
    return jsonify({
        'categories': categories,
        'property_types': property_types,
        'regions': regions,
        'cities': cities
    })

@app.route('/api/stats')
def get_stats():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM properties")
    total_listings = cur.fetchone()[0]

    cur.execute("SELECT COUNT(DISTINCT compound) FROM properties WHERE compound != ''")
    compounds_count = cur.fetchone()[0]

    # Average price per sqm for top cities (for sales)
    top_cities = [
        'New Cairo City', 'Sheikh Zayed City', '6 October City', 
        'Hay El Maadi', 'New Capital City', 'Hurghada', 'Madinaty'
    ]
    city_sqm_stats = []
    for c in top_cities:
        cur.execute("""
            SELECT city_ar, ROUND(AVG(value_per_sqm)), COUNT(*) 
            FROM properties 
            WHERE city = ? AND category = 'buy' AND value_per_sqm > 5000 AND value_per_sqm < 300000
        """, (c,))
        res = cur.fetchone()
        if res and res[1]:
            city_sqm_stats.append({
                'city': c,
                'city_ar': res[0],
                'avg_sqm': int(res[1]),
                'count': res[2]
            })

    # Property type distribution
    cur.execute("""
        SELECT property_type_ar, COUNT(*) as count 
        FROM properties 
        WHERE property_type IN ('Apartment', 'Villa', 'Townhouse', 'Duplex', 'Chalet', 'Office Space', 'Shop')
        GROUP BY property_type 
        ORDER BY count DESC
    """)
    type_distribution = [dict(r) for r in cur.fetchall()]

    conn.close()
    return jsonify({
        'total_listings': total_listings,
        'compounds_count': compounds_count,
        'city_sqm_stats': city_sqm_stats,
        'type_distribution': type_distribution
    })

@app.route('/api/estimate', methods=['POST'])
def estimate_price():
    data = request.get_json() or {}
    city = data.get('city', 'New Cairo City')
    property_type = data.get('property_type', 'Apartment')
    size = float(data.get('size', 150))
    category = data.get('category', 'buy')

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT value_per_sqm 
        FROM properties 
        WHERE city = ? AND property_type = ? AND category = ? AND value_per_sqm > 500
        ORDER BY value_per_sqm ASC
    """, (city, property_type, category))
    rows = [r[0] for r in cur.fetchall()]

    if not rows:
        # Fallback to city general
        cur.execute("""
            SELECT value_per_sqm 
            FROM properties 
            WHERE city = ? AND category = ? AND value_per_sqm > 500
            ORDER BY value_per_sqm ASC
        """, (city, category))
        rows = [r[0] for r in cur.fetchall()]

    if not rows:
        conn.close()
        return jsonify({'error': 'بيانات غير كافية لحساب التقدير لهذه المنطقة'}), 400

    n = len(rows)
    median_sqm = rows[n // 2]
    q25_sqm = rows[int(n * 0.25)]
    q75_sqm = rows[int(n * 0.75)]

    estimated_price = int(median_sqm * size)
    min_range = int(q25_sqm * size)
    max_range = int(q75_sqm * size)

    conn.close()
    return jsonify({
        'estimated_price': estimated_price,
        'min_range': min_range,
        'max_range': max_range,
        'median_sqm': int(median_sqm),
        'sample_size': n,
        'size': size,
        'currency': 'ج.م'
    })

@app.route('/api/leads', methods=['POST'])
def submit_lead():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    budget = data.get('budget')
    preferred_city = data.get('preferred_city', '').strip()
    property_type = data.get('property_type', '').strip()
    notes = data.get('notes', '').strip()

    if not name or not phone:
        return jsonify({'error': 'يرجى إدخال الاسم ورقم الموبايل بشكل صحيح'}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO property_requests (name, phone, budget, preferred_city, property_type, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, phone, budget, preferred_city, property_type, notes))
    lead_id = cur.lastrowid
    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'message': 'تم تسجيل طلبك بنجاح! سيتواصل معك أحد مستشارينا العقاريين قريباً.',
        'lead_id': lead_id
    })

@app.route('/api/leads', methods=['GET'])
def list_leads():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM property_requests ORDER BY id DESC LIMIT 50')
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
