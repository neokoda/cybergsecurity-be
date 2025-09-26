import requests
import json

# Gunakan URL sesuai dengan uvicorn (default: localhost:8000)
BASE_URL = "http://127.0.0.1:8000"

def test_chatbot():
    print("=" * 50)
    print("CHATBOT TEST")
    print("=" * 50)
    
    while True:
        user_input = input("\nMasukkan pertanyaan (atau 'quit' untuk keluar): ")
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Bye!")
            break
            
        if not user_input.strip():
            print("Pertanyaan tidak boleh kosong!")
            continue
        
        try:
            payload = {"message": user_input}
            response = requests.post(f"{BASE_URL}/chatbot/chat", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                print("\nJawaban:")
                print("-" * 30)
                print(result["response"])
                print("-" * 30)
                if result.get("sources"):
                    print(f"Sources: {result['sources']}")
            else:
                print(f"Error: {response.status_code}")
                print(response.text)
                
        except requests.exceptions.ConnectionError:
            print("Error: Tidak dapat terhubung ke server. Pastikan server berjalan di localhost:8000")
            break
        except Exception as e:
            print(f"Error: {str(e)}")

def test_compliance():
    print("=" * 50)
    print("COMPLIANCE TEST")
    print("=" * 50)
    
    sample_urls = [
        "https://example.com/sample-contract.pdf",
        "https://storage.googleapis.com/your-bucket/contract.pdf"
    ]
    
    print("Sample URLs untuk testing:")
    for i, url in enumerate(sample_urls, 1):
        print(f"{i}. {url}")
    
    while True:
        file_url = input("\nMasukkan URL file (atau 'back' untuk kembali): ")
        
        if file_url.lower() == 'back':
            break
            
        if not file_url.strip():
            print("URL tidak boleh kosong!")
            continue
        
        try:
            payload = {"file_url": file_url}
            print("\nMemproses compliance check...")
            response = requests.post(f"{BASE_URL}/compliance/evaluate", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                print("\nHasil Compliance Check:")
                print("-" * 30)
                print(f"Status: {result['status']}")
                print(f"Summary: {result['summary']}")
                print("-" * 30)
            else:
                print(f"Error: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"Detail: {error_detail.get('detail', 'Unknown error')}")
                except:
                    print(response.text)
                    
        except requests.exceptions.ConnectionError:
            print("Error: Tidak dapat terhubung ke server. Pastikan server berjalan di localhost:8000")
            break
        except Exception as e:
            print(f"Error: {str(e)}")

def test_health_check():
    print("=" * 50)
    print("HEALTH CHECK TEST")
    print("=" * 50)
    
    endpoints = [
        "/health",
        "/chatbot/health",
        "/"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"\n{endpoint}:")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {response.json()}")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"{endpoint}: Error - {str(e)}")

def main():
    print("RAG API Test Client")
    print(f"Server: {BASE_URL}")
    
    while True:
        print("\n" + "=" * 40)
        print("Pilih test yang ingin dijalankan:")
        print("1. Health Check")
        print("2. Chatbot Test")
        print("3. Compliance Check Test")
        print("4. Exit")
        
        choice = input("\nPilihan (1/2/3/4): ")
        
        if choice == "1":
            test_health_check()
        elif choice == "2":
            test_chatbot()
        elif choice == "3":
            test_compliance()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Pilihan tidak valid!")

if __name__ == "__main__":
    main()
