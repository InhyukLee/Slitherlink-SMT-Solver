import os

def load_puzzles(data_dir="data/puzzle/sat", size=None, difficulty=None, puzzle_id=None):
    """
    Reads Slitherlink puzzle text files from the data directory and converts them
    into processable clue matrices, accounting for metadata and character spacing.
    """
    puzzles_dataset = {}
    
    if not os.path.exists(data_dir):
        print(f"Warning: Directory '{data_dir}' does not exist.")
        return puzzles_dataset

    files = [f for f in os.listdir(data_dir) if f.endswith('.txt')]
    
    for filename in files:
        parts = filename.replace('.txt', '').split('_')
        if len(parts) < 4:
            continue  
            
        f_size = parts[1]        
        f_difficulty = parts[2]  
        f_id = parts[3]          
        
        if size and f_size != size:
            continue
        if difficulty and f_difficulty != difficulty:
            continue
        if puzzle_id and str(f_id) != str(puzzle_id):
            continue
            
        file_path = os.path.join(data_dir, filename)
        
        try:
            clue_matrix = []
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            if not lines:
                continue
                
            # 1. FIX: Read and skip the first line metadata (e.g., "10 10")
            meta_line = lines[0].strip().split()
            if len(meta_line) == 2 and meta_line[0].isdigit():
                grid_cols = int(meta_line[1])  # Target width of the matrix (e.g., 10)
                grid_lines = lines[1:]         # The rest are the actual puzzle rows
            else:
                grid_cols = None
                grid_lines = lines             # Fallback if no meta header exists

            # 2. FIX: Parse character-by-character to preserve empty cells
            for line in grid_lines:
                # Remove newline characters but keep the leading/middle/trailing spaces intact!
                line = line.replace('\n', '').replace('\r', '')
                if not line.strip(): 
                    continue  # Skip truly empty lines
                
                row = []
                # Loop through the string by individual characters
                for char in line:
                    if char == ' ' or char == '.':
                        row.append(-1)  # Empty cell
                    elif char.isdigit():
                        row.append(int(char))  # Clue cell (0-3)
                
                # Sanity padding: If a line was cut short in the text file, pad it with empty cells
                if grid_cols and len(row) < grid_cols:
                    row.extend([-1] * (grid_cols - len(row)))
                # If it's too long, truncate it to match the metadata width
                elif grid_cols and len(row) > grid_cols:
                    row = row[:grid_cols]
                    
                clue_matrix.append(row)
            
            puzzles_dataset[filename] = clue_matrix
            
        except Exception as e:
            print(f"Error reading file {filename}. Details: {e}")
            
    return puzzles_dataset