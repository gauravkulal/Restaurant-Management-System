import re

# Fix veg.html - change IDs 1-50 to 51-100
with open('templates/veg.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace data-item-id and onclick addToCart for veg items
for old_id in range(50, 0, -1):  # Start from 50 to avoid conflicts
    new_id = old_id + 50
    # Replace data-item-id="X"
    content = content.replace(f'data-item-id="{old_id}"', f'data-item-id="{new_id}"')
    # Replace onclick="addToCart(X,
    content = re.sub(rf'onclick="addToCart\({old_id},', f'onclick="addToCart({new_id},', content)

with open('templates/veg.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Fixed veg.html - IDs now range from 51-100")

# Fix nonveg.html - change IDs 1-50 to 101-150
with open('templates/nonveg.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace data-item-id and onclick addToCart for nonveg items
for old_id in range(50, 0, -1):  # Start from 50 to avoid conflicts
    new_id = old_id + 100
    # Replace data-item-id="X"
    content = content.replace(f'data-item-id="{old_id}"', f'data-item-id="{new_id}"')
    # Replace onclick="addToCart(X,
    content = re.sub(rf'onclick="addToCart\({old_id},', f'onclick="addToCart({new_id},', content)

with open('templates/nonveg.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Fixed nonveg.html - IDs now range from 101-150")
print("\nAll done! Item IDs have been updated:")
print("  - Beverages: 1-25")
print("  - Snacks: 26-50")
print("  - Veg: 51-100")
print("  - Non-veg: 101-150")
