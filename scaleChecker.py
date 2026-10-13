import re
import math

def check_display_scales(command: str, threshold: float = 40000.0):
    # Find all transformation arrays within the command string
    matches = re.findall(r'transformation:\s*\[([^\]]+)\]', command, re.IGNORECASE)
    
    if not matches:
        return []
    
    results = []
    
    # Loop through every transformation found in the command
    for i, values_str in enumerate(matches):
        values_list = values_str.split(',')
        
        if len(values_list) != 16:
            results.append({
                "model_index": i + 1, 
                "error": f"Expected 16 values, found {len(values_list)}."
            })
            continue
            
        try:
            # Clean and parse the floats
            values = [float(v.strip().replace('f', '').replace('F', '')) for v in values_list]
        except ValueError:
            results.append({
                "model_index": i + 1, 
                "error": "Failed to parse float values."
            })
            continue
        
        # Calculate the magnitude (length) of each column in the 3x3 transform part.
        # This isolates the true scale, completely ignoring rotation or shear.
        x_scale = math.sqrt(values[0]**2 + values[4]**2 + values[8]**2)
        y_scale = math.sqrt(values[1]**2 + values[5]**2 + values[9]**2)
        z_scale = math.sqrt(values[2]**2 + values[6]**2 + values[10]**2)
        
        scales = [round(x_scale, 2), round(y_scale, 2), round(z_scale, 2)]
        max_scale = max(scales)
        
        # Store the result for this specific nested model
        results.append({
            "model_index": i + 1,
            "x_scale": scales[0],
            "y_scale": scales[1],
            "z_scale": scales[2],
            "max_scale": max_scale,
            "exceeds_threshold": max_scale > threshold
        })
        
    return results

# ==========================================
# ---        SINGLE COMMAND HERE         ---
# ==========================================
cmd = ''

results = check_display_scales(cmd, threshold=1000.0)

# --- PRINT FULL RESULTS ---
print("--- ALL TRANSFORMS FOUND IN COMMAND ---")
if not results:
    print("No transformations found.")
else:
    for res in results:
        print(res)

# --- PRINT ONLY THE OFFENDERS ---
print("\n--- ⚠️ OFFENDING MODELS (Exceeds Threshold) ---")
offenders = [r for r in results if r.get('exceeds_threshold')]

if not offenders:
    print("✅ No models exceed the scale limit!")
else:
    for offender in offenders:
        print(f"❌ Model {offender['model_index']}: Max Scale = {offender['max_scale']} (X: {offender['x_scale']}, Y: {offender['y_scale']}, Z: {offender['z_scale']})")
