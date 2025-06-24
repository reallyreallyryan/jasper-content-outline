print("Hello World - Python is working!")

try:
    import fastapi
    print("✅ FastAPI found!")
except ImportError:
    print("❌ FastAPI NOT found")

print("Test complete")
