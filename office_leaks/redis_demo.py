"""
=============================================================================
 Redis Setup Verification & Testing Script for Office Leaks
=============================================================================

 Run this script anytime using Python:
   python redis_demo.py

 Tests direct connection to Redis server using core.redis_client.
=============================================================================
"""

import os
import sys
import django

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'office_leaks.settings')
django.setup()

from core.redis_client import RedisClient, get_redis_client


def run_demo():
    print("🚀 Verifying Redis Connection & Setup...")

    # Health Check
    if not RedisClient.ping():
        print("❌ Redis Server is OFFLINE! Make sure Redis is running on 127.0.0.1:6379.")
        return

    print("✅ Redis Server is ONLINE & RESPONDING!")

    r = get_redis_client()

    # 1. Key-Value String Test
    r.set("test:greeting", "Hello Redis!", ex=60)
    val = r.get("test:greeting")
    print(f"-> Key-Value test: {val}")

    # 2. Hash Test
    r.hset("test:user:1", mapping={"name": "Marwan", "role": "Developer"})
    r.expire("test:user:1", 60)
    user = r.hgetall("test:user:1")
    print(f"-> Hash test: {user}")

    # 3. Counter Test
    r.delete("test:counter")
    c1 = r.incrby("test:counter", 1)
    c2 = r.incrby("test:counter", 5)
    print(f"-> Counter test (1 + 5): {c2}")

    # Cleanup test keys
    r.delete("test:greeting", "test:user:1", "test:counter")
    print("✅ Test keys cleaned up successfully!")
    print("\n🎉 Redis is completely ready to be used!")


if __name__ == "__main__":
    run_demo()
