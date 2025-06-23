#!/usr/bin/env python3
import os
import sys

import uvicorn

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def start_microservice():
    """Start the AI microservice"""
    try:
        print("🚀 Starting AI Microservice with Redis cache and rate limiting...")
        print("📡 Microservice will be available at: http://localhost:8001")
        print("🔥 Features enabled: Redis cache, Rate limiting, Async tasks")
        print("=" * 60)

        # Start the server
        uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False, log_level="info")
    except KeyboardInterrupt:
        print("\n🛑 Microservice stopped by user")
    except Exception as e:
        print(f"❌ Failed to start microservice: {e}")
        sys.exit(1)


if __name__ == "__main__":
    start_microservice()
