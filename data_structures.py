from datetime import datetime, date

# --- 1. LINKED LIST (สำหรับจัดการข้อมูลถุงเลือด) ---
class BloodBagNode:
    def __init__(self, bag_id, blood_type, volume, collection_date, expiry_date, status, location):
        self.bag_id = bag_id
        self.blood_type = blood_type
        self.volume = volume
        self.collection_date = collection_date
        self.expiry_date = expiry_date
        self.status = status  # AVAILABLE, USED, EXPIRED, DISCARDED
        self.location = location
        self.next = None

    def get_expiry_status(self):
        try:
            # แปลงเป็น date object เสมอไม่ว่าจะรับค่ามาแบบไหน
            if isinstance(self.expiry_date, str):
                exp = datetime.strptime(self.expiry_date, "%Y-%m-%d").date()
            else:
                exp = self.expiry_date
                
            today = date.today()
            delta = (exp - today).days
            if delta < 0:
                return "EXPIRED"
            elif delta <= 7:
                return "EXPIRING SOON"
            else:
                return "NORMAL"
        except Exception as e:
            return "NORMAL"

class BloodLinkedList:
    def __init__(self):
        self.head = None

    def append(self, bag_id, blood_type, volume, collection_date, expiry_date, status="AVAILABLE", location="Shelf A-1"):
        new_node = BloodBagNode(bag_id, blood_type, volume, collection_date, expiry_date, status, location)
        if not self.head:
            self.head = new_node
            return
        curr = self.head
        while curr.next:
            curr = curr.next
        curr.next = new_node

    def insert(self, bag_id, blood_type, volume, collection_date, expiry_date, status="AVAILABLE", location="Shelf A-1", index=0):
        new_node = BloodBagNode(bag_id, blood_type, volume, collection_date, expiry_date, status, location)
        if index == 0:
            new_node.next = self.head
            self.head = new_node
            return
        curr = self.head
        for _ in range(index - 1):
            if curr.next is None:
                break
            curr = curr.next
        new_node.next = curr.next
        curr.next = new_node

    def remove(self, bag_id):
        curr = self.head
        prev = None
        while curr:
            if curr.bag_id == bag_id:
                if prev:
                    prev.next = curr.next
                else:
                    self.head = curr.next
                return True
            prev = curr
            curr = curr.next
        return False

    def find(self, bag_id):
        curr = self.head
        while curr:
            if curr.bag_id == bag_id:
                return curr
            curr = curr.next
        return None

    def find_by_blood_type(self, blood_type):
        result = []
        curr = self.head
        while curr:
            if curr.blood_type == blood_type and curr.status == "AVAILABLE":
                result.append(curr)
            curr = curr.next
        return result

    def find_expiring_soon(self):
        result = []
        curr = self.head
        while curr:
            if curr.status == "AVAILABLE" and curr.get_expiry_status() in ["EXPIRED", "EXPIRING SOON"]:
                result.append(curr)
            curr = curr.next
        return result

    def to_list(self):
        result = []
        curr = self.head
        while curr:
            result.append({
                "bag_id": curr.bag_id,
                "blood_type": curr.blood_type,
                "volume": curr.volume,
                "collection_date": curr.collection_date,
                "expiry_date": curr.expiry_date,
                "status": curr.status,
                "location": curr.location,
                "expiry_status": curr.get_expiry_status()
            })
            curr = curr.next
        return result


# --- 2. QUEUE (สำหรับคิวคำขอเลือดทั่วไป - FIFO) ---
class Queue:
    def __init__(self):
        self.items = []

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        if not self.is_empty():
            return self.items.pop(0)
        return None

    def peek(self):
        if not self.is_empty():
            return self.items[0]
        return None

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)


# --- 3. PRIORITY QUEUE (สำหรับจัดลำดับคำขอตามความเร่งด่วน) ---
class PriorityQueue:
    def __init__(self):
        self.items = [] # เก็บแบบ tuple: (priority_level, item)
        # ลำดับความสำคัญ: CRITICAL (1), URGENT (2), NORMAL (3)

    def _get_priority_value(self, priority_str):
        mapping = {"CRITICAL": 1, "URGENT": 2, "NORMAL": 3}
        return mapping.get(priority_str.upper(), 3)

    def enqueue(self, item, priority_str):
        p_val = self._get_priority_value(priority_str)
        item['priority'] = priority_str.upper()
        self.items.append((p_val, item))
        # จัดเรียงใหม่ตามความสำคัญ (ค่าน้อยกว่าอยู่หน้า)
        self.items.sort(key=lambda x: x[0])

    def dequeue(self):
        if not self.is_empty():
            return self.items.pop(0)[1]
        return None

    def peek(self):
        if not self.is_empty():
            return self.items[0][1]
        return None

    def change_priority(self, req_id, new_priority):
        for i, (p_val, item) in enumerate(self.items):
            if item.get('request_id') == req_id:
                self.items.pop(i)
                self.enqueue(item, new_priority)
                return True
        return False

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

    def to_list(self):
        return [item for p_val, item in self.items]


# --- 4. STACK (สำหรับประวัติการจ่ายเลือด - LIFO) ---
class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.is_empty():
            return self.items.pop()
        return None

    def peek(self):
        if not self.is_empty():
            return self.items[-1]
        return None

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

    def get_recent(self, n=5):
        return self.items[::-1][:n]

    def to_list(self):
        return self.items[::-1]