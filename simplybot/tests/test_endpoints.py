import requests
import json
import os
from pathlib import Path

def test_documents_info():
    """Test endpointu /documents/info"""
    print("="*60)
    print("TEST ENDPOINTU /documents/info")
    print("="*60)
    
    API_BASE_URL = "http://localhost:8000"
    
    try:
        response = requests.get(f"{API_BASE_URL}/documents/info")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {result.get('status', 'unknown')}")
            print(f"📊 Collection name: {result.get('name', 'unknown')}")
            print(f"🔢 Vector count: {result.get('vectors_count', 'unknown')}")
            
            # Check if vectors_count is not None
            if result.get('vectors_count') is not None:
                print("✅ vectors_count is not None")
            else:
                print("❌ vectors_count is None")
                
        else:
            print(f"❌ Błąd: {response.status_code}")
            print(f"Odpowiedź: {response.text}")
    except Exception as e:
        print(f"❌ Błąd połączenia: {e}")

def test_files_endpoint():
    """Test /files endpoint"""
    print("\n" + "="*60)
    print("TEST /files ENDPOINT")
    print("="*60)
    
    API_BASE_URL = "http://localhost:8000"
    
    try:
        response = requests.get(f"{API_BASE_URL}/files")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: OK")
            print(f"📁 File count: {result.get('total_count', 0)}")
            print(f"📏 Total size: {result.get('total_size', 0)} bytes")
            
            files = result.get('files', [])
            if files:
                print("📄 File list:")
                for file in files:
                    print(f"  - {file.get('filename')} ({file.get('size')} bytes)")
            else:
                print("📄 No files")
                
        else:
            print(f"❌ Błąd: {response.status_code}")
            print(f"Odpowiedź: {response.text}")
    except Exception as e:
        print(f"❌ Błąd połączenia: {e}")

def test_health_check():
    """Test endpointu / (health check)"""
    print("\n" + "="*60)
    print("TEST ENDPOINTU / (health check)")
    print("="*60)
    
    API_BASE_URL = "http://localhost:8000"
    
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {result.get('status', 'unknown')}")
            
            services = result.get('services', {})
            print("🔧 Status usług:")
            for service, status in services.items():
                print(f"  - {service}: {status}")
                
        else:
            print(f"❌ Błąd: {response.status_code}")
            print(f"Odpowiedź: {response.text}")
    except Exception as e:
        print(f"❌ Błąd połączenia: {e}")

def test_cleanup_audio_removed():
    """Test czy endpoint /cleanup-audio został usunięty"""
    print("\n" + "="*60)
    print("TEST USUNIĘCIA /cleanup-audio")
    print("="*60)
    
    API_BASE_URL = "http://localhost:8000"
    
    try:
        response = requests.post(f"{API_BASE_URL}/cleanup-audio")
        if response.status_code == 404:
            print("✅ Endpoint /cleanup-audio został usunięty (404)")
        else:
            print(f"❌ Endpoint /cleanup-audio nadal istnieje (status: {response.status_code})")
    except Exception as e:
        print(f"❌ Błąd połączenia: {e}")

def test_upload_dir_exists():
    """Test czy katalog uploads istnieje"""
    print("\n" + "="*60)
    print("TEST KATALOGU UPLOADS")
    print("="*60)
    
    upload_dir = Path("uploads")
    if upload_dir.exists():
        print(f"✅ Katalog {upload_dir} istnieje")
        
        # Sprawdź pliki w katalogu
        files = list(upload_dir.glob("*.*"))
        print(f"📁 Liczba plików w katalogu: {len(files)}")
        
        for file in files:
            if file.suffix.lower() in ['.pdf', '.txt', '.docx']:
                size = file.stat().st_size
                print(f"  - {file.name} ({size} bajtów)")
    else:
        print(f"⚠️ Katalog {upload_dir} nie istnieje (zostanie utworzony automatycznie)")

if __name__ == "__main__":
    test_documents_info()
    test_files_endpoint()
    test_health_check()
    test_cleanup_audio_removed()
    test_upload_dir_exists()
    
    print("\n" + "="*60)
    print("✅ WSZYSTKIE TESTY ZAKOŃCZONE")
    print("="*60) 