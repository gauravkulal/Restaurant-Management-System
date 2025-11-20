# Admin Menu Management Guide

## Overview
The admin menu management system allows you to dynamically add new categories and items to your restaurant menu. All changes are immediately visible to users.

## Features

### 1. Add New Category
- Navigate to Admin Dashboard → "Manage Menu"
- Fill in the "Add New Category" form:
  - **Category Name**: URL-safe name (lowercase, no spaces) - e.g., "desserts"
  - **Display Name**: Customer-facing name - e.g., "Desserts"
- Click "Create Category"
- The new category will appear in the "Our Menu" page immediately

### 2. Add New Item
- In the "Add New Item" section:
  - **Item Name**: Name of the dish - e.g., "Chocolate Cake"
  - **Price**: Price in rupees - e.g., 150.00
  - **Category**: Select from dropdown (includes your new categories)
  - **Description**: Optional description of the item
- Click "Add Item"
- Item appears in the menu immediately

### 3. Edit Existing Items
- Scroll to "All Menu Items" section
- Click "Edit" on any item
- Update name, price, category, or description
- Click "Update Item"
- Changes are live immediately

### 4. Delete Items
- Click "Delete" on any item in the "All Menu Items" section
- Confirm deletion
- Note: Items in order history cannot be deleted (data integrity)

## How It Works

### Dynamic Category Pages
- When you create a new category (e.g., "desserts"), a new page is automatically created
- The category appears in the "Our Menu" page with an item count
- Clicking the category shows all items in that category
- Full cart integration works automatically

### Real-Time Updates
- No server restart needed
- Changes reflect immediately for all users
- Database updates happen in real-time

## Database Schema

### Categories Table
```sql
- category_id (Primary Key)
- category_name (Unique, URL-safe)
- display_name (Customer-facing name)
- is_custom (TRUE for admin-created, FALSE for built-in)
- created_at (Timestamp)
```

### Items Table Updates
```sql
- Added: description (TEXT, optional)
- Existing: item_id, item_name, price, category
```

## Best Practices

1. **Category Names**: Use lowercase, no spaces (e.g., "chinese", "italian", "desserts")
2. **Display Names**: Capitalize properly (e.g., "Chinese", "Italian", "Desserts")
3. **Descriptions**: Keep concise but informative
4. **Pricing**: Use decimal format (e.g., 150.00, not 150)
5. **First Item**: Always add at least one item when creating a new category

## Access Control
- Only admin users (is_admin = TRUE) can access menu management
- Admin login: gaurav / 1234
- Regular users cannot see or access admin features

## Navigation Path
Home → Admin Dashboard → Manage Menu

## Example Workflow

### Adding "Italian Cuisine" Category:
1. Go to Manage Menu
2. Category Name: `italian`
3. Display Name: `Italian Cuisine`
4. Click "Create Category"

### Adding First Item:
1. Item Name: `Margherita Pizza`
2. Price: `299.00`
3. Category: Select "Italian Cuisine"
4. Description: `Classic Italian pizza with fresh mozzarella and basil`
5. Click "Add Item"

### Result:
- "Italian Cuisine" appears on "Our Menu" page
- Shows "1 delicious items to choose from"
- Clicking it shows the Margherita Pizza
- Users can add to cart normally

## Troubleshooting

**Category not appearing?**
- Refresh the page
- Check if category name is unique
- Ensure form was submitted successfully

**Item not showing?**
- Verify category was selected
- Check price is valid decimal
- Refresh the category page

**Can't delete item?**
- Item may exist in order history
- This is by design to maintain data integrity

## Technical Details

### Files Modified:
- `app.py` - Added routes for category/item CRUD
- `templates/admin_menu_management.html` - Management interface
- `templates/menu.html` - Dynamic category loading
- `templates/dynamic_category.html` - Template for new categories
- `update_menu_schema.sql` - Database schema updates

### API Endpoints:
- `/api/add-category` - Create new category
- `/api/add-item` - Create new item
- `/api/get-item/<id>` - Get item details
- `/api/update-item` - Update item
- `/api/delete-item` - Delete item
- `/category/<name>` - Dynamic category page

## Security
- All admin routes check `is_admin` flag
- SQL injection protection via parameterized queries
- Form validation on both frontend and backend
