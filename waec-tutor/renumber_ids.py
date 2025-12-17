import json
#another comment
def renumber_json_ids(file_path):
    try:
        # 1. Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ Loaded {len(data)} questions.")

        # 2. Renumber sequentially
        # enumerate(data, 1) starts counting from 1
        for index, question in enumerate(data, 1):
            old_id = question.get('id', 'N/A')
            question['id'] = index
            # print(f"Renamed ID {old_id} -> {index}") # Uncomment to see details

        # 3. Save back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"🎉 Success! IDs are now sequential from 1 to {len(data)}.")

    except Exception as e:
        print(f"❌ Error: {e}")

# --- RUN IT ---
# Change 'data/waec_questions.json' to your actual file name
renumber_json_ids('data/waec_questions.json')
