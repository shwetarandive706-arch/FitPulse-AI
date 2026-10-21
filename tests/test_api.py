import unittest
import json
import os
import sys

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app
import database
import models

class FitPulseAPITestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_01_health_status(self):
        """Test health and system status endpoint"""
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("status"), "online")
        self.assertIn("RandomForest_ChurnClassifier", data.get("ai_models_loaded"))

    def test_02_admin_login(self):
        """Test admin authentication"""
        res = self.client.post("/api/auth/login", json={"identifier": "admin", "password": "admin123"})
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data.get("success"))
        self.assertEqual(data["user"]["role"], "admin")

    def test_03_member_login(self):
        """Test member authentication"""
        res = self.client.post("/api/auth/login", json={"identifier": "member1", "password": "1234"})
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data.get("success"))
        self.assertEqual(data["user"]["role"], "member")
        self.assertIn("subscription", data["user"])

    def test_04_invalid_login(self):
        """Test rejection of bad credentials"""
        res = self.client.post("/api/auth/login", json={"identifier": "admin", "password": "wrongpassword"})
        self.assertEqual(res.status_code, 401)
        data = json.loads(res.data)
        self.assertFalse(data.get("success"))

    def test_05_admin_dashboard_metrics(self):
        """Test KPI dashboard aggregation"""
        res = self.client.get("/api/admin/dashboard")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data.get("success"))
        m = data["metrics"]
        self.assertGreaterEqual(m["total_members"], 5)
        self.assertGreaterEqual(m["active_subscribers"], 4)
        self.assertGreater(m["total_revenue"], 0)

    def test_06_member_listing(self):
        """Test member roster endpoint"""
        res = self.client.get("/api/members")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data.get("success"))
        self.assertGreaterEqual(data["count"], 5)

    def test_07_membership_plans(self):
        """Test membership plans listing"""
        res = self.client.get("/api/plans")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data.get("success"))
        self.assertEqual(len(data["plans"]), 4)

    def test_08_dynamic_qr_generation(self):
        """Test dynamic time-limited QR token generation"""
        res = self.client.get("/api/checkin/generate-token?member_id=1")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data.get("success"))
        tok = data["token_data"]
        self.assertTrue(len(tok["token"]) >= 16)
        self.assertEqual(tok["valid_seconds"], 300)

    def test_09_csv_exports(self):
        """Test member and attendance CSV downloads"""
        res_mem = self.client.get("/api/export/members.csv")
        self.assertEqual(res_mem.status_code, 200)
        self.assertIn("text/csv", res_mem.content_type)
        self.assertIn("Member ID", res_mem.data.decode("utf-8"))

        res_att = self.client.get("/api/export/attendance.csv")
        self.assertEqual(res_att.status_code, 200)
        self.assertIn("text/csv", res_att.content_type)
        self.assertIn("Checkin ID", res_att.data.decode("utf-8"))

if __name__ == "__main__":
    unittest.main()
