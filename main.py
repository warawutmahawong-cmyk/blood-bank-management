from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta
from data_structures import BloodLinkedList, Queue, PriorityQueue, Stack

app = Flask(__name__)
app.secret_key = 'blood_bank_secret_key'

blood_list = BloodLinkedList()
request_queue = Queue()
priority_queue = PriorityQueue()
distribution_stack = Stack()
hospitals_db = []
storage_rooms_db = []

site_info = {
    "phone": "02-123-4567",
    "email": "support@bloodbank.org",
    "address": "Bangkok, Thailand"
}

def init_mock_data():
    global hospitals_db, storage_rooms_db
    hospitals_db = [
        {"id": "SIR", "name": "โรงพยาบาลศิริราช", "phone": "02-419-7000", "address": "พหลโยธิน กทม."},
        {"id": "CUL", "name": "โรงพยาบาลจุฬาลงกรณ์", "phone": "02-256-4000", "address": "ปทุมวัน กทม."},
        {"id": "RAM", "name": "โรงพยาบาลรามาธิบดี", "phone": "02-201-1000", "address": "พญาไท กทม."}
    ]

    storage_rooms_db = [
        {"room_id": "SIR-R1", "hospital_id": "SIR", "room_name": "ห้องเย็นหลัก ชั้น 1", "capacity": 500, "temperature": "4°C"},
        {"room_id": "CUL-R1", "hospital_id": "CUL", "room_name": "ห้องคลังเลือด ชั้น 3", "capacity": 400, "temperature": "4°C"}
    ]

    today = datetime.today()
    blood_list.append("SIR-O+-0921-001", "O+", 450, (today - timedelta(days=10)).strftime("%Y-%m-%d"), (today + timedelta(days=5)).strftime("%Y-%m-%d"), "AVAILABLE", "SIR-R1")
    blood_list.append("CUL-A+-0921-001", "A+", 450, (today - timedelta(days=5)).strftime("%Y-%m-%d"), (today + timedelta(days=25)).strftime("%Y-%m-%d"), "AVAILABLE", "CUL-R1")

    req1 = {"request_id": "REQ001", "hospital": "โรงพยาบาลศิริราช", "blood_type": "O+", "quantity": 1, "urgency": "NORMAL", "reason": "ผ่าตัดทั่วไป", "date": today.strftime("%Y-%m-%d")}
    req2 = {"request_id": "REQ002", "hospital": "โรงพยาบาลจุฬาลงกรณ์", "blood_type": "O+", "quantity": 1, "urgency": "CRITICAL", "reason": "อุบัติเหตุฉุกเฉิน", "date": today.strftime("%Y-%m-%d")}

    request_queue.enqueue(req1)
    priority_queue.enqueue(req1, "NORMAL")
    priority_queue.enqueue(req2, "CRITICAL")

init_mock_data()

translations = {
    'TH': {
        'nav_dash': 'แดชบอร์ด',
        'nav_inv': 'จัดการคลังถุงเลือด',
        'nav_hosp': 'จัดการข้อมูลโรงพยาบาลและห้องเก็บเลือด',
        'nav_req': 'คำขอรับเลือด',
        'nav_dist': 'ระบบจ่ายเลือด',
        'about': 'เกี่ยวกับเว็บไซต์',
        'dash_title': 'แดชบอร์ดภาพรวมระบบคลังเลือด',
        'total_bags': 'ถุงเลือดทั้งหมด',
        'available': 'พร้อมใช้งาน',
        'expiring': 'ใกล้หมดอายุ',
        'expired': 'หมดอายุแล้ว',
        'queue_req': 'คำขอรอคิว',
        'critical_req': 'คำขอวิกฤต',
        'group_summary': 'สรุปปริมาณเลือดแต่ละกรุ๊ป (พร้อมใช้งาน)',
        'bag_unit': 'ถุง',
        'top_req': 'คำขอเลือดลำดับความสำคัญสูงสุด',
        'hospital': 'โรงพยาบาล',
        'blood_type': 'กรุ๊ปเลือด',
        'urgency': 'ความเร่งด่วน',
        'no_req': 'ไม่มีคำขอในระบบ',
        'inv_title': 'จัดการคลังถุงเลือด',
        'add_bag': 'เพิ่มถุงเลือดใหม่',
        'edit_bag': 'แก้ไขข้อมูลถุงเลือด',
        'search_placeholder': 'ค้นหา รหัสถุง หรือ กรุ๊ป...',
        'all_groups': 'ทุกกรุ๊ปเลือด',
        'search_btn': 'ค้นหา',
        'th_bag_id': 'รหัสถุงเลือด',
        'th_group': 'กรุ๊ป',
        'th_volume': 'ปริมาณ',
        'th_collect_date': 'วันที่เก็บ',
        'th_exp_date': 'วันหมดอายุ',
        'th_exp_status': 'สถานะอายุ',
        'th_stock_status': 'สถานะคลัง',
        'th_location': 'สถานที่จัดเก็บ',
        'th_action': 'การจัดการ',
        'delete': 'ลบ',
        'edit': 'แก้ไข',
        'hosp_title': 'จัดการข้อมูลโรงพยาบาลและห้องเก็บเลือด',
        'add_hosp': 'เพิ่มโรงพยาบาลใหม่',
        'edit_hosp': 'แก้ไขข้อมูลโรงพยาบาล',
        'hosp_list': 'รายชื่อโรงพยาบาลทั้งหมด',
        'th_hosp_code': 'รหัสย่อ',
        'th_hosp_name': 'ชื่อโรงพยาบาล',
        'th_phone': 'เบอร์โทรศัพท์',
        'th_address': 'ที่อยู่',
        'th_rooms': 'ห้องเก็บเลือด',
        'view_rooms': 'ดูห้องเก็บเลือด',
        'req_title': 'คำขอรับเลือด',
        'add_req': 'สร้างคำขอรับเลือด',
        'th_req_id': 'รหัสคำขอ',
        'th_qty': 'จำนวน',
        'th_reason': 'เหตุผล',
        'th_req_date': 'วันที่ขอ',
        'dist_title': 'ระบบจ่ายเลือด',
        'next_req': 'คำขอคิวถัดไปที่ต้องพิจารณา',
        'fefo_title': 'ถุงเลือดที่ระบบเลือกให้ตามหลัก FEFO',
        'confirm_dist': 'ยืนยันการจ่ายเลือด',
        'no_avail_bag': 'ไม่มีถุงเลือดที่พร้อมใช้งาน',
        'dist_history': 'ประวัติการจ่ายเลือดล่าสุด',
        'th_dist_id': 'รหัสรายการ',
        'th_dest_hosp': 'โรงพยาบาลปลายทาง',
        'th_dist_time': 'เวลาจ่าย'
    },
    'EN': {
        'nav_dash': 'Dashboard',
        'nav_inv': 'Blood Inventory',
        'nav_hosp': 'Hospital & Storage Management',
        'nav_req': 'Blood Requests',
        'nav_dist': 'Blood Distribution',
        'about': 'About this Website',
        'dash_title': 'Blood Bank Dashboard Overview',
        'total_bags': 'Total Blood Bags',
        'available': 'Available',
        'expiring': 'Expiring Soon',
        'expired': 'Expired',
        'queue_req': 'Pending Queue',
        'critical_req': 'Critical Requests',
        'group_summary': 'Blood Group Summary (Available)',
        'bag_unit': 'bags',
        'top_req': 'Highest Priority Blood Request',
        'hospital': 'Hospital',
        'blood_type': 'Blood Type',
        'urgency': 'Urgency',
        'no_req': 'No requests in system',
        'inv_title': 'Blood Inventory Management',
        'add_bag': 'Add New Blood Bag',
        'edit_bag': 'Edit Blood Bag',
        'search_placeholder': 'Search Bag ID or Group...',
        'all_groups': 'All Blood Groups',
        'search_btn': 'Search',
        'th_bag_id': 'Bag ID',
        'th_group': 'Group',
        'th_volume': 'Volume',
        'th_collect_date': 'Collection Date',
        'th_exp_date': 'Expiry Date',
        'th_exp_status': 'Expiry Status',
        'th_stock_status': 'Stock Status',
        'th_location': 'Storage Location',
        'th_action': 'Action',
        'delete': 'Delete',
        'edit': 'Edit',
        'hosp_title': 'Hospital & Storage Rooms Management',
        'add_hosp': 'Add New Hospital',
        'edit_hosp': 'Edit Hospital',
        'hosp_list': 'All Hospitals List',
        'th_hosp_code': 'Code',
        'th_hosp_name': 'Hospital Name',
        'th_phone': 'Phone Number',
        'th_address': 'Address',
        'th_rooms': 'Storage Rooms',
        'view_rooms': 'View Rooms',
        'req_title': 'Blood Requests Management',
        'add_req': 'Create Blood Request',
        'th_req_id': 'Request ID',
        'th_qty': 'Quantity',
        'th_reason': 'Reason',
        'th_req_date': 'Request Date',
        'dist_title': 'Blood Distribution System (FEFO)',
        'next_req': 'Next Request to Process',
        'fefo_title': 'Selected Blood Bag via FEFO Principle',
        'confirm_dist': 'Confirm Distribution',
        'no_avail_bag': 'No available blood bags matching criteria',
        'dist_history': 'Recent Distribution History',
        'th_dist_id': 'Transaction ID',
        'th_dest_hosp': 'Destination Hospital',
        'th_dist_time': 'Distribution Time'
    }
}

@app.context_processor
def inject_global_data():
    lang = session.get('lang', 'TH')
    return dict(site_info=site_info, lang=lang, t=translations[lang])

@app.route('/set_lang/<lang>')
def set_lang(lang):
    if lang in ['TH', 'EN']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('dashboard'))

@app.route('/update_contact', methods=['POST'])
def update_contact():
    global site_info
    site_info['phone'] = request.form.get('phone', site_info['phone'])
    site_info['email'] = request.form.get('email', site_info['email'])
    site_info['address'] = request.form.get('address', site_info['address'])
    return redirect(request.referrer or url_for('dashboard'))

@app.route('/')
def dashboard():
    bags = blood_list.to_list()
    total_bags = len(bags)
    avail_bags = len([b for b in bags if b['status'] == 'AVAILABLE'])
    expiring_bags = len([b for b in bags if b['expiry_status'] == 'EXPIRING SOON' and b['status'] == 'AVAILABLE'])
    expired_bags = len([b for b in bags if b['expiry_status'] == 'EXPIRED' or b['status'] == 'EXPIRED'])
    
    group_summary = {}
    for g in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]:
        group_summary[g] = len([b for b in bags if b['blood_type'] == g and b['status'] == 'AVAILABLE'])

    return render_template('index.html', 
                           total_bags=total_bags, 
                           avail_bags=avail_bags, 
                           expiring_bags=expiring_bags, 
                           expired_bags=expired_bags,
                           pending_requests=priority_queue.size(),
                           critical_requests=len([r for r in priority_queue.to_list() if r['urgency'] == 'CRITICAL']),
                           group_summary=group_summary,
                           recent_requests=priority_queue.to_list()[:5],
                           recent_distributions=distribution_stack.get_recent(5))

@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            hospital_code = request.form.get('hospital_code', 'GEN')
            blood_type = request.form.get('blood_type')
            date_str = datetime.today().strftime("%m%d")
            existing_count = len([b for b in blood_list.to_list() if b['blood_type'] == blood_type])
            auto_bag_id = f"{hospital_code}-{blood_type}-{date_str}-{existing_count + 1:03d}"

            blood_list.append(
                auto_bag_id, blood_type, int(request.form.get('volume', 450)),
                request.form.get('collection_date'), request.form.get('expiry_date'),
                "AVAILABLE", request.form.get('location')
            )
        elif action == 'edit':
            bag_id = request.form.get('bag_id')
            bag = blood_list.find(bag_id)
            if bag:
                bag.blood_type = request.form.get('blood_type')
                bag.volume = int(request.form.get('volume', 450))
                bag.collection_date = request.form.get('collection_date')
                bag.expiry_date = request.form.get('expiry_date')
                bag.status = request.form.get('status')
                bag.location = request.form.get('location')
        elif action == 'delete':
            blood_list.remove(request.form.get('bag_id'))
        return redirect(url_for('inventory'))

    search = request.args.get('search', '').strip()
    filter_type = request.args.get('filter_type', '').strip()
    bags = blood_list.to_list()

    if search:
        bags = [b for b in bags if search.lower() in b['bag_id'].lower() or search.lower() in b['blood_type'].lower()]
    
    if filter_type:
        bags = [b for b in bags if b['blood_type'] == filter_type]

    return render_template('inventory.html', bags=bags, filter_type=filter_type, search=search, hospitals=hospitals_db, storage_rooms=storage_rooms_db)

@app.route('/hospitals', methods=['GET', 'POST'])
def hospitals():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_hospital':
            hospitals_db.append({
                "id": request.form.get('id').upper(),
                "name": request.form.get('name'),
                "phone": request.form.get('phone'),
                "address": request.form.get('address')
            })
        elif action == 'edit_hospital':
            h_id = request.form.get('id')
            for h in hospitals_db:
                if h['id'] == h_id:
                    h['name'] = request.form.get('name')
                    h['phone'] = request.form.get('phone')
                    h['address'] = request.form.get('address')
        elif action == 'delete_hospital':
            h_id = request.form.get('id')
            hospitals_db[:] = [h for h in hospitals_db if h['id'] != h_id]
            storage_rooms_db[:] = [r for r in storage_rooms_db if r['hospital_id'] != h_id]
        elif action == 'add_room':
            h_id = request.form.get('hospital_id')
            room_count = len([r for r in storage_rooms_db if r['hospital_id'] == h_id])
            storage_rooms_db.append({
                "room_id": f"{h_id}-R{room_count + 1}",
                "hospital_id": h_id,
                "room_name": request.form.get('room_name'),
                "capacity": int(request.form.get('capacity', 100)),
                "temperature": request.form.get('temperature', '4°C')
            })
        elif action == 'delete_room':
            r_id = request.form.get('room_id')
            storage_rooms_db[:] = [r for r in storage_rooms_db if r['room_id'] != r_id]
        return redirect(url_for('hospitals'))

    return render_template('hospitals.html', hospitals=hospitals_db, storage_rooms=storage_rooms_db)

@app.route('/hospital/<h_id>/rooms')
def hospital_rooms(h_id):
    hospital = next((h for h in hospitals_db if h['id'] == h_id), None)
    if not hospital:
        return redirect(url_for('hospitals'))
    rooms = [r for r in storage_rooms_db if r['hospital_id'] == h_id]
    bags = blood_list.to_list()
    return render_template('hospital_rooms.html', hospital=hospital, rooms=rooms, bags=bags)

@app.route('/requests', methods=['GET', 'POST'])
def requests_page():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            req = {
                "request_id": f"REQ0{len(priority_queue.to_list()) + 1}",
                "hospital": request.form.get('hospital'),
                "blood_type": request.form.get('blood_type'),
                "quantity": int(request.form.get('quantity', 1)),
                "urgency": request.form.get('urgency'),
                "reason": request.form.get('reason'),
                "date": datetime.today().strftime("%Y-%m-%d")
            }
            request_queue.enqueue(req)
            priority_queue.enqueue(req, req['urgency'])
        return redirect(url_for('requests_page'))

    return render_template('requests.html', queue_items=request_queue.items, pq_items=priority_queue.to_list(), hospitals=hospitals_db)

@app.route('/distribution', methods=['GET', 'POST'])
def distribution():
    selected_req = priority_queue.peek()
    matching_bags = []
    selected_bag_feFo = None

    if selected_req:
        b_type = selected_req['blood_type']
        avail_bags = blood_list.find_by_blood_type(b_type)
        valid_bags = [b for b in avail_bags if b.get_expiry_status() != "EXPIRED"]
        valid_bags.sort(key=lambda x: x.expiry_date)
        matching_bags = valid_bags
        if valid_bags:
            selected_bag_feFo = valid_bags[0]

    if request.method == 'POST':
        if selected_req and selected_bag_feFo:
            bag_node = blood_list.find(selected_bag_feFo.bag_id)
            if bag_node:
                bag_node.status = "USED"
            if not request_queue.is_empty():
                request_queue.dequeue()
            priority_queue.dequeue()

            dist_record = {
                "dist_id": f"DIST-{datetime.now().strftime('%H%M%S')}",
                "bag_id": selected_bag_feFo.bag_id,
                "hospital": selected_req['hospital'],
                "blood_type": selected_req['blood_type'],
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            distribution_stack.push(dist_record)
        return redirect(url_for('distribution'))

    return render_template('distribution.html', selected_req=selected_req, matching_bags=matching_bags, selected_bag=selected_bag_feFo, stack_items=distribution_stack.to_list())

@app.route('/structures')
def structures_page():
    return render_template('structures.html',
                           queue_items=request_queue.items,
                           pq_items=priority_queue.to_list(),
                           ll_items=blood_list.to_list(),
                           stack_items=distribution_stack.to_list())

import os
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)